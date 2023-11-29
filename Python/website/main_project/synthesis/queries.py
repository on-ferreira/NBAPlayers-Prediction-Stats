from .models import GameStatistics, Player, Team, Game


def get_last_X_games(player_name, number_of_games):
    """
    Retrieve the last 10 games for a given player.

    Args:
    - player_name (str): The name of the player.

    Returns:
    - QuerySet: QuerySet of GameStatistics objects representing the last 10 games for the player.
    """

    player_id = Player.objects.get(name=player_name).id

    player_statistics = GameStatistics.objects.filter(player_id=player_id)

    last_10_games = player_statistics.order_by('-game__date')[:number_of_games]

    return last_10_games


def get_last_10_games_vs_opponent(player_name, opp_abbreviation):
    """
    Retrieve the last 10 games for a given player against a specific opponent.

    Args:
    - player_name (str): The name of the player.
    - opp_abbreviation (str): The abbreviation of the opponent team.

    Returns:
    - QuerySet: QuerySet of GameStatistics objects representing the last 10 games for the player against the specified opponent.
    """
    player_id = Player.objects.get(name=player_name).id

    opponent_team = Team.objects.get(abbreviation=opp_abbreviation)

    player_statistics_vs_opponent = GameStatistics.objects.filter(
        player_id=player_id,
        opp=opponent_team,
    ).order_by('-game__date')[:10]

    return player_statistics_vs_opponent
