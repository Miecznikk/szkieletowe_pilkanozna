from .models import Player,Team,Match,Invite

def top_scorers():
    class table_row:
        team=None
        player=None
        scored=0

    table=[]
    players=Player.objects.filter(mod=False)
    for player in players:
        tr=table_row()
        tr.player=player
        tr.team=player.team
        tr.scored=player.get_goals()
        table.append(tr)
    return sorted(table,reverse=True,key=lambda x:x.scored)[:5]

def get_table():

    class table_row:
        team = None
        matches = 0
        scored = 0
        lost = 0
        balance = 0
        points = 0
        wins = 0
        draws = 0
        loses = 0

    teams = Team.objects.filter()
    rows = []
    for team in teams:
        tr = table_row()
        tr.team = team
        matches = Match.objects.filter(status=True,team1=team) | Match.objects.filter(status=True,team2=team)
        tr.matches = len(matches)
        for match in matches:
            if match.get_winner() == team:
                tr.points+=3
                tr.wins+=1
            elif match.get_winner() == 'draw':
                tr.points+=1
                tr.draws+=1
            else:
                tr.loses+=1
        tr.scored = team.get_goals_scored()
        tr.lost = team.get_goals_lost()
        tr.balance = team.get_balance()
        rows.append(tr)
    return sorted(rows,key=lambda x:(x.points,x.balance),reverse=True)

def matches_limit(team1,team2):
    query = Match.objects.filter(team1=team1,team2=team2) | Match.objects.filter(team1=team2,team2=team1)
    return len(query) >= 2

def get_teams(request):
    return {'teams' : Team.objects.all()}

def send_invite_to_team(description,send_from,send_to,invited_team):
    invite = Invite.objects.create(description=description,sender =send_from,receiver=send_to,invited_team=invited_team)