# -*- coding: utf-8 -*-`
"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""


import logging
import endpoints
from protorpc import remote, messages
from google.appengine.api import memcache
from google.appengine.api import taskqueue

from models import User, Game, Score, Hangman
from models import StringMessage, NewGameForm, GameForm, MakeMoveForm,\
    ScoreForms
from utils import get_by_urlsafe

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(
        urlsafe_game_key=messages.StringField(1),)
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(
    MakeMoveForm,
    urlsafe_game_key=messages.StringField(1),)
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2))

MEMCACHE_MOVES_REMAINING = 'MOVES_REMAINING'

@endpoints.api(name='hangman', version='v1')
class HangmanApi(remote.Service):
    """Game API"""
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                    'A User with that name already exists!')
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(
                request.user_name))

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')

        word_stripped = request.word.strip()
        if not word_stripped:
            raise endpoints.BadRequestException("Hangman 'word' field required")

        word_list = word_stripped.split()
        if len(word_list) > 1:
            raise endpoints.BadRequestException("Hangman 'word' field must be a single word")

        game = Game.new_game(user.key, word_stripped)
        return game.to_form('Good luck playing Hangman!')


    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            return game.to_form('Time to make a guess!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Makes a move. Returns a game state with message"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game.game_over:
            return game.to_form('Game already over!')

        request_upper = request.guess.upper().strip()
        if not request_upper:
            raise endpoints.BadRequestException("Hangman 'guess' field required")

        if len(request_upper) > 1:
            raise endpoints.BadRequestException("Hangman 'guess' field must be 1 character")

        if request_upper in game.hits:
            raise endpoints.BadRequestException("You've already guessed '{0}'".format(request_upper))

        if request_upper in game.misses:
            raise endpoints.BadRequestException("You've already guessed '{0}'".format(request_upper))

        if request_upper in game.word:
            game.hits.append(request_upper)
            game.match_count += game.word.count(request_upper)
            msg = 'Hit!'
        else:
            game.misses.append(request_upper)
            miss_count = game.miss_count
            game.miss_count = miss_count + 1
            if miss_count < game.guess_limit:
                img_key = "guess-{0}".format(game.miss_count)
                game.image_uri = Hangman.images[img_key]
            msg = 'Miss!'

        if game.match_count == len(game.word):
            game.end_game(True)
            return game.to_form('You win!')

        if game.miss_count == game.guess_limit:
            game.end_game(False)
            return game.to_form(msg + ' Game over!')
        else:
            game.put()
            return game.to_form(msg)


api = endpoints.api_server([HangmanApi])
