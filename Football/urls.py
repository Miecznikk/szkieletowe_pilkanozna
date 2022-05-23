from django.urls import path
from django.contrib.auth import views as v
from .forms import UserLoginForm
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
    path('register/',views.sign_up,name='register'),
    path('login/',v.LoginView.as_view(template_name="registration/login.html",authentication_form=UserLoginForm),name = 'login'),
    path('profile/',views.profile,name='profile'),
    path('messages/',views.messages_view,name='messages')
]
