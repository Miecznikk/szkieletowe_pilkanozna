from .models import Player,Team,Match,Invite
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

def top_scorers():
    def take_second(elem):
        return elem[1]
    players = Player.objects.all()
    players = sorted([[player,len(player.get_goals())] for player in players],key = take_second,reverse=True)
    return players

def get_table():
    teams = Team.objects.all()
    table_dict = {team : 0 for team in teams}
    matches = Match.objects.all()
    winners = [[match,match.get_winner()] for match in matches]

    def take_second(elem):
        return elem[1]

    for winner in winners:
        if winner[1]!='draw':
            table_dict[winner[1]] += 3
        elif winner[1] == 'draw':
            table_dict[winner[0].team1] +=1
            table_dict[winner[0].team2] +=1
    arr=[]

    for key in table_dict:
        arr.append([key,table_dict[key]])
    arr = sorted(arr,key=take_second)[::-1]
    arr = [f'{str(i[0])} - {str(i[1])}' for i in arr]
    return arr

@receiver(post_save,sender=User)
def update_user_profile(sender,instance,created,**kwargs):
    if created:
        Player.objects.create(user=instance)
    instance.player.save()

def get_teams(request):
    return {'teams' : Team.objects.all()}

def send_invite_to_team(description,send_from,send_to,invited_team):
    invite = Invite.objects.create(description=description,sender =send_from,receiver=send_to,invited_team=invited_team)