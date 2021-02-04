from django.forms import ModelForm
from .models import Event,FAQ

class eventForm(ModelForm):
    class Meta:
        fields = ('title','description','start_time','end_time')
        model = Event

class questionForm(ModelForm):
    class Meta:
        fields = ('question',)
        model = FAQ
