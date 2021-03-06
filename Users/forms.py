from django import forms
from Football.models import Player,Team
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth.models import User

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label='Nazwa użytkownika')
    password = forms.CharField(label ='Hasło',widget=forms.PasswordInput())

class RegisterForm(UserCreationForm):
    name = forms.CharField(max_length=30,required=True,label="Imię")
    surname = forms.CharField(max_length=30,required=True,label="Nazwisko")
    username = forms.CharField(max_length=30,required=True,label = "Nazwa użytkownika")
    password1 = forms.CharField(label='Hasło',strip=False,widget=forms.PasswordInput(),help_text='Podaj haslo')
    password2 = forms.CharField(label='Potwierdź hasło',strip=False,
                                widget=forms.PasswordInput(),help_text='Potwierdz hasło')
    position = forms.ChoiceField(label='Pozycja',
                                 choices=(('1','Obrona'),('2','Pomoc'),('3','Atak'),('4','Bramkarz')),required=True)

    class Meta:
        model = User
        fields = ["username","name","surname","password1","password2","position"]