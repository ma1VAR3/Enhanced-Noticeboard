from django.shortcuts import render
from accounts.models import GroupMember,Group
from .models import Event,FAQ
from django.contrib.auth.decorators import login_required
from .forms import eventForm,questionForm
from django.urls import reverse
from django.http import HttpResponseRedirect

from .groupping import checkSemantics,load_pretrained,get_embeddings,formatOutput

import numpy as np
import tensorflow as tf
global graph,model
from tensorflow.python.framework.ops import disable_eager_execution


# Create your views here.
def Home(request):
    member_groups = []
    admin_groups = []
    if request.user.is_authenticated:
        member_groups = GroupMember.objects.filter(user=request.user)
        admin_groups = Group.objects.filter(admin=request.user.username)
    return render(request,'home.html',{'member_groups':member_groups,
                                       'admin_groups':admin_groups})

@login_required
def Eventform(request,slug):
    if request.method == 'POST':
        form = eventForm(data=request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.group = Group.objects.get(slug=slug)
            event.save()
            return HttpResponseRedirect(reverse('general:event',kwargs={"id":event.id}))
    else:
        form = eventForm()
    return render(request,'accounts/form.html',{'form':form})

@login_required
def EventUpdateform(request,id):
    event = Event.objects.get(id=id)
    if request.method == 'POST':
        form = eventForm(data=request.POST,instance=event)
        if form.is_valid():
            event.save()
            return HttpResponseRedirect(reverse('general:event',kwargs={"id":event.id}))
    else:
        form = eventForm(instance=event)
    return render(request,'accounts/form.html',{'form':form})

print("Keras model loading.......")
embed = get_embeddings()
model = load_pretrained(embed)
# embeddings = embeddings()
print("Model loaded!!")


@login_required
def Eventview(request,id):
    event = Event.objects.get(id=id)
    try:
        faqs = FAQ.objects.filter(event=event)
    except:
        faqs = []
    if request.method == 'POST':
        form = questionForm(data=request.POST)
        if form.is_valid():
            res = []
            faq = form.save(commit = False)
            question = form.cleaned_data['question']
            print("***************************")
            print(question)
            print("**************************************")
            for i in faqs:
                result, op_len= checkSemantics(question, i.question)
                print(result)
                tf.executing_eagerly()
                prediction = model.predict(result)
                prediction = formatOutput(prediction,op_len)
                print(prediction)
                if prediction == True:
                    res.append(i)
            print(res)
            faq.frequency += 1
            faq.event = event
            faq.user = request.user
            faq.save()
            return HttpResponseRedirect(reverse('general:event',kwargs={"id":event.id}))
    else:
        form = questionForm()
    return render(request, "general/eventview.html",{'event':event,'faqs':faqs,'form':form})





@login_required
def Eventdelete(request,id):
    event = Event.objects.get(id=id)
    group =event.group
    event.delete()
    return HttpResponseRedirect(reverse('accounts:group',kwargs={"slug":group.slug}))

@login_required
def AnswerFaq(request,id):
    faq = FAQ.objects.get(id=id)
    if request.method == 'POST':
        answer = request.POST.get('answer')
        faq.answer = answer
        faq.save()
        return HttpResponseRedirect(reverse('general:event',kwargs={"id":faq.event.id}))
    return render(request, "general/answerfaq.html",{'faq':faq})


print("Keras model loading.......")
embed = get_embeddings()
model = load_pretrained(embed)
# embeddings = embeddings()
print("Model loaded!!")

def predict(request,id):
    faq = FAQ.objects.get(id=id)
    if request.method == "POST":
        form = take_question(data = request.POST)
        if form.is_valid():
            question = form.cleaned_data['question']
            print("***************************")
            print(question)
            print("**************************************")
            from_database = FAQ.objects.values('question')
            for i in from_database:
                result = checkSemantics(question, i, model)
                tf.executing_eagerly()
                prediction = model.predict(result)
                print(prediction)
                if prediction == True:
                    res.append(i)
            print(res)
    else:
        form = take_question()
    return render(request,'model.html',{
    "form": form
    })
        # Add the frequency in the questions where the results are True
        #Add the user id in the question as well
        #Return a render to the page saying question sent successfully
