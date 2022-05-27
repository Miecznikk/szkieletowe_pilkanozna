from django.contrib import admin
from .models import Position,Player,Team,Stadium,Match,Goal,Message,Invite,Challenge

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['title']

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['name','surname','position','team','mod']
    list_filter = ['team','surname','position']

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name']
    prepopulated_fields = {'slug':('name',)}

@admin.register(Stadium)
class StadiumAdmin(admin.ModelAdmin):
    list_display = ['name','place']

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ['player','match']

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['team1','team2','date','status']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['receiver','description']

@admin.register(Invite)
class InviteAdmin(admin.ModelAdmin):
    list_display = ['invited_team']

@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ['challenging_team','challenged_team']
# Register your models here.
