from django import forms
from .models import Player,Team,Message
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.models import User

class SendMessage(forms.ModelForm):
    receiver = forms.ModelChoiceField(required=True,label='Odbiorca',
                                      queryset=Player.objects.filter(mod=False))

    def __init__(self,*args,**kwargs):
        self.user=kwargs.pop('user')
        super(SendMessage,self).__init__(*args,**kwargs)

    class Meta:
        model = Message
        fields = ['receiver','description']
        labels = {
            'description' : 'Treść'
        }

    def clean(self):
        cd = self.cleaned_data
        if self.user == cd.get('receiver'):
            raise forms.ValidationError('Nie możesz wysłać wiadomości do samego siebie!')
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