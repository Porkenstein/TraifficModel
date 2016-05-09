# car.py
from car import *
import math
from sys import *
import numpy as np
import random

class Car:
	_id = 0
	_maxspeed = 300 #kmph
	_maxpos = 30000 #m
	#member functions 
	def __init__(self, p_dict, tau, t):
		'''Constructor initialized member variables.'''
		self.id = Car._id
		Car._id += 1
		#the speed that the driver would like to go, V_n
		#this is set by a normal distribution centered on 110 km/h
		#with standard deviation of 10 km/h
		self.vel = np.random.normal(125, 3)
		#a reference to the car that this car is following, n-1.  If next_car = None, then we know that this is the first
		self.next_car = None
		#a reference to the car following this one.
		self.prev_car = None
		#the maximum acceleration the driver is willing to undertake, a_n
		self.accel = np.random.normal(3, 1)
		#the most severe breaking the driver is willing to undertake, b_n
		self.brake = np.random.normal(-5, 1)
		#the size of the vehicle plus a margin that drivers are not willing to intrude
		#even when stopped, s_n
		self.size = 0
		#the location of the front of this vehicle at time t, x_n(t)
		self.pos = 0
		#the location of the front of this vehicle at time t-tsteo, x_n(t-tstep)
		self.pos_prev = 0
		#the speed of this car at time t, v_n(t)
		self.speed = np.random.normal(110, 7)
		#the speed of this car at time t - tstep, v_n(t-tstep)
		self.speed_prev = self.speed
		# contains the probabilities for different events relevent to this single car
		self.pmap = p_dict
		# reaction time
		self.tau = tau
		# creation time
		self.t0 = t
		# road raging?
		self.angry = 0
		# wrecked?
		self.wrecked = False

	def printCarInfo(self):
		print("car id = " + str(self.id))
		print("V_n = " + str(self.vel))
		print("a_n = " + str(self.accel))
		print("b_n = " + str(self.brake))
		print("S_n = " + str(self.size))
		print("Previous Pos = " + str(self.pos_prev))
		print("Pos = " + str(self.pos))
		print("Speed = " + str(self.speed))
		
	
	# getters and setters for the next and previous cars
	def getPrevCar(self):
		if (self.prev_car is None):
			prev_car = Car(None, 1, 1)
			prev_car.size = 1
			prev_car.pos = Car._maxpos
			prev_car.speed = Car._maxspeed
		else:
			prev_car = self.prev_car
		return prev_car
	
	def getNextCar(self):
		if (self.next_car is None):
			next_car = Car(None, 1, 1)
			next_car.size = 1
			next_car.pos = -1 * Car._maxpos
			next_car.speed = 1
		else:
			next_car = self.next_car
		return next_car
	
	def setSpeed(self, time):
		'''A function that takes time and sets the speed value of the car.'''
		#self.speed = v_n(t)
		prev_car = self.getPrevCar()
		self.speed_prev = self.speed
		# TODO: make sure that cars aren't spawning on top of each other
		try:
			self.speed = min(self.speed + 2.5 * self.accel * self.tau * (1 - (self.speed / self.vel)) * \
				math.sqrt(abs(0.025 + self.speed / self.vel)), self.brake * self.tau + math.sqrt(abs(self.brake**2 \
				* self.tau**2 - self.brake * (2 * (prev_car.pos - prev_car.size - self.pos) - \
				self.speed * self.tau - (prev_car.speed**2) / min(-3.0, (self.brake - 3.0) / 2)))))
		except ValueError:
			print("ValueError.  Taking Square root of " + str((self.brake**2 \
				* self.tau**2 - self.brake * (2 * (prev_car.pos - prev_car.size - self.pos) - \
				self.speed * self.tau - (prev_car.speed**2) / min(-3.0, (self.brake - 3.0) / 2)))))
	
	def __str__(self):
		return "car " + str(self.id) + ": Speed " + str("%.2f" % self.speed) + "  Pos " + str("%.2f" % self.pos)

	def setPosition(self, tstep):
		'''A function that takes time and time step, and sets the position value of the car.
		   Uses Butchers Method from the Gipps' Model Wikipedia page.'''
		# "am I on top of the car in front of me?  If yes, go back a half meter at a time"
		prev_car = self.getPrevCar()
		while self.pos > (prev_car.pos - prev_car.size):
			self.pos -= .5
			
		k1 = self.speed_prev
		k3 = self.speed_prev + 0.25 * (self.speed - self.speed_prev)
		k4 = self.speed_prev + 0.5 * (self.speed - self.speed_prev)
		k5 = self.speed_prev + 0.75 * (self.speed - self.speed_prev)
		k6 = self.speed
		self.pos_prev = self.pos
		self.pos = self.pos_prev + (1 / 90) * (7 * k1 + 32 * k3 + 12 * k4 + 32 * k5 + \
			       7 * k6) * tstep
	def getPosition(self):
		return self.pos

	def update(self, tstep):
		#setPosition
		self.setPosition(tstep)
		#setSpeed
		self.setSpeed(tstep)
		
	@staticmethod
	def changeLane(car, lane):
		for c in lane:
			if not c is None and not car is None:
				if car.pos > c.pos:
					if not c.next_car is None and not c.next_car.prev_car is None:
						c.next_car.prev_car = car
						c.next_car = car
						if not car.next_car is None:
							car.next_car.prev_car = car.prev_car
						if not car.prev_car is None:
							car.prev_car.next_car = car.next_car
						car.next_car = c.next_car
						car.prev_car = c

		
	@staticmethod
	def remove(car, lane):
		if not car.prev_car is None:
			car.prev_car.next_car = car.next_car
		if not car.next_car is None:
			car.next_car.prev_car = car.prev_car