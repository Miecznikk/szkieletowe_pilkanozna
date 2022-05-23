from .forms import RegisterForm
from Football.models import Position,Player
from django.contrib.auth.models import User
from django.contrib.auth import login,logout,authenticate
from django.shortcuts import render,get_object_or_404,redirect
from django.db.models.signals import post_save
from django.dispatch import receiver


def sign_up(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.player.name=form.cleaned_data.get('name')
            user.player.surname=form.cleaned_data.get('surname')
            position = Position.objects.filter(id=form.cleaned_data.get('position'))[0]
            user.player.position = position
            login(request,user)
            return redirect('/home')
    else:
        form = RegisterForm()

    return render(request,'registration/sign_up.html',{'form':form})

@receiver(post_save,sender=User)
def update_user_profile(sender,instance,created,**kwargs):
    if created:
        Player.objects.create(user=instance)
    instance.player.save()
# Create your views here.
