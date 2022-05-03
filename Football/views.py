from django.shortcuts import render,get_object_or_404,redirect
from .models import Team,Player,get_table
from .forms import PlayerForm
from django.http import HttpResponseRedirect

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
    if request.method == "POST":
        form = PlayerForm(request.POST,request.FILES)
        form.instance.team = team
        if form.is_valid():
            form.save()
            HttpResponseRedirect(f'teams/{slug}')
    else:
        form = PlayerForm()
    return render(request,'team_detail.html',{'team':team,'players':players,'form':form})

def player_detail(request,id):
    player = get_object_or_404(Player,id=id)
    return render(request,'player_detail.html',{'player':player})
# Create your views here.
