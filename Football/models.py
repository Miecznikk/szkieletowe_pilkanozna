from django.db import models
from django.db.models import Count
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator,MinValueValidator

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
        matches = Match.objects.filter(team1 = self) | Match.objects.filter(team2 = self)
        goals = [goal for goal in Goal.objects.all() if goal.match in matches]
        goals_lost = [goal for goal in goals if goal.team != self]
        return len(goals_lost)

    def get_absolute_url(self):
        return reverse('football:team_detail',args=[self.slug])

    def get_players_cunt(self):
        return len(Player.objects.filter(team_id=self.id))

    def get_balance(self)->int:
        pass

    def get_captain(self):
        player = Player.objects.filter(team=self,captain=True).first()
        return player


class Player(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,null=True)
    name = models.CharField(max_length=30)
    surname = models.CharField(max_length=30)
    position = models.ForeignKey(Position,on_delete=models.CASCADE,null=True)
    shirt_number = models.IntegerField(null=True, validators=[MinValueValidator(1),MaxValueValidator(99)])
    team = models.ForeignKey(Team,null=True,on_delete=models.SET_NULL)
    image = models.ImageField(upload_to='images/players/',null=False,default='images/default_profile_picture.jpg')
    captain = models.BooleanField(null=False,default=False)
    mod = models.BooleanField(null=False,default=False)

    def get_goals(self):
        goals = Goal.objects.all().filter(player = self)
        return goals

    def get_hat_tricks(self):
        goals = Goal.objects.all().filter(player = self)
        goals = goals.values('match').annotate(total = Count('player'))
        count = 0
        for i in goals:
            if i['total'] >= 3:
                count+=1
        return count

    def score(self,match,n_of_goals):
        for i in range(n_of_goals):
            Goal.objects.create(match=match,player=self,team=self.team)

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
    date = models.DateField(null=False)
    status = models.BooleanField(default=False, null=False)

    class Meta:
        verbose_name_plural = 'Matches'

    def __str__(self):
        return f'{self.team1.__str__()} - {self.team2.__str__()} {self.get_score()}'

    def get_score(self):
        goals1 = Goal.objects.filter(match=self,team=self.team1)
        goals2 = Goal.objects.filter(match=self,team=self.team2)
        return f'{len(goals1)} : {len(goals2)}'

    def get_winner(self):
        score = self.get_score().split(':')
        if score[0] > score[1]:
            return self.team1
        elif score[0] < score[1]:
            return self.team2
        else:
            return 'draw'

class Goal(models.Model):
    match = models.ForeignKey(Match,on_delete=models.CASCADE)
    player = models.CharField(max_length=100)
    team = models.ForeignKey(Team,on_delete=models.CASCADE)

    def __str__(self):
        return f'{str(self.player)} - {self.match}'


class Message(models.Model):
    sender = models.ForeignKey(Player,on_delete=models.CASCADE,related_name='sender')
    receiver = models.ForeignKey(Player,on_delete=models.CASCADE,related_name='receiver')
    description = models.TextField(max_length=500)

class Invite(Message):
    invited_team = models.ForeignKey(Team,on_delete=models.CASCADE)

class Challenge(Message):
    stadium = models.ForeignKey(Stadium,on_delete=models.CASCADE)
    date = models.DateField()
    challenged_team = models.ForeignKey(Team,on_delete=models.CASCADE,related_name='challenged_team')
    challenging_team = models.ForeignKey(Team,on_delete=models.CASCADE,related_name='challenging_team')

    def accept(self):
        Match.objects.create(stadium=self.stadium,date=self.date,team1=self.challenging_team,
                             team2 = self.challenged_team)


class MatchReport(Message):
    match = models.ForeignKey(Match,on_delete=models.CASCADE)