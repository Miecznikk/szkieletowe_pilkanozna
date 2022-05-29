from django.shortcuts import render,get_object_or_404,redirect
from .models import Team,Player,Message,Invite,Challenge,Match,Goal
from .ext_methods import get_table,send_invite_to_team,top_scorers,matches_limit
from django.template.defaultfilters import slugify
from .forms import RegisterTeamForm,UpdateProfileForm,InvitePlayer,SendMessage,ChallengeForm
from django.contrib.auth.decorators import login_required,permission_required
from datetime import date
from django.contrib.auth.models import User,Group

captains_group = Group.objects.get(name='captains')

def home_view(request):
    table = top_scorers()
    recent_matches = sorted(Match.objects.filter(status=True),key=lambda x:x.date,reverse=True)[:5]
    return render(request,'home.html',{'table':table,'matches':recent_matches})

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
                deleted_player = get_object_or_404(Player,id=delete_player)
                deleted_player.team = None
                deleted_player.save()
                return redirect('football:team_detail',slug=team.slug)
            if promote_player is not None:
                promoting_player = get_object_or_404(Player, id=promote_player)
                promoting_player_user = get_object_or_404(User,player=promoting_player)
                promoting_player.captain=True
                request.user.player.captain=False
                captains_group.user_set.remove(request.user)
                captains_group.user_set.add(promoting_player_user)
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
            captains_group.user_set.add(request.user)
            captains_group.save()
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
            if matches_limit(challenge.challenging_team,challenge.challenged_team) or challenge.date < date.today():
                err_msg = 'Coś poszło nietak, być może wyzwanie wygasło'
                return render(request,'error.html',{'err':err_msg})
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
@permission_required('Football.add_challenge',login_url='/login')
def challenge_team(request,challenged_team=None):
    if request.method=="POST":
        form = ChallengeForm(request.POST,team = request.user.player.team)
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
        form = ChallengeForm(team=request.user.player.team,initial={'challenged_team':challenged_team})
    return render(request,'match/challenge.html',{'form':form})

@login_required(login_url='/login')
@permission_required('Football.add_goal',login_url='/login')
def post_score_view(request,id):
    match = Match.objects.filter(id=id).first()
    players1 = Player.objects.filter(team= match.team1)
    players2 = Player.objects.filter(team = match.team2)
    if request.user.player not in players1 and request.user.player not in players2:
        return redirect('football:home')
    if request.method=="POST" and not match.status and match.already_played():
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

def all_matches(request):
    finished_matches = sorted(Match.objects.filter(status=True),key=lambda x:x.date,reverse=True)
    upcoming_matches = sorted(Match.objects.filter(status=False),key=lambda x:x.date)
    return render(request,'match/all_matches.html',{
        'finished':finished_matches,
        'upcoming':upcoming_matches
    })

def match_detail(request,id):

    class Scorer:
        scorer = None
        count = 0

    match = Match.objects.filter(id=id).first()
    goals_scored = Goal.objects.filter(match=match)
    scorers = [goal.player for goal in goals_scored]
    ind_scorers = set(scorers)
    scorers_w_count = []
    for scorer in ind_scorers:
        swc = Scorer()
        swc.scorer=scorer
        swc.count = scorers.count(scorer)
        scorers_w_count.append(swc)
    return render(request,'match/match_detail.html',{
        'match':match,
        'scorers':sorted(scorers_w_count,reverse=True,key=lambda x:x.count),
    })