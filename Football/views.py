from django.shortcuts import render,get_object_or_404,redirect
from .models import Team,Player,get_table,Position
from django.template.defaultfilters import slugify
from .forms import RegisterTeamForm,RegisterForm
from django.http import HttpResponseRedirect
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

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

def get_teams(request):
    return {'teams' : Team.objects.all()}

def home_view(request):
    return render(request,'home.html',{})

def all_teams(request):
    context = {
        'teams' : Team.objects.all()
    }
    return render(request,'all_teams.html',context)

def table_view(request):
    context = {
        'table': get_table()
    }
    return render(request,'table.html',context)

def team_detail(request,slug):
    team = get_object_or_404(Team, slug=slug)
    players = Player.objects.filter(team_id=team.id)
    return render(request,'team_detail.html',{'team':team,'players':players})

def register_team(request):
    if request.method == "POST":
        form = RegisterTeamForm(request.POST,request.FILES)
        if form.is_valid():
            name = form.cleaned_data['name']
            form.instance.slug = slugify(name)
            form.save()
            HttpResponseRedirect('')
    else:
        form = RegisterTeamForm()
    return render(request,'register_team.html',{'form':form})


def player_detail(request,id):
    player = get_object_or_404(Player,id=id)
    return render(request,'player_detail.html',{'player':player})
# Create your views here.
