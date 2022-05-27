from django.urls import path
from django.contrib.auth import views as v
from . import views

app_name = 'football'

urlpatterns = [
    path('',views.home_view,name='home'),
    path('home/',views.home_view,name='home'),
    path('teams/',views.all_teams,name='all_teams'),
    path('player',views.all_players,name='all_players'),
    path('table/',views.table_view,name = 'table'),
    path('teams/<slug:slug>',views.team_detail,name='team_detail'),
    path('player/<int:id>',views.player_detail,name='player_detail'),
    path('register_team/',views.register_team,name='register_team'),
    path('profile/',views.profile,name='profile'),
    path('messages/',views.messages_view,name='messages'),
    path('messages/send',views.send_message_view,name='send_message'),
    path('messages/send/?P<int:receiver>',views.send_message_view,name='send_message'),
    path('teams/challenge/?P<int:challenged_team>',views.challenge_team,name='challenge'),
    path('match/?P<int:id>',views.post_score_view,name='post_score'),
    path('match/',views.team_matches,name='team_matches'),
]
