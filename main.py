# main.py
from car import *
from math import *
from sys import *
import numpy
import random

# constants
DEBUG = True  #output debug info
OUTPUT = True #output at each time step
NLANES = 4
TMIN = 0
TMAX = 25200
ARCHETYPEFILE = "archetypes.txt"
SOBERREACTIONTIME = 0.5
IMPAIREDREACTIONTIME = 1.0
SUNSET = 21600 # for the sake of example, it's at 6pm
SUNSETLENGTH = 1800 # half an hour
SUNSETMOD = .001 # sunset increases chance of accident every second by .1%
[SEDAN, SUV, COMPACT, MOTORCYCLE, BUS, SEMI] = range(0, 6)
[ANGRY, NORMAL, BAD, GOOD, SLOW, UNOBSERVANT, FAST, EMERGENCY, DRUNK] = range(0,9)
# 0 position is beginning of the lane
#
# sunset increases accident frequency due to poor visibility
# model from noon - 7pm,  t = 0 to 25200 (seconds)
# each car has a set of probabilities for different random events to happen
# random resolution is done in main, but the actions themselves are done as static functions from Car
# Random events: accidents (2 adjacent cars), triggered randomly when updating, passing, changing lanes, or 
#  ESCPECIALLY when another accident occurs. blocks the lane
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

# contains driver archetypes, which are just p_maps starting with their p to create.  A list of dictionaries.
_archetypes_mu = []
_archetypes_sd = []
_car_types = [] # contains the availability of each archetype to each car type.  first value is chance to create that type.

# contains the mean probabilities and their standard deviations for all random events
_mu_dict = {}
#_sd_dict = {}
_timetable = []
_onramp_loc = []
_offramp_loc = []
_car_sizes = [4.5, 5.3, 4.35, 2.1, 12.2, 17.5] #average lenths, in meters, of car types

# when generating random event, use normal distribution with above properties.
#    Compare to the P of the car's event from car.p_dict

_sunset = 0
_accidnet_mod = 0 # increases or decreases globally, making all drivers worse at avoiding accidents.  increases during sunset and poor weather.

def getNormal(key, mu_dict, sd_dict):
	if sd_dict[key] is 0:
		return mu_dict[key]
	return numpy.random.normal(mu_dict[key], sd_dict[key])
	
def buildDictionaries(roadfilename): # parse file.  Crazy code warning
	# parse the input files
	fin = open(roadfilename, mode="r")
	if fin is None:
		return 0	
	lines = fin.readlines()
	
	for i in range(0, len(lines)):
		lines[i] = lines[i].split()
		for j in range(0, len(lines[i])):
			lines[i][j] = float(lines[i][j])
	print(lines)
	
	global _mu_dict, _onramp_loc, _offramp_loc, _archetypes_mu, _archetypes_sd, _car_sizes, _car_types, _timetable 
	_timetable = lines[1:7]  # create chance to make new car at each hour, then assign the first one to the mu
	[_mu_dict["BADWEATHER"], _mu_dict["MULTICARACCIDENT"], _mu_dict["TAKEEXIT"], _mu_dict["NEWCAR"]] = lines[0] + [_timetable[0][1]]
	_onramp_loc = lines[8]
	_offramp_loc = lines[9]
	for i in range(0, 9):
		_archetypes_mu.append({ "CREATE" : lines[10][i]}) #create the archetype lists
		_archetypes_sd.append({ "CREATE" : 0}) # chance to spawn shouldn't be normal distribution! Road needs to be consistent
	for i in range(0, 6):
		_car_types.append([lines[11][i]] + lines[12+i]) #create the car lists	
	return 1
	
def buildArchetypes(archetpyefilename):
	return 1
	
def checkSunset(t):
	if ( abs(t-SUNSET) < SUNSETLENGTH ):
		if (not _sunset):
			_accident_mod += SUNSETMOD
			return 1
	if (_sunset):
		_accident_mod -= SUNSETMOD # consider making this continuous
	return 0
	
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
	
def checkCreateNewCar(mindist, lane, t): #shared between beginning of each lane
	# TODO ajust pcreate by time of day
	pcreate = _mu_dict["NEWCAR"]
	if (lane[0].getPosition() > (lane[0].size + mindist)) and ( random.random() < pcreate):
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
	
	# now determine the archetype
	roulette = random.random()
	pscalar = 1# add all ps for the selected vechile type.  1/this is the scalar value
	rtotal = 0
	tau = SOBERREACTIONTIME
	for i in range(0, len(_archetypes_mu)):
		rtotal += _archetypes_mu[i]["CREATE"]
		if(rtotal >= roulette):
			if i is DRUNK:
				tau = IMPAIREDREACTIONTIME
			for key in _archetypes_mu[i]:
				pmap[key] = getNormal(key, _archetypes_mu[i], _archetypes_sd[i]) # normal distribution to model differing behaviors
			return Car(pmap, tau, t)
	return None # shouldn't happen


if __name__ == "__main__":
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
		print("Usage: main.py <parameterfile>")
	if not buildDictionaries(roadname):
		print("Error building dictionaries!")
	elif DEBUG:
		print(_mu_dict)
		print(_car_types)
		print(_car_sizes)
		print(_offramp_loc)
		print(_onramp_loc)
		print(_timetable)
		print(_archetypes_mu)
		print(_archetypes_sd)
		
	lanes = [[],[],[],[]] # 4 lanes
	pcar = None
	ccar = None
	# create initial cars
	for j in range(0, NLANES):
		for i in range(0, ncars[j]):
			pcar = ccar
			ccar = createCar(0)
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