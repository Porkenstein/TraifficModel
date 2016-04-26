# car.py

class Car:
	#member functions 
	def __init__(self, id):
		'''Constructor initialized member variables.'''
		self.id = id
		#the speed that the driver would like to go, V_n
		self.vel = 0
		#a reference to the car that this car is following, n-1
		self.next_car = None
		#a reference to the car following this one
		self.prev_car = None
		#the maximum acceleration the driver is willing to undertake, a_n
		self.accel = 0
		#the most severe breaking the driver is willing to undertake, b_n
		self.brake = 0
		#the size of the vehicle plus a margin that drivers are not willing to intrude
		#even when stopped, s_n
		self.size = 0
		#the location of the front of this vehicle at time t, x_n(t)
		self.pos = 0
		#the speed of this car at time t, v_n(t)
		self.speed = 0

	def update(self, tstep, lane):
		#setSpeed
		#setPosition
		pass
		
	def setSpeed(self, time):
		'''A function that takes time and sets the speed value of the car.'''
		#self.speed = v_n(t)
		pass
		
	def __str__(self):
		return "car " + str(self.id) + ": Speed " + str(self.speed) + ""

	def setPosition(self, time):
		'''A function that takes time and sets the position value of the car.'''
		#self.pos = x_n(t)
		pass

	@staticmethod
	def changeLane(car, lane):

		pass