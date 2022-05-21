from django.shortcuts import render,get_object_or_404,redirect
from .models import Team,Player,Position,Message,Invite
from .ext_methods import get_table,send_invite_to_team
from django.template.defaultfilters import slugify
from .forms import RegisterTeamForm,RegisterForm,UpdateProfileForm,InvitePlayer
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login,logout,authenticate



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
    if request.user.player.captain and request.user.player.team == team:
        if request.method == "POST":
            form = InvitePlayer(request.POST)
            if form.is_valid():
                invited_player = form.cleaned_data.get('invite')
                send_invite_to_team(f'Zostałeś zaproszony przez {request.user.player.__str__()} do drużyny '
                                    f'{team.__str__()}',invited_player,team)
                return redirect('football:home')
        else:
            form = InvitePlayer()
    else:
        form = None
    return render(request,'team_detail.html',{'team':team,'players':players,'form':form})

@login_required(login_url='/login')
def register_team(request):
    if request.method == "POST":
        form = RegisterTeamForm(request.POST,request.FILES)
        if form.is_valid():
            name = form.cleaned_data['name']
            form.instance.slug = slugify(name)
            team = form.save()
            player = Player.objects.filter(user = request.user)[0]
            player.team = team
            player.captain = True
            player.save()
            return redirect('football:home')
    else:
        if request.user.player.team is not None:
            err_msg = "Jesteś już w drużynie, opuść ją aby założyć własną"
            return render(request,'error.html',{'err':err_msg})
        form = RegisterTeamForm()
    return render(request,'register_team.html',{'form':form})

@login_required(login_url='/login')
def profile(request):
    if request.method=="POST":
        form = UpdateProfileForm(request.POST,request.FILES,instance=request.user.player)
        if form.is_valid():
            form.save()
            return redirect('football:home')
    else:
        form = UpdateProfileForm(instance = request.user.player)
    return render(request,'profile.html',{'form':form})

def player_detail(request,id):
    player = get_object_or_404(Player,id=id)
    return render(request,'player_detail.html',{'player':player})

@login_required(login_url='/login')
def messages_view(request):
    messages = Message.objects.filter(receiver=request.user.player,invite__isnull = True)
    invites = Message.objects.filter(receiver=request.user.player)
    if request.method == "POST":
        message_accept = request.POST.get("accept")
        message_decline = request.POST.get("decline")
        if message_decline is not None:
            message = get_object_or_404(Message,id = message_decline)
            message.delete()
        elif message_accept is not None:
            inv = get_object_or_404(Invite,id = message_accept)
            team = inv.invited_team
            request.user.player.team = team
            request.user.player.save()
            inv.delete()
            return redirect('football:team_detail',slug=team.slug)
    return render(request,'messages.html',{'messages':messages,'invites':invites})
# Create your views here.
