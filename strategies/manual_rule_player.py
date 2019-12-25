import random

from strategies.player import Player


class ManualRulePlayer(Player):
    """
    Completely random decision based strategy
    """

    def __init__(self, figure):
        super().__init__(figure)
        self.STRATEGY = "MANUAL"
        self.current_question = None

        self.unknown_figures = set()
        self.unknown_weapons = set()
        self.unknown_rooms = set()

        self.figure_cards = set()
        self.weapon_cards = set()
        self.room_cards = set()


    def game_play_starts(self):
        self.figure_cards = set((card for card in self.cards if card in self.game.figures))
        self.weapon_cards = set((card for card in self.cards if card in self.game.weapons))
        self.room_cards = set((card for card in self.cards if card in self.game.room_manager.rooms))

    def set_game_reference(self, game):
        """
        (Override)
        Attach a reference to the central game logic object
        Overriding this to use this to also initiate our knowledge repository

        :param game: central game logic
        :type game: Game
        """
        super().set_game_reference(game)

        # Init knowledge repository with existing game elements (figures, weapons and rooms)
        self.unknown_figures = set(game.figure_names)
        self.unknown_weapons = set(game.weapons)
        self.unknown_rooms = set(game.room_manager.rooms)

    def _note_seen_card(self, card):
        """
        Note that the given card was seen

        :param card: card that was shown
        :type card: str
        """
        # Add this card to knowledge repository (by removing it from set of unknown elements)
        if card in self.game.figure_names:
            self.unknown_figures.discard(card)
        elif card in self.game.weapons:
            self.unknown_weapons.discard(card)
        else:
            self.unknown_rooms.discard(card)

    def set_own_card(self, card):
        """
        (Override)
        Set the given card as an own card
        Overriding this to update knowledge repository

        :param card: card (figure, weapon or room)
        :type card: str
        """
        super().set_own_card(card)

        # Add card to knowledge repository
        self._note_seen_card(card)

    def next_room(self, possible_rooms):
        return random.choice(possible_rooms)

    def next_question(self):
        # Narrowed everything down to one option? Accuse
        if len(self.unknown_figures) == 1 and len(self.unknown_weapons) == 1 and len(self.unknown_rooms) == 1:
            self.current_question = (
                True,
                self.unknown_figures.pop(),
                self.unknown_weapons.pop(),
                self.unknown_rooms.pop()
            )
        # Not sure yet? Just ask
        else:
            # As we are the random player, we just ask randomly (at least only for cards we do not know yet).
            # Although there might be better ways :D

            # if self.figure.position in self.room_cards:
            #     if not self.figure_cards:
            #         if not self.weapon_cards:
            #             guess_figure = random.choice(list(self.unknown_figures))
            #             guess_weapon = random.choice(list(self.unknown_weapons))
            #         else:
            #             guess_weapon = random.choice(list(self.weapon_cards))
            #             guess_figure = random.choice(list(self.unknown_figures))
            #     elif not self.weapon_cards:
            #         guess_figure = random.choice(list(self.figure_cards))
            #         guess_weapon = random.choice(list(self.unknown_weapons))
            #     else:
            #         if random.getrandbits(1):
            #             guess_figure = random.choice(list(self.figure_cards))
            #             guess_weapon = random.choice(list(self.unknown_weapons))
            #         else:
            #             guess_weapon = random.choice(list(self.weapon_cards))
            #             guess_figure = random.choice(list(self.unknown_figures))
            # else:
            #     if not self.figure_cards:
            #         guess_figure = random.choice(list(self.unknown_figures))
            #     else:
            #         guess_figure = random.choice(list(self.figure_cards))
            #
            #     if not self.weapon_cards:
            #         guess_weapon = random.choice(list(self.unknown_weapons))
            #     else:
            #         guess_weapon = random.choice(list(self.weapon_cards))
            #
            # guess_room = self.figure.position
            #
            # self.current_question = (
            #     False,
            #     guess_figure,
            #     guess_weapon,
            #     guess_room)
            self.current_question = (
                    False,
                    random.choice(list(self.unknown_figures)),
                    random.choice(list(self.unknown_weapons)),
                    self.figure.position)
        return self.current_question

    def choose_card_to_show(self, questioned_cards):
        # Show random card if player has at least one of them

        possible_cards = [card for card in questioned_cards if card in self.cards]

        if len(possible_cards) == 0:
            return None
        else:
            return random.choice(possible_cards)

    def see_card(self, card, showing_player):
        # Note that the given card was seen (random player does not care who showed this card to them)
        self._note_seen_card(card)

    def see_no_card(self, showing_player):
        # Random player does not care about this information
        pass

    def see_no_card_from_nobody(self):
        if not self.current_question[1] in self.cards:
            self.unknown_figures = set([self.current_question[1]])
        if not self.current_question[2] in self.cards:
            self.unknown_weapons = set([self.current_question[2]])
        if not self.current_question[3] in self.cards:
            self.unknown_rooms = set([self.current_question[3]])
        #pass

    def observe_card_shown(self, showing_player, seeing_player, questioned_cards):
        # Random player does not care about this information
        pass

    def observe_no_card_shown(self, showing_player, seeing_player, questioned_cards):
        # Random player does not care about this information
        pass

    def observe_no_card_from_nobody(self, seeing_player, questioned_cards):
        # Random player does not care about this information
        pass
