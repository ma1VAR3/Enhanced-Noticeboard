from django.shortcuts import render
from .forms import UserCreateForm,CreatGroupForm
from .models import Group,GroupMember
from general.models import Event
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import RedirectView
from django.shortcuts import get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
# Create your views here.
def Registration(request):
    if request.method == 'POST':
        form = UserCreateForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            return HttpResponseRedirect(reverse('accounts:login'))
    else:
        form = UserCreateForm()
    return render(request,'accounts/form.html',{'form':form})

@login_required
def CreateGroup(request):
    if request.method == 'POST':
        form = CreatGroupForm(data=request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.admin = request.user.username
            group.save()
            return HttpResponseRedirect(reverse('accounts:group',kwargs={"slug":group.slug}))
        else:
            print("Invalid")
    else:
        form = CreatGroupForm()

    return render(request, "accounts/form.html",{'form':form})

@login_required
def Groupview(request,slug):
    group = Group.objects.get(slug=slug)
    events = Event.objects.filter(group=group)
    current_site = get_current_site(request)
    return render(request, "accounts/groupview.html",{'group':group,
                                                      'current_site':current_site,
                                                      'events':events})

class JoinGroup(LoginRequiredMixin,RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        return reverse("accounts:group",kwargs={"slug":self.kwargs.get("slug")})

    def get(self, request, *args, **kwargs):
        group = get_object_or_404(Group,slug=self.kwargs.get("slug"))

        try:
            GroupMember.objects.create(user=self.request.user,group=group)
        except IntegrityError:
            return HttpResponse('User is already a member of the group')
        else:
            print("registered successfull")

        return super().get(request, *args, **kwargs)

class LeaveGroup(LoginRequiredMixin, RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        return reverse("home")

    def get(self, request, *args, **kwargs):
        try:
            membership = GroupMember.objects.filter(
                user = self.request.user,
                group__slug = self.kwargs.get("slug")

            ).get()

        except GroupMember.DoesNotExist:
            return HttpResponse('You are not a member')

        else:
            membership.delete()
            print("successfully deleted")

        return super().get(request, *args, **kwargs)
