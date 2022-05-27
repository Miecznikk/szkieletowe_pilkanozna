from django import forms
import datetime
from django.utils import timezone
from .models import Player,Team,Message,Challenge
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.models import User
from django.db.models import Q

class SendMessage(forms.ModelForm):
    receiver = forms.ModelChoiceField(required=True,label='Odbiorca',
                                      queryset=Player.objects.filter(mod=False))

    def __init__(self,*args,**kwargs):
        self.user = kwargs.pop('user')
        super(SendMessage,self).__init__(*args,**kwargs)
        self.fields['receiver'].queryset = Player.objects.filter(mod=False).exclude(id=self.user.id)

    class Meta:
        model = Message
        fields = ['receiver','description']
        labels = {
            'description' : 'Treść'
        }

    def clean(self):
        cd = self.cleaned_data
        if cd.get('receiver') == self.user:
            raise forms.ValidationError('Nie możesz wysłać wiadomości do siebie')
        return cd

class DateInput(forms.DateInput):
    input_type = 'date'

class ChallengeForm(forms.ModelForm):
    class Meta:
        model = Challenge
        fields=['stadium','date','challenged_team']
        labels ={
            'stadium': 'Biosko',
            'date': 'Data',
            'challenged_team': 'Drużyna'
        }
        widgets = {
            'date':DateInput(),
            }

    def clean(self):
        cd=self.cleaned_data
        if cd.get('date') <= datetime.date.today():
            raise forms.ValidationError('Pomiędzy dniem dzisiejszym a meczowym musi być co najmniej jeden dzień różnicy')
        return cd

class InvitePlayer(forms.Form):
    invite = forms.ModelChoiceField(label = 'Zaproś zawodnika do drużyny', required=False,
                                    queryset=Player.objects.filter(team=None,mod=False))

class UpdateProfileForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['name','surname','shirt_number','image']
        labels = {
            'name': 'Imię',
            'surname': 'Nazwisko',
            'shirt_number': 'Nr koszulki',
            'image': 'Zdjęcie profilowe'
        }


class RegisterTeamForm(forms.ModelForm):
    class Meta:
        model = Team
        exclude = ('slug',)
        labels = {
                'name': 'Nazwa drużyny',
                'image': 'Zdjęcie'
                }