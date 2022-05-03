from django.urls import path
from . import views

app_name = 'football'

urlpatterns = [
    path('',views.home_view,name='home'),
    path('teams/',views.all_teams,name='all_teams'),
    path('table/',views.table_view,name = 'table'),
    path('teams/<slug:slug>',views.team_detail,name='team_detail'),
    path('player/<int:id>',views.player_detail,name='player_detail'),
]
