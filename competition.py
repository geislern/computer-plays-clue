import random

from game import Game
from strategies import RandomPlayer, CheatingRandomPlayer, ManualRulePlayer

COMPETITION_STRATEGIES = [RandomPlayer, CheatingRandomPlayer, ManualRulePlayer]
PLAYERS_PER_STRATEGY = 2
GAMES = 5000

if __name__ == "__main__":
    game = Game("config/classic_game_de.json")

    results_per_strategy = dict()
    strategies_for_players = COMPETITION_STRATEGIES * PLAYERS_PER_STRATEGY
    player_count = len(strategies_for_players)
    figures_for_players = random.sample(game.figures, player_count)

    for game_id in range(0, GAMES):
        # Generate players for all strategies
        strategy_figures_zip = zip(strategies_for_players, figures_for_players)
        players = [strategy(figure) for strategy, figure in strategy_figures_zip]
        game.set_players(players)

        winner, turn_count = game.play()
        print(f"\nGame over. {winner} wins after {turn_count} turns.")

        # Update winning count of strategy
        winning_strategy = winner.STRATEGY
        results_per_strategy[winning_strategy] = results_per_strategy.get(winning_strategy, 0) + 1

    print(f"\nFinal results after {GAMES} games:")
    print(results_per_strategy)
