import random

from inout.parser import parse_game_config
from strategies import Player
from strategies import RandomPlayer
from strategies import CheatingRandomPlayer
from strategies import ManualRulePlayer


class Game:
    """
    Main class of the game
    """

    def __init__(self, config_file):
        """
        Constructor
        :param config_file: file containing the central game configuration
        :type config_file: str
        """
        self.room_manager, self.figure_names, self.figures, self.weapons = parse_game_config(config_file)

        # Prepare attributes
        self.crime_figure = ""
        self.crime_weapon = ""
        self.crime_scene = ""
        self.players: [Player] = []

    def set_players(self, players):
        """
        Attach a list of players

        :param players: list of players
        :type players: list[strategies.player.Player]
        """
        self.players = players

        # Attach this game to each player
        for player in self.players:
            player.set_game_reference(self)

    def play(self):
        """
        Main playing routine

        :return: winning Player, count of turns
        :rtype: logic.player.Player, int
        """
        # Init crime (choose weapon, crime scene and murderer)
        self.crime_weapon = random.choice(self.weapons)
        self.crime_figure = random.choice(self.figure_names)
        self.crime_scene = random.choice(self.room_manager.rooms)

        # Remaining weapons, figures and rooms will be given to the players
        cards = [w for w in self.weapons if w != self.crime_weapon]
        cards.extend(f for f in self.figure_names if f != self.crime_figure)
        cards.extend(r for r in self.room_manager.rooms if r != self.crime_scene)
        random.shuffle(cards)

        # Distribute cards to all players
        current_receiving_player = 0
        for card in cards:
            self.players[current_receiving_player].set_own_card(card)
            current_receiving_player = (current_receiving_player + 1) % len(self.players)

        print(f"Starting a game with {len(self.players)} Players: {', '.join(str(p) for p in self.players)}")
        # Real game starts now (callback)
        for player in self.players:
            player.game_play_starts()

        # Play actual game
        current_player_index = 0
        turn_count = 0
        active_players_remaining = len(self.players)
        while True:
            turn_count += 1
            # Get current player
            current_player : Player = self.players[current_player_index]

            # Player still active (did not make false accusations)
            if current_player.still_in_game:
                print(f"\nNext player is {current_player.figure.name}")

                # Roll dice
                dice_roll = random.randint(1, 6) + random.randint(1, 6)

                # Decide to which room to go
                possible_rooms = [room for (room, distance)
                                  in self.room_manager.get_reachables_for_room(current_player.figure.position)
                                  if distance <= dice_roll]
                next_room = current_player.next_room(possible_rooms)
                current_player.figure.move_to(next_room)

                # Decide which question to ask
                q_accuse, q_figure, q_weapon, q_room = current_player.next_question()

                # Accusing?
                if q_accuse:
                    print(f"Accusing! Was it {q_figure} with {q_weapon} in {q_room}?")

                    # Check accusation
                    if q_figure == self.crime_figure and q_weapon == self.crime_weapon and q_room == self.crime_scene:
                        # Correct?
                        print("Yes. Correct accusation")
                        return current_player, turn_count
                    else:
                        # Wrong? Player looses
                        print("No. This accusation was wrong")
                        current_player.still_in_game = False
                        active_players_remaining -= 1

                        # Last active player wins automatically
                        if active_players_remaining == 1:
                            print("Only one player left")
                            return [p for p in self.players if p.still_in_game][0], turn_count

                # Questioning?
                else:
                    print(f"Question: Was it {q_figure} with {q_weapon} in {q_room}?")
                    questioned_cards = [q_figure, q_weapon, q_room]

                    # Ask all players to show their cards until one showed one card or all players were asked
                    player_show_cards_index = current_player_index
                    while True:
                        player_show_cards_index = (player_show_cards_index + 1) % len(self.players)

                        # Player left that did not try to show a card yet
                        if player_show_cards_index != current_player_index:
                            questioned_player : Player = self.players[player_show_cards_index]
                            card_to_show = questioned_player.choose_card_to_show(questioned_cards)

                            # Is there a card to show?
                            if card_to_show is not None:
                                # Show card to asking player
                                current_player.see_card(card_to_show, questioned_player)

                                print(f"{questioned_player} showed a card")

                                # Other players observe that a card was shown (but not which card)
                                for other_player in self.players:
                                    if other_player != current_player and other_player != questioned_player:
                                        other_player.observe_card_shown(questioned_player, current_player, questioned_cards)

                                # Stop showing after one player showed a card
                                break

                            # Player cannot show a card
                            else:
                                # Player is informed that this player cannot show a card
                                current_player.see_no_card(questioned_player)

                                # Other players observe that no card was shown
                                for other_player in self.players:
                                    if other_player != current_player and other_player != questioned_player:
                                        other_player.observe_no_card_shown(questioned_player, current_player, questioned_cards)

                        # One complete round, nobody showed a card
                        else:
                            # Notify players
                            current_player.see_no_card_from_nobody()

                            print("Nobody showed a card")

                            # Other players observe that no card was shown
                            for other_player in self.players:
                                if other_player != current_player:
                                    other_player.observe_no_card_from_nobody(current_player, questioned_cards)

                            # Leave showing loop
                            break

            # Next player
            current_player_index = (current_player_index + 1) % len(self.players)


if __name__ == "__main__":
    game = Game("config/classic_game_de.json")

    # Generate 4 random players
    current_figures = random.sample(game.figures, 3)
    players = [RandomPlayer(current_figures[0]), CheatingRandomPlayer(current_figures[1]), ManualRulePlayer(current_figures[2])]
    game.set_players(players)

    winner, turn_count = game.play()
    print(f"\nGame over. {winner} wins after {turn_count} turns.")
