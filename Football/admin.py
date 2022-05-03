from django.contrib import admin
from .models import Position,Player,Team,Stadium,Match,Goal,Asist

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['title']

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['name','surname','position','team']
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

@admin.register(Asist)
class AsistAdmin(admin.ModelAdmin):
    list_display = ['player']

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['team1','team2','date']
# Register your models here.
