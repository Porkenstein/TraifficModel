# car.py
import math

class Car:
	#member functions 
	def __init__(self):
		'''Constructor initialized member variables.'''
		self.id = id
		#the speed that the driver would like to go, V_n
		self.vel = 0
		#a reference to the car that this car is following, n-1.  If next_car = None, then we know that this is the first
		self.next_car = None
		#a reference to the car following this one.
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

	def update(self, tstep):
		#setSpeed
		#setPosition
		pass
		
	def setSpeed(self, time):
		'''A function that takes time and sets the speed value of the car.'''
		#self.speed = v_n(t)
		self.speed = min(self.speed + 2.5 * self.accel * Car.TAU * (1 - (self.speed / self.vel)) * \
			math.sqrt(0.025 + self.speed / self.vel), self.brake * Car.TAU + math.sqrt(self.brake**2 \
			* Car.TAU**2 - self.brake * (2 * (self.prev_car.pos - self.prev_car.size - self.pos) - \
			self.speed * Car.TAU - (self.prev_car.speed**2) / min(-3.0, (self.brake - 3.0) / 2))))
		
	def __str__(self):
		return "car " + str(self.id) + ": Speed " + str(self.speed) + ""

	def setPosition(self, time):
		'''A function that takes time and sets the position value of the car.'''
		#self.pos = x_n(t)
		pass
		
	@staticmethod
	def changeLane(car, lane):

		pass


	#class variables
	#reaction time
	TAU = 0