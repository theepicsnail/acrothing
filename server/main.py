
from google.appengine.api import users
from google.appengine.ext.webapp import template
import webapp2
from db import Game, Player
from os import path


def render(req, template_name, args):
    data = template.render(
        path.join(
            path.dirname(__file__),
            'templates',
            template_name),
        args)
    req.response.out.write(data)

class BaseHandler(webapp2.RequestHandler):
    def get(self, *args, **kwargs):
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
            return
        self.user = user
        return self.handle(*args, **kwargs)


class PlayNew(BaseHandler):
    def handle(self):
        self.redirect("/play/%s" % Game.create().gameId)

class PlayJoin(BaseHandler):
    def handle(self, gameId):
        print "PlayJoin %s" % gameId
        game = Game.byId(gameId)
        if game is None:
            self.response.out.write("Invalid game")
            return

        player = Player.byUser(self.user)

        # Player joining this game fresh
        if player is None:
            player = Player.joinGame(self.user, game)

        # Player was in another game, leave it.
        if player.game.gameId != game.gameId:
            player.leaveGame()
            player = Player.joinGame(self.user, game)

        render(self, 'play.html', {
            'me': player.user,
            'token': player.token,
            'game_key': player.game
        })

class PlayList(BaseHandler):
    def handle(self, gameId):
        player = Player.byUser(self.user)
        if player is None:
            self.response.out.write("")
            return

        game = Game.byId(gameId)
        out = [player.email for player in game.players]
        self.response.out.write(json.dumps(out))


class Chat(BaseHandler):
    def handle(self, gameId):
        player = Player.byUser(self.user)
        if player is None:
            self.response.out.write("")
            return

        game = Game.byId(gameId)
        msg = self.request.get('msg')
        game.broadcast({
            "sender": player.username,
            "message":msg})


app = webapp2.WSGIApplication([
    ('/play/?', PlayNew),
    ('/play/([A-Z]+)/list', PlayList),
    ('/play/([A-Z]+)/chat', Chat),
    ('/play/(.*)', PlayJoin),
], debug=True)
