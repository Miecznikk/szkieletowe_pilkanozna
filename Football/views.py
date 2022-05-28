from django.shortcuts import render,get_object_or_404,redirect
from .models import Team,Player,Position,Message,Invite,Challenge,Match
from .ext_methods import get_table,send_invite_to_team,top_scorers
from django.template.defaultfilters import slugify
from .forms import RegisterTeamForm,UpdateProfileForm,InvitePlayer,SendMessage,ChallengeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login,logout,authenticate


def home_view(request):
    table = top_scorers()
    return render(request,'home.html',{'table':table})

def all_teams(request):
    context = {
        'teams' : Team.objects.all()
    }
    return render(request, 'team/all_teams.html', context)

def all_players(request):
    context = {
        'players' : Player.objects.filter(mod=False)
    }
    if request.method=="POST":
        name,surname = request.POST.get('zawodnik').split()
        player = Player.objects.filter(name=name,surname=surname)
        if player:
            if len(player)>1:
                context = {
                    'players':player
                }
            elif len(player)==1:
                return redirect('football:player_detail',id=player[0].id)
    return render(request, 'player/all_players.html', context)

def table_view(request):
    context = {
        'table': get_table()
    }
    return render(request,'table.html',context)

def team_detail(request,slug):
    team = get_object_or_404(Team, slug=slug)
    players = Player.objects.filter(team_id=team.id)
    if request.user.player.team == team and not request.user.player.captain:
        if request.method == "POST":
            leave_team = request.POST.get('leave_team')
            if leave_team is not None:
                request.user.player.team = None
                request.user.player.save()
                return redirect('football:home')
    if request.user.player.captain and request.user.player.team == team:
        if request.method == "POST":
            delete_player = request.POST.get('delete_from_team')
            promote_player = request.POST.get('promote')
            if delete_player is not None:
                form = None
                deleted_player = get_object_or_404(Player,id=delete_player)
                deleted_player.team = None
                deleted_player.save()
                return redirect('football:team_detail',slug=team.slug)
            if promote_player is not None:
                form = None
                promoting_player = get_object_or_404(Player, id=promote_player)
                promoting_player.captain=True
                request.user.player.captain=False
                promoting_player.save()
                request.user.player.save()
                return redirect('football:team_detail',slug=team.slug)
            else:
                form = InvitePlayer(request.POST)
                if form.is_valid():
                    invited_player = form.cleaned_data.get('invite')
                    send_invite_to_team(f'Zostałeś zaproszony przez {request.user.player.__str__()} do drużyny '
                                        f'{team.__str__()}',request.user.player,invited_player,team)
                    return redirect('football:team_detail',slug=team.slug)
        else:
            form = InvitePlayer()
    else:
        form = None
    return render(request, 'team/team_detail.html', {'team':team, 'players':players, 'form':form})

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
    return render(request, 'team/register_team.html', {'form':form})

@login_required(login_url='/login')
def profile(request):
    if request.method=="POST":
        form = UpdateProfileForm(request.POST,request.FILES,instance=request.user.player)
        if form.is_valid():
            form.save()
            return redirect('football:home')
    else:
        form = UpdateProfileForm(instance = request.user.player)
    return render(request, 'player/profile.html', {'form':form})

def player_detail(request,id):
    player = get_object_or_404(Player,id=id)
    if request.method=="POST":
        send_invite_to_team(f'Zostałeś zaproszony przez {request.user.player.__str__()} do drużyny'
                            f'{request.user.player.team.__str__()}',request.user.player,player,request.user.player.team)
        return redirect('football:all_players')
    return render(request, 'player/player_detail.html', {'player':player})

@login_required(login_url='/login')
def messages_view(request):
    messages = Message.objects.filter(receiver=request.user.player,invite__isnull = True,challenge__isnull=True)
    challenges = Challenge.objects.filter(receiver=request.user.player)
    invites = Invite.objects.filter(receiver=request.user.player)
    if request.method == "POST":
        message_accept = request.POST.get("accept")
        message_decline = request.POST.get("decline")
        challenge_accept = request.POST.get("challenge")
        if message_decline is not None:
            message = get_object_or_404(Message,id = message_decline)
            message.delete()
        elif message_accept is not None:
            inv = get_object_or_404(Invite,id = message_accept)
            team = inv.invited_team
            if request.user.player.team is None:
                request.user.player.team = team
                request.user.player.save()
                inv.delete()
            else:
                err_msg = 'Jesteś już w drużynie, opuść ją aby dołączyć do innej'
                return render(request,'error.html',{'err':err_msg})
            return redirect('football:team_detail',slug=team.slug)
        elif challenge_accept is not None:
            challenge = Challenge.objects.filter(id=challenge_accept).first()
            challenge.accept()
            challenge.delete()
            return redirect('football:messages')
    return render(request, 'messages/messages.html', {'messages':messages, 'invites':invites,'challenges':challenges})

@login_required(login_url='/login')
def send_message_view(request,receiver = None):
    if request.method == "POST":
        form = SendMessage(request.POST,user=request.user.player)
        if form.is_valid():
            form.instance.sender = request.user.player
            form.save()
            return redirect('football:messages')
    else:
        form = SendMessage(user=request.user.player,initial={'receiver':receiver,'sender':request.user.player})
    return render(request,'messages/send_message.html',{'form':form})

@login_required(login_url='/login')
def challenge_team(request,challenged_team):
    if request.method=="POST":
        form = ChallengeForm(request.POST)
        if form.is_valid():
            form.instance.sender = request.user.player
            form.instance.challenging_team = request.user.player.team

            cd = form.cleaned_data
            team = cd.get('challenged_team')
            form.instance.receiver = team.get_captain()
            form.instance.description = f'Rzucono ci wyzwanie od drużyny {request.user.player.team} w dniu' \
                                        f' {cd.get("date")} na boisku {cd.get("stadium")}'
            form.save()
            return redirect('football:team_detail',slug=request.user.player.team.slug)
    else:
        form = ChallengeForm(initial={'challenged_team':challenged_team})
    return render(request,'match/challenge.html',{'form':form})

@login_required(login_url='/login')
def post_score_view(request,id):
    match = Match.objects.filter(id=id).first()
    players1 = Player.objects.filter(team= match.team1)
    players2 = Player.objects.filter(team = match.team2)

    if request.method=="POST" and not match.status:
        for player in players1 | players2:
            n_of_goals=int(request.POST.get(str(player.id)))
            if n_of_goals>0:
                player.score(match,n_of_goals)
        match.status = True
        match.save()
        sender = request.user.player
        receiver=None
        if sender.team == match.team1:
            receiver = match.team2.get_captain()
        elif sender.team == match.team2:
            receiver = match.team1.get_captain()
        Message.objects.create(sender=sender,receiver=receiver,
                               description=f'Kapitan drużyny przeciwnej wprowadził wynik meczu {match}'
                                           f', jeśli nie zgadzasz się z wprowadzonym wynikiem skontaktuj się '
                                           f'z administratorem Diabelskich rozgrywek')
        return redirect('football:team_matches')

    context = {
        'match':match,
        'players1':players1,
        'players2':players2,
    }
    return render(request,'match/post_score.html',context)

@login_required(login_url='/login')
def team_matches(request):
    my_matches = Match.objects.filter(team1 = request.user.player.team) \
                 | Match.objects.filter(team2 = request.user.player.team)
    return render(request,'match/team_matches.html',{'matches':my_matches})