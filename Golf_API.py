from google.appengine.ext import ndb
import webapp2
import json
import string

GET_ROUNDS=True

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
		p_dict['first_name'] = self.name.first
		p_dict['last_name'] = self.name.last
		p_dict['city'] = self.player_address.city
		p_dict['state'] = self.player_address.state
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
			self.response.write(json.dumps(player_key.get().player_to_dict(GET_ROUNDS)))
		except:
			self.abort(400)

	def get(self, id=None):
		if id:
			self.response.write(json.dumps(ndb.Key(urlsafe=id).get().player_to_dict(GET_ROUNDS)))
		else:
			players = Player.query().fetch()
			res = [p.player_to_dict(GET_ROUNDS) for p in players]	
			res2 = {}
			res2['players'] = res
			self.response.write(json.dumps(res2))

	def patch(self, id=None):
		if id:
			player = ndb.Key(urlsafe=id).get()
			changes = json.loads(self.request.body)
			if 'first_name' in changes:
				try:
					player.name.first = changes['first_name']
				except:
					self.abort(500)
			if 'last_name' in changes:
				try:
					player.name.last = changes['last_name']
				except:
					self.abort(500)
			if 'city' in changes:
				try:
					player.player_address.city = changes['city']
				except:
					self.abort(500)
			if 'state' in changes:
				try:
					player.player_address.state = changes['state']
				except:
					self.abort(500)
			player.put()
			self.response.set_status(200)
			self.response.write(json.dumps(ndb.Key(urlsafe=id).get().player_to_dict(GET_ROUNDS)))
		else:
			self.abort(400)

	def delete(self, id=None):
		if id:
			player = ndb.Key(urlsafe=id).get()
			for r in player.player_rounds:
				try:
					r.delete()
				except:
					self.abort(500)
			try:
				ndb.Key(urlsafe=id).delete()
			except:
				self.abort(500)
			self.response.set_status(200)
			self.response.write("Deleted Player and Associated Rounds.")
		else:
			self.abort(400)

class RoundHandler(webapp2.RequestHandler):
	def post(self, id=None):
		if id:
			try:
				player = ndb.Key(urlsafe=id).get()
				round_data = json.loads(self.request.body)
				round_key = Round(course_info=Course(name=round_data["course_name"], course_address=Address(city=round_data["course_city"], state=round_data["course_state"])), pars=round_data["pars"], scores=round_data["scores"]).put()
				newround = round_key.get()
				newround.id = round_key.urlsafe()
				newround.link = "player/" + id + "/round/" + round_key.urlsafe()
				newround.put()
				player.player_rounds.append(round_key)
				player.put()
				self.response.set_status(201)
				self.response.write(json.dumps(ndb.Key(urlsafe=id).get().player_to_dict(GET_ROUNDS)))
			except:
				self.abort(500)
		else:
			self.abort(400)

	def get(self, id=None):
		if id:
			try:
				self.response.write(json.dumps(ndb.Key(urlsafe=id).get().to_dict()))
			except:
				self.abort(500)
		else:
			self.abort(400)

	def patch(self, p_id=None, r_id=None):
		if p_id and r_id:
			editround = ndb.Key(urlsafe=r_id).get()
			changes = json.loads(self.request.body)
			if 'course_name' in changes:
				try:
					editround.course_info.name = changes['course_name']
				except:
					self.abort(500)
			if 'course_city' in changes:
				try:
					editround.course_info.course_address.city = changes['course_city']
				except:
					self.abort(500)
			if 'course_state' in changes:
				try:
					editround.course_info.course_address.state = changes['course_state']
				except:
					self.abort(500)
			if 'pars' in changes:
				try:
					editround.pars = changes['pars']
				except:
					self.abort(500)
			if 'scores' in changes:
				try:
					editround.score = changes['scores']
				except:
					self.abort(500)
			editround.put()
			self.response.set_status(200)
			self.response.write(json.dumps(ndb.Key(urlsafe=r_id).get().to_dict()))
		else:
			self.abort(400)

	def delete(self, p_id=None, r_id=None):
		if p_id and r_id:
			try:
				round_key = ndb.Key(urlsafe=r_id)
				player = ndb.Key(urlsafe=p_id).get()
				player.player_rounds.remove(round_key)
				player.put()
				round_key.delete()
			except:
				self.abort(500)
			self.response.set_status(200)
			self.response.write(str("Deleted Round"))
		else:
			self.abort(401)

allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods
app = webapp2.WSGIApplication([
	('/player', PlayerHandler),
	('/player/([\w-]+)', PlayerHandler),
	('/player/([\w-]+)/round', RoundHandler),
	('/player/([\w-]+)/round/([\w-]+)', RoundHandler),
	('/round/([\w-]+)', RoundHandler)
], debug=True)