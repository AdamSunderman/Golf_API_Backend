from google.appengine.ext import ndb
import webapp2
import json
import string

config = {
	
}

class ProperName(ndb.Model):
	first = ndb.StringProperty()
	last = ndb.StringProperty()

class Address(ndb.Model):
	city = ndb.StringProperty()
	state = ndb.StringProperty()

class Course(ndb.Model):
	name = ndb.StringProperty()
	course_address = ndb.StructuredProperty(Address)

class Round(ndb.Model):
	id = ndb.StringProperty()
	link = ndb.StringProperty()
	course_info = ndb.StructuredProperty(Course)
	scores = ndb.IntegerProperty(repeated=True)
	pars = ndb.IntegerProperty(repeated=True)
	
class Player(ndb.Model):
	id = ndb.StringProperty()
	link = ndb.StringProperty()
	name = ndb.StructuredProperty(ProperName)
	player_address = ndb.StructuredProperty(Address)
	player_rounds = ndb.KeyProperty(kind=Round, repeated=True)
	def player_to_dict(self, get_rounds):
		p_dict = {}
		p_dict['id'] = self.id
		p_dict['link'] = self.link
		p_dict['name'] = self.name.first + ", " + self.name.last
		p_dict['address'] = self.player_address.city + ", " self.player_address.state
		if get_rounds:
			p_dict['rounds'] = [Round.query(Round.key == key).get().to_dict() for key in self.player_rounds]
			return p_dict
		else:
			return p_dict

class PlayerHandler(webapp2.RequestHandler):
	def post(self):
		try:
			player_parent_key = ndb.Key(Player, "parent_player")
			player_data = json.loads(self.request.body)
			player_key = Player( name=ProperName(first=player_data['first_name'], last=player_data['last_name']), player_address=Address(city=player_data['city'], state=player_data['state']), parent=player_parent_key).put()
			player = player_key.get()
			player.id = player_key.urlsafe()
			player.link = "/player/" + player_key.urlsafe()
			player.put()
			self.response.set_status(201)
			self.response.write(json.dumps(player_key.get().to_dict()))
		except:
			self.abort(400)

	def get(self, id=None):
		if id:
			self.response.write(json.dumps(ndb.Key(urlsafe=id).get().custom_to_dict(True)))
		else:
			players = Player.query().fetch()
			res = []
			for p in players:
				res.append(p.custom_to_dict(True))
			res2 = {}
			res2['players'] = res
			self.response.write(json.dumps(res2))

	def patch(self, emp_id=None):
		if emp_id:
			self.response.write(json.dumps(t))

	def delete(self, id=None):
		if id:
			delete_player = ndb.Key(urlsafe=id).get().to_dict()
			delete_rounds = delete_player['player_rounds']
			for r in delete_rounds:
				r.delete()
			self.response.set_status(200)
			ndb.Key(urlsafe=id).delete()
		else:
			self.abort(401)

class RoundHandler(webapp2.RequestHandler):
	def post(self, id=None):
		if id:
			
		else:
			self.abort(400)

	def patch(self, job_id=None):
		if job_id:

	def delete(self, id=None):
		if id:
			ndb.Key(urlsafe=id).delete()	
		else:
			self.abort(401)


allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods
app = webapp2.WSGIApplication([
	('/player', PlayerHandler),
	('/player/([\w-]+)/round/([\w-]+)', RoundHandler),
	('/player/([\w-]+)/round', RoundHandler),
	('/round/([\w-]+)', PlayerHandler),
	('/player/round', PlayerHandler)
], debug=True)