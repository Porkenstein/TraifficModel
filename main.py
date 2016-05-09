# main.py
from car import *
from math import *
from sys import *
import numpy
import random

DEBUG = True  #output debug info
OUTPUT = True #output at each time step
NLANES = 4
TMIN = 0
TMAX = 25200

# 0 position is beginning of the lane
#
# sunset increases accident frequency due to poor visibility
# model from noon - 7pm,  t = 0 to 25200 (seconds)
# each car has a set of probabilities for different random events to happen
# random resolution is done in main, but the actions themselves are done as static functions from Car
# Random events: accidents (2 adjacent cars), triggered randomly when updating, passing, changing lanes, or ESCPECIALLY when another accident occurs. blocks the lane
#	single car accident, when updating, passing, changing lanes in the outermost lanes
#	road range: car turns into angry driver archetpye randomly
#	inclement weather: raod conditions change. Somethimes awful, sometimes only slightly bad.
#	engine failure (car stops, blocks lane.  totally random.  More likely with stupid/inexperienced drivers)
# Randomly generated car archetypes:
#	angru driver
#	careful driver
#	stupid/inexperienced driver
#	fantastic driver
#	old/high person
#	unobservant driver (intersection between inexperienced and old)
#	speed racer
#	COP (lowers the willing speed of surrounding drivers and makes them panic)
#	emergency vehicle (causes people to slow down)
#	drunk driver
#	motorcycle gang (big blob of cyclists)
# Vechile types
#	sedan (standard)
#	SUV/pickup (longer, less observant)
#	compact car (shorter)
#	motorcyclist (more aggressive, shorter)
#	bus (longer, more aggressive)
#	semi truck (slower, longer, better driver)

# contains driver archetypes, which are just p_maps starting with their p to create.  A dictionary of dictionaries.
_archetypes_mu = []
_archetypes_sd = []

# contains the mean probabilities and their standard deviations for all random events
_mu_dict = {}
_sd_dict = {}
# when generating random event, use normal distribution with above properties.
#    Compare to the P of the car's event from car.p_dict

_sunset = 0
_accidnet_mod = 0 # increases or decreases globally, making all drivers worse at avoiding accidents.  increases during sunset and poor weather.

def getNormal(key, mu_dict, sd_dict):
	return numpy.random.normal(mu_dict[key], sd_dict[key])
	
	
def checkSunset():
	#if ( time is sunset )
	#	if (!_sunset)
	#		_accident_mod += _mu_dict["SUNSET"]
	#	return 1
	#if (_sunset)
	#	_accident_mod -= _mu_dict["SUNSET"] # consider making this continuous
	#return 0

	
# RANDOM EVENTS
#	each event is a Markov chain sharing the car and lane states.
#	cars do the side effect, and then return if they did it or not.
	
def checkSingleCarAccident(car, lane):
	return 0
	
def checkMultiCarAccident(car1, car2, lane):
	return 0
	
def checkRoadRage(car, lane):
	return 0
	
def checkWeather():
	return 0
	
def checkEngineFailure(car):
	return 0
	
#def createPmap(): #creates a random Pmap based on what's in _mu_dict and _sd_dict
#	return dict()
	
def checkCreateNewCar(mindist, lane, t): #shared between beginning of each lane and on-ramps
	# TODO ajust pcreate by time of day
	pcreate = _mu_dict["NEWCAR"] * (t/TMAX)
	if (lane[0].getPosition > (lane[0].size + mindist)) and ( < pcreate):
		lanes[l].insert(0, createCar(t))
		return 1
	return 0

def checkChangeLane(lanes, car):
	return 0

def checkTakeExit(car):
	return 0
	
def updateCar(car, c, lanes, l, tstep, t, road_len):
	#TODO change car attributes
	car.update(tstep)
	# resolve random events
	checkChangeLane(lanes, car)
	checkEngineFailure(car)
	checkRoadRage(car, lane)
	checkSingleCarAccident(car, lane) #check for multicar accident in the main loop
	# check to see if the car is out of bounds and needs to be removed
	if car.getPosition() >= road_len:
		del lanes[l][c]
		return 0
	return 1
	
def createCar(t): # different times of day have different chances
	pmap = {}
	roulette = random.random()
	rtotal = 0
	for i in range(0, len(_archetypes_mu)):
		rtotal += _archetypes_mu[i]["CREATE"]
		if(rtotal >= roulette):
			for key, value in _archetypes_mu[i]:
				pmap[key] = getNormal(key, _archetypes_mu[i], _archetypes_sd[i]) # normal distribution to model differing behaviors
			return car(pmap)
	return None # shouldn't happen
		

if __name__ == "__main__":
	print("||| \n||| TRAFFIC JAMBULATOR 1000\n|||   by Derek Stotz and Charles Parsons\n|||\n")
	
	mu_dict = {} # a dictionary to hold probability keys
	ncars = []
	foutname = ""
	tstep = 0
	road_len = 0
	tmax = 0

	# check for input file
	if len(argv) > 1:
		fin = open(argv[1], mode="r")
		lines = fin.read().splitlines()
		road_len = int(lines[0])
		for i in range(1, 5):
			ncars.append(int(lines[i]))
		tstep = int(lines[5])
		tmax = int(lines[6])
		roadname = lines[7]
		foutname = lines[8]
		
	else:
		road_len = int(input("Enter road_length:         "))
		ncars.append(int(input("Enter ncars in lane1: ")))
		ncars.append(int(input("Enter ncars in lane2: ")))
		ncars.append(int(input("Enter ncars in lane3: ")))
		ncars.append(int(input("Enter ncars in lane4: ")))
		tstep = int(input("Enter timestep:       "))
		tmax = int(input("Enter timemax:        "))
		# lanes = int(input("Enter lanes: ")) the model is specifically for I-60 between the 71 and the 15
		roadname = input("Enter road file:    ")
		foutname = input("Enter output file:    ")
		
	lanes = [[],[],[],[]] # 4 lanes
	pcar = None
	ccar = None
	# create cars
	for j in range(0, NLANES):
		for i in range(0, ncars[j]):
			pcar = ccar
			ccar = Car()
			ccar.prev_car = pcar
			if not pcar is None:
				pcar.next_car = ccar
			lanes[j].append(ccar)
			if DEBUG: print("Making Car " + str(i))
			
	fout = open(foutname, mode="w")
	
	# iterate at each time step
	for t in range(0, tmax+1):
		# resolve random environmental events
		checkWeather()
		checkSunset()
		
		for j in range(0, NLANES):
			# resolve creation of new cars
			checkCreateNewCar(0, 0, lanes[j])
			
			fout.write("\n\nT = " + str(t) + "------------\n")
			if OUTPUT or DEBUG: print("\n\nT = " + str(t) + "------------\n")
			for c in range(0, len(lanes[j])):
				car = lanes[j][c]
				updateCar(car, c, lanes, j, t, tstep, road_len)
				checkMultiCarAccident(car, car.prev_car, lanes[j]) #does the car behind this one hit this car?
				fout.write("|  Lane "+str(j) + ", " + str(car) + "\n")
				if OUTPUT or DEBUG: print("|  Lane "+str(j) + ", " + str(car) + "\n")
				
	# finalize
	fout.close()