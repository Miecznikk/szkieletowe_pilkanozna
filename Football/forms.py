from django import forms
import datetime
from .models import Player,Team,Message,Challenge
from .ext_methods import matches_limit

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
    def __init__(self,*args,**kwargs):
        self.team = kwargs.pop('team')
        super(ChallengeForm,self).__init__(*args,**kwargs)

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
            raise forms.ValidationError('Pomiędzy dniem dzisiejszym a meczowym musi '
                                        'być co najmniej jeden dzień różnicy')
        if matches_limit(self.team,cd.get('challenged_team')):
            raise forms.ValidationError('Rozegrałeś już 2 mecze z tą drużyną!')
        if cd.get('challenged_team') == self.team:
            raise forms.ValidationError('Nie możesz rzucić wyzwania samemu sobie!')
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