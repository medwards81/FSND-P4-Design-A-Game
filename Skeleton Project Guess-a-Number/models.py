"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb

class Hangman:
    DEFAULTS = {
        'guess_limit': 6,
        'points_per_hit': 2,
        'images': {
            'start': '//upload.wikimedia.org/wikipedia/commons/thumb'\
                   '/8/8b/Hangman-0.png/60px-Hangman-0.png' ,
            'guess-1': '//upload.wikimedia.org/wikipedia/commons/thumb'\
                   '/8/8b/Hangman-0.png/60px-Hangman-1.png' ,
            'guess-2': '//upload.wikimedia.org/wikipedia/commons/thumb'\
                   '/8/8b/Hangman-0.png/60px-Hangman-2.png' ,
            'guess-3': '//upload.wikimedia.org/wikipedia/commons/thumb'\
                   '/8/8b/Hangman-0.png/60px-Hangman-3.png' ,
            'guess-4': '//upload.wikimedia.org/wikipedia/commons/thumb'\
                   '/8/8b/Hangman-0.png/60px-Hangman-4.png' ,
            'guess-5': '//upload.wikimedia.org/wikipedia/commons/thumb'\
                   '/8/8b/Hangman-0.png/60px-Hangman-5.png' ,
            'guess-6': '//upload.wikimedia.org/wikipedia/commons/thumb'\
                   '/8/8b/Hangman-0.png/60px-Hangman-6.png' ,
        },
    }


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()


class UserRecord(ndb.Model):
    """User record object"""
    user = ndb.KeyProperty(required=True, kind='User')
    games = ndb.IntegerProperty(required=True, default=0)
    wins = ndb.IntegerProperty(required=True, default=0)
    losses = ndb.IntegerProperty(required=True, default=0)
    win_pct = ndb.FloatProperty(required=True, default=0.00)
    
    def to_form(self):
        return UserRecordForm(user_name=self.user.get().name,
                         games=self.games,
                         wins=self.wins,
                         losses=self.losses,
                         win_pct="{0:.3f}".format(self.win_pct))


class Game(ndb.Model):
    """Game object"""
    created = ndb.DateTimeProperty(auto_now_add=True)
    word = ndb.StringProperty(required=True)
    miss_count = ndb.IntegerProperty(default=0)
    match_count = ndb.IntegerProperty(default=0)
    guess_limit = ndb.IntegerProperty(default=Hangman.DEFAULTS['guess_limit'])
    hits = ndb.StringProperty(repeated=True)
    misses = ndb.StringProperty(repeated=True)
    image_uri = ndb.StringProperty(default=Hangman.DEFAULTS['images']['start'])
    game_over = ndb.BooleanProperty(required=True, default=False)
    user = ndb.KeyProperty(required=True, kind='User')
    cancelled = ndb.BooleanProperty(default=False)
    history = ndb.StringProperty(repeated=True)

    @classmethod
    def new_game(cls, user, word):
        """Creates and returns a new game"""
        word_upper = word.upper()
        game = Game(user=user,
                    word=word_upper,
                    game_over=False)
        game.put()
        return game

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.created = str(self.created)
        form.urlsafe_key = self.key.urlsafe()
        form.user_name = self.user.get().name
        form.word = self.word
        form.miss_count = self.miss_count
        form.match_count = self.match_count
        form.guess_limit = self.guess_limit
        form.hits = self.hits
        form.misses = self.misses
        form.image_uri = self.image_uri
        form.game_over = self.game_over
        form.message = message
        form.cancelled = self.cancelled
        return form
        
    def to_history_form(self):
        """Returns a GameHistoryForm"""
        form = GameHistoryForm()
        form.word = self.word
        form.history = self.history
        return form

    def end_game(self, won=False):
        """Ends the game - if won is True, the player won. - if won is False,
        the player lost."""
        self.game_over = True
        self.put()

        # Add the game to the score 'board'
        final_score = 0
        if won:
            final_score = len(self.hits) * Hangman.DEFAULTS['points_per_hit']
        score = Score(user=self.user, date=date.today(),
                        game=self.key, won=won, score=final_score)
        score.put()

        # Create and/or update the UserRecord
        user_record = UserRecord.query(UserRecord.user == self.user).get()
        if not user_record:
            user_record = UserRecord(user=self.user)
        if won:
            user_record.wins += 1
        else:
            user_record.losses += 1
        user_record.games += 1
        user_record.win_pct = round(int(user_record.wins) / int(user_record.games), 3)
        user_record.put()


class Score(ndb.Model):
    """Score object"""
    user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True)
    game = ndb.KeyProperty(required=True, kind='Game')
    won = ndb.BooleanProperty(required=True)
    score = ndb.IntegerProperty(required=True, default=0)

    def to_form(self):
        return ScoreForm(user_name=self.user.get().name, won=self.won,
                         date=str(self.date),
                         guess_limit=self.game.get().guess_limit,
                         miss_count=len(self.game.get().misses),
                         word_count=len(self.game.get().word),
                         score=self.score, word=self.game.get().word)


class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    word = messages.StringField(2, required=True)
    miss_count = messages.IntegerField(3)
    game_over = messages.BooleanField(4, required=True)
    message = messages.StringField(5, required=True)
    user_name = messages.StringField(6, required=True)
    created = messages.StringField(7, required=True)
    guesses = messages.IntegerField(8)
    hits = messages.StringField(9, repeated=True)
    misses = messages.StringField(10, repeated=True)
    image_uri = messages.StringField(11)
    guess_limit = messages.IntegerField(12)
    match_count = messages.IntegerField(13)
    cancelled = messages.BooleanField(14)


class GameForms(messages.Message):
    """Return multiple GameForms"""
    items = messages.MessageField(GameForm, 1, repeated=True)
    
    
class GameHistoryForm(messages.Message):
    """GameHistoryForm for outbound game state information"""
    word = messages.StringField(1, required=True)
    history = messages.StringField(2, repeated=True)


class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_name = messages.StringField(1, required=True)
    word = messages.StringField(2, required=True)


class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    guess = messages.StringField(1, required=True)


class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    user_name = messages.StringField(1, required=True)
    date = messages.StringField(2, required=True)
    won = messages.BooleanField(3, required=True)
    guess_limit = messages.IntegerField(4, required=True)
    miss_count = messages.IntegerField(5, required=True)
    word_count = messages.IntegerField(6, required=True)
    score = messages.IntegerField(7, required=True)
    word = messages.StringField(8, required=True)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)
    

class UserRecordForm(messages.Message):
    """UserRecordForm for outbound UserRecord information"""
    user_name = messages.StringField(1, required=True)
    games = messages.IntegerField(2, required=True)
    wins = messages.IntegerField(3, required=True)
    losses = messages.IntegerField(4, required=True)
    win_pct = messages.StringField(5, required=True)
    
 
class UserRecordForms(messages.Message):
    """Return multiple UserRecordForms"""
    items = messages.MessageField(UserRecordForm, 1, repeated=True)

    
class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)
