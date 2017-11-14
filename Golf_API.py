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

class Round(ndb.Model):
	id = ndb.StringProperty()
	link = ndb.StringProperty()
	name = ndb.StringProperty()
	course_address = ndb.StructuredProperty(Address)
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
			employees = Employee.query().fetch()
			res = []
			for emps in employees:
				res.append(emps.custom_to_dict(False))
			res2 = {}
			res2['employees'] = res
			self.response.write(json.dumps(res2))

	def patch(self, emp_id=None):
		if emp_id:
			emp = ndb.Key(urlsafe=emp_id).get()
			req_data = json.loads(self.request.body)
			if 'name' in req_data:
				emp.name = req_data['name']
			if 'contact_number' in req_data:
				job.contact_number = req_data['contact_number']
			if 'position' in req_data:
				job.position = req_data['position']
			if 'wage' in req_data:
				job.wage = req_data['wage']
			t = {}
			t['name'] = emp.name
			t['id'] = emp.id
			t['contact_number'] = emp.contact_number
			t['position'] = emp.position
			t['wage'] = emp.wage
			t['link'] = emp.link
			emp.put()
			self.response.set_status(201)
			self.response.write(json.dumps(t))

	def delete(self, id=None):
		if id:
			delete_emp = ndb.Key(urlsafe=id).get().to_dict()
			de_jobs = delete_emp['jobs']
			for de in de_jobs:
				de.delete()
			ndb.Key(urlsafe=id).delete()
		else:
			self.abort(401)

class RoundHandler(webapp2.RequestHandler):
	def post(self, id=None):
		if id:
			emp_key = ndb.Key(urlsafe=id)
			emp = emp_key.get()
			rq_data = json.loads(self.request.body)
			job_key = Job(name=rq_data['name'], start_date=rq_data['start_date'], end_date=rq_data['end_date'], location=rq_data['location'], job_type=rq_data['job_type']).put()
			job = job_key.get()
			job.id = job_key.urlsafe()
			job.link = str("/employee/job/" + job.id)
			job.put()
			emp.jobs.append(job_key)
			emp.put()
			self.response.set_status(201)
			self.response.write(json.dumps(job_key.get().to_dict()))
		else:
			self.abort(400)

	def patch(self, job_id=None):
		if job_id:
			#emp = ndb.Key(urlsafe=emp_id).get().to_dict()
			job = ndb.Key(urlsafe=job_id).get()
			req_data = json.loads(self.request.body)
			if 'name' in req_data:
				job.name = req_data['name']
			if 'start_date' in req_data:
				job.start_date = req_data['start_date']
			if 'end_date' in req_data:
				job.end_date = req_data['end_date']
			if 'job_type' in req_data:
				job.job_type = req_data['job_type']
			if 'location' in req_data:
				job.location = req_data['location']
			job.put()
			self.response.set_status(201)
			self.response.write(json.dumps(ndb.Key(urlsafe=job_id).get().to_dict()))

	def delete(self, id=None):
		if id:
			ndb.Key(urlsafe=id).delete()	
		else:
			self.abort(401)


allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods
app = webapp2.WSGIApplication([
	('/employee', EmployeeHandler),
	('/employee/([\w-]+)/job', JobHandler),
	('/employee/job/(.*)', JobHandler),
	('/employee/(.*)', EmployeeHandler)
], debug=True)