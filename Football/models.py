from django.db import models
from django.db.models import Count
from django.urls import reverse
from django import forms

class Position(models.Model):
    title = models.CharField(max_length=30)

    def __str__(self):
        return self.title

class Team(models.Model):
    name = models.CharField(max_length=30)
    slug = models.SlugField(max_length=30,unique=True)
    image = models.ImageField(upload_to='images/teams')

    def __str__(self):
        return self.name

    def get_goals_scored(self):
        goals = Goal.objects.all().filter(player__team_id = self.id)
        return goals

    def get_goals_lost(self):
        matches = Match.objects.all().filter(team1=self)
        matches_ids = [match.id for match in matches]
        matches2 = Match.objects.all().filter(team2=self)
        matches2_ids = [match.id for match in matches2]
        goals = Goal.objects.all()
        goals_lost = [goal for goal in goals if goal.match_id in matches_ids]
        goals_lost2 = [goal for goal in goals if goal.match_id in matches2_ids]
        goals = goals_lost + goals_lost2
        goals = [goal for goal in goals if goal.player.team_id != self.id]
        return goals

    def get_absolute_url(self):
        return reverse('football:team_detail',args=[self.slug])

    def get_players_cunt(self):
        return len(Player.objects.filter(team_id=self.id))

    def get_balance(self)->int:
        return len(self.get_goals_scored()) - len(self.get_goals_lost())

class Player(models.Model):
    name = models.CharField(max_length=30)
    surname = models.CharField(max_length=30)
    position = models.ForeignKey(Position,on_delete=models.CASCADE)
    shirt_number = models.IntegerField()
    team = models.ForeignKey(Team,null=True,on_delete=models.SET_NULL)
    image = models.ImageField(upload_to='images/players/')


    def get_goals(self):
        goals = Goal.objects.all().filter(player = self)
        return goals

    def get_assists(self):
        assists = Asist.objects.all().filter(player = self)
        return assists

    def get_hat_tricks(self):
        goals = Goal.objects.all().filter(player = self)
        goals = goals.values('match').annotate(total = Count('player'))
        count = 0
        for i in goals:
            if i['total'] >= 3:
                count+=1
        return count

    def get_absolute_url(self):
        return reverse('football:player_detail',args=[self.id])

    def __str__(self):
        return f'{self.name} {self.surname}'

class Stadium(models.Model):
    name = models.CharField(max_length=30)
    place = models.CharField(max_length=30)

    def __str__(self):
        return f'{self.name} - {self.place}'

class Match(models.Model):
    team1 = models.ForeignKey(Team,related_name='teamone',on_delete=models.CASCADE)
    team2 = models.ForeignKey(Team,related_name='teamtwo',on_delete=models.CASCADE)
    stadium = models.ForeignKey(Stadium,null=True,on_delete=models.SET_NULL)
    date = models.DateTimeField()

    class Meta:
        verbose_name_plural = 'Matches'

    def get_score(self):
        all_goals = Goal.objects.all().filter(match=self.id)
        one_goals = all_goals.filter(player__team_id=self.team1)
        two_goals = all_goals.filter(player__team_id=self.team2)
        return f'{len(one_goals)} : {len(two_goals)}'

    def get_winner(self):
        all_goals = Goal.objects.filter(match = self.id)
        one_goals = len(all_goals.filter(player__team_id = self.team1))
        two_goals = len(all_goals.filter(player__team_id = self.team2))
        if one_goals>two_goals:
            return self.team1
        elif one_goals<two_goals:
            return self.team2
        else:
            return 'draw'

    def __str__(self):
        return f'{self.team1.__str__()} - {self.team2.__str__()} : {self.get_score()}'

class Goal(models.Model):
    match = models.ForeignKey(Match,on_delete=models.CASCADE)
    player = models.ForeignKey(Player,on_delete=models.CASCADE)

    def __str__(self):
        return f'{str(self.player)} - {self.match}'

class Asist(models.Model):
    goal = models.OneToOneField(Goal,on_delete=models.CASCADE)
    player = models.ForeignKey(Player,on_delete=models.CASCADE)


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
