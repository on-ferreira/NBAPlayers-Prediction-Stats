from django.urls import path
from .views import last_10_games_vs_opponent_view, last_X_games_view

urlpatterns = [
    path('last_10_games_vs_opponent/<str:player_name>/<str:opp_abbreviation>/', last_10_games_vs_opponent_view,
         name='last_10_games_vs_opponent'),
    path('last_10_games_vs_opponent/<str:player_name>/<int:number_of_games>/', last_X_games_view,
         name='last_X_games'),
]
