from django.shortcuts import render
from .queries import get_last_X_games,get_last_10_games_vs_opponent
from django.http import HttpResponse


def last_X_games_view(request, player_name, number_of_games):
    last_X_games = get_last_X_games(player_name, number_of_games)

    response_text = f"Last {number_of_games} Games of {player_name}:\n"

    for game_statistic in last_X_games:
        response_text += f"{str(game_statistic)}\n"

    return HttpResponse(response_text)


def last_10_games_vs_opponent_view(request, player_name, opp_abbreviation):
    last_10_games_vs_opponent = get_last_10_games_vs_opponent(player_name, opp_abbreviation)

    response_text = "Last 10 Games vs Opponent:\n"

    for game_statistic in last_10_games_vs_opponent:
        response_text += f"{game_statistic.game} - {game_statistic.player} - {game_statistic.opp}\n"

    return HttpResponse(response_text)
