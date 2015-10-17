from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import channel
import random
import json
import string

def genId(gameIdLength):
    return ''.join([random.choice(string.uppercase) for _ in range(gameIdLength)])

class Round(db.Model):
    timeLimit = db.IntegerProperty(required=True)
    letters = db.StringProperty(required=True)

class Game(db.Model):
    """ A game consists of a set of rounds.
    Before and after each round there's a small chat session.
    """
    gameId = db.StringProperty(required=True)
    # players = list(Player)

    @staticmethod
    def create():
        for i in range(4,10):
            gid = genId(i)
            if Game.byId(gid):
                continue
            g = Game(gameId = gid)
            g.put()
            # For some reason this forces the object to propigate.
            Game.get(g.key())
            return g
        print "Failed to create game!"
        return None

    @staticmethod
    def byId(gameId):
        q = Game.all()
        q.filter('gameId =', gameId)
        return q.get()

    def playerLeft(self, player):
        self.broadcast({
            "sender": "<<",
            "message": "User [%s] has left." % player.username})

    def playerJoined(self, player):
        self.broadcast({
            "sender": ">>",
            "message": "User [%s] has joined." % player.username})

    def broadcast(self, message):
        for player in self.players:
            player.send(message)

# A player in a game.
class Player(db.Model):
    user = db.UserProperty(required=True)
    token = db.StringProperty(required=True)
    game = db.ReferenceProperty(reference_class=Game,
            collection_name='players', required=True)

    @property
    def username(self):
        return self.email.split("@")[0]

    @property
    def email(self):
        return self.user.email()

    def send(self, data):
        channel.send_message(self.token, json.dumps(data))

    def leaveGame(self):
        self.game.playerLeft(self)
        self.delete()

    @staticmethod
    def joinGame(user, game):
        token = channel.create_channel("%s_%s" % (
            user.user_id(), game.gameId))
        p = Player(user = user, token=token, game=game)
        p.put()
        game.playerJoined(p)
        return p

    @staticmethod
    def byUser(user):
        return Player.all().filter('user =', user).get()
