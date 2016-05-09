# main.py
from car import *
from math import *
from sys import *
import numpy
import random

# constants
DEBUG = False #output debug info
OUTPUT = False #output at each time step
NLANES = 4
TMIN = 0
TMAX = 25200
ARCHETYPEFILE = "archetypes.txt"
SOBERREACTIONTIME = 0.5
IMPAIREDREACTIONTIME = 1.0
SUNSET = 21600 # for the sake of example, it's at 6pm
SUNSETLENGTH = 1800 # half an hour
SUNSETMOD = .001 # sunset increases chance of accident every second by .1%
WEATHERMOD = .001
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

_weather = 0
_sunset = 0
_accident_mod = 0 # increases or decreases globally, making all drivers worse at avoiding accidents.  increases during sunset and poor weather.

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
	[_mu_dict["WEATHER"], _mu_dict["MULTICARACCIDENT"], _mu_dict["TAKEEXIT"], _mu_dict["NEWCAR"]] = lines[0] + [_timetable[0][1]]
	_onramp_loc = lines[8]
	_offramp_loc = lines[9]
	for i in range(0, 9):
		_archetypes_mu.append({ "CREATE" : lines[10][i]}) #create the archetype lists
		_archetypes_sd.append({ "CREATE" : 0}) # chance to spawn shouldn't be normal distribution! Road needs to be consistent
	for i in range(0, 6):
		_car_types.append([lines[11][i]] + lines[12+i]) #create the car lists	
	return 1
	
def buildArchetypes(archetpyefilename):
	# parse the input files
	fin = open(archetpyefilename, mode="r")
	if fin is None:
		return 0	
	lines = fin.readlines()
	
	for i in range(0, len(lines)):
		lines[i] = lines[i].split()
		for j in range(0, len(lines[i])):
			lines[i][j] = float(lines[i][j])
	print(lines)
	
	global _archetypes_mu, _archetypes_sd 
	i = 0
	while i < 18:
		_archetypes_mu[i//2]["SPEEDING"] = lines[i][0]
		_archetypes_mu[i//2]["ROADRAGE"] = lines[i][1]
		_archetypes_mu[i//2]["SINGLECARACCIDENT"] = lines[i][2]
		_archetypes_mu[i//2]["ENGINEFAILURE"] = lines[i][3]
		_archetypes_mu[i//2]["CHANGELANE"] = lines[i][4]
		_archetypes_sd[i//2]["SPEEDING"] = lines[i+1][0]
		_archetypes_sd[i//2]["ROADRAGE"] = lines[i+1][1]
		_archetypes_sd[i//2]["SINGLECARACCIDENT"] = lines[i+1][2]
		_archetypes_sd[i//2]["ENGINEFAILURE"] = lines[i+1][3]
		_archetypes_sd[i//2]["CHANGELANE"] = lines[i+1][4]
		i = i + 2
	return 1
	
def checkSunset(t):
	if ( abs(t-SUNSET) < SUNSETLENGTH ):
		if (not _sunset):
			_accident_mod += SUNSETMOD
			_sunset = 1
			return 1
		if (_sunset):
			_accident_mod -= SUNSETMOD # consider making this continuous
			_sunset = 0
	return 0
	
# RANDOM EVENTS
#	each event is a Markov chain sharing the car and lane states.
#	cars do the side effect, and then return if they did it or not.

def checkSingleCarAccident(car, lane):
	if ( random.random() < car.pmap["SINGLECARACCIDENT"] ):
		car.wrecked = 1
		car.vel = 0
		car.speed = 0
		return 1
	return 0
	
def checkMultiCarAccident(car1, car2, lane): # far more probably than single car
	if ( random.random() < _mu_dict["MULTICARACCIDENT"] ):
		car.wrecked = 1
		car.vel = 0
		car.speed = 0
	return 0
	
def checkRoadRage(car, lane):
	if ( random.random() < car.pmap["ROADRAGE"] ):
		if (not car.angry):
			car.pmap = createPmap(ANGRY)
			car.angry = 1
			return 1
		else:
			car.pmap = createPmap(NORMAL)
			car.angry = 0
	return 0
	
	
def checkWeather():
	if ( random.random() < _mu_dict["WEATHER"] ):
		if (not _weather):
			_accident_mod += WEATHERMOD
			_weather = 1
			return 1
		if (_weather):
			_accident_mod -= WEATHERMOD # consider making this continuous
			_weather = 0
	return 0
	
def checkEngineFailure(car): # just treat like a wreck for now
	if ( random.random() < car.pmap["ENGINEFAILURE"] ):
		car.wrecked = 1
		car.vel = 0
		car.speed = 0
		return 1
	return 0
	
def createPmap(i): #creates a random Pmap based on what's in _mu_dict and _sd_dict
	pmap = {}
	for key in _archetypes_mu[i]: # i is the archetype index
		pmap[key] = getNormal(key, _archetypes_mu[i], _archetypes_sd[i]) # normal distribution to model differing behaviors
	return pmap
	
def checkUpdateGlobals(t):
	checkWeather()
	checkSunset(t)
	# update incoming traffic density
	for i in range(0, len(_timetable)):
		if t is _timetable[i][0]:
			_mu_dict["CREATE"] = _timetable[i][1]
			return 1
	return 0
	
def checkCreateNewCar(mindist, lane, t): #shared between beginning of each lane
	# TODO ajust pcreate by time of day
	pcreate = _mu_dict["NEWCAR"]
	if (random.random() < pcreate):
		lane.insert(0, createCar(t))
		return 1
	return 0
	
def checkChangeLane(lanes, car):
	dice = random.random()
	if ( random.random() < car.pmap["CHANGELANE"] ):
		if j is (len(lanes)-1):
			Car.changeLane(car.next_car, lanes[j-1]) # pass to right if crash is leftmost
		elif j is 0 or dice < .5:
			Car.changeLane(car.next_car, lanes[j+1]) # prefer to pass on the left
		else:
			Car.changeLane(car.next_car, lanes[j-1]) # pass to right if crash is leftmost
		return 1
	return 0

def checkTakeExit(car, c, lanes, l):
	if ( random.random() < _mu_dict["TAKEEXIT"] and l is 0): #rightmost lane
		del lanes[l][c]
	return 0
	
def updateCar(car, c, lanes, l, tstep, t, road_len):
	if car.getPosition() >= road_len:
		del lanes[l][c]
		return 0
	#TODO change car attributes
	# resolve random events
	checkChangeLane(lanes, car)
	checkEngineFailure(car)
	checkRoadRage(car, lanes[l])
	checkSingleCarAccident(car, lanes[l]) #check for multicar accident in the main loop
	# check to see if the car is out of bounds and needs to be removed
	if not car.wrecked:
		car.update(tstep)
	return 1
	
def createCar(t): # different times of day have different chances
	# determine the car type
	roulette = random.random()
	rtotal = 0
	type = 0
	for i in range(0, len(_car_types)):
		rtotal += _car_types[i][0]
		if rtotal > roulette:
			type = i
			break
	# now determine the archetype
	roulette = random.random()
	pscalar = 9/sum( _car_types[type][1:9])# add all ps for the selected vechile type.  9/this is the scalar value
	rtotal = 0
	tau = SOBERREACTIONTIME
	for i in range(0, len(_archetypes_mu)):
		rtotal += _archetypes_mu[i]["CREATE"]
		if(rtotal >= roulette):
			if i is DRUNK:
				tau = IMPAIREDREACTIONTIME
			pmap = createPmap(i)
			car = Car(pmap, tau, t)
			car.size = _car_sizes[type]
			if DEBUG: print("NEW CAR of type " + str(type) + " and driver archetype "+ str(i) +" : " + str(car))
			return car
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
	if not (buildDictionaries(roadname) and buildArchetypes(ARCHETYPEFILE)):
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
			if DEBUG: print("Making Car " + str(ccar.id))
			
	fout = open(foutname, mode="w")
	
	# iterate at each time step
	for t in range(0, tmax+1):
		# resolve random environmental events
		checkUpdateGlobals(t)
		
		for j in range(0, NLANES):
			# resolve creation of new cars
			
			checkCreateNewCar(0, lanes[j], t)
			
			fout.write("\n\nT = " + str(t) + "------------\n")
			if OUTPUT or DEBUG: print("\n\nT = " + str(t) + "------------\n")
			c = 0
			while c < len(lanes[j]):
				car = lanes[j][c]
				if(car.wrecked):
					if not checkMultiCarAccident(car, car.next_car, lanes[j]): #does the car behind this one hit this car?
						if j is (len(lanes)-1):
							Car.changeLane(car.next_car, lanes[j-1]) # pass to right if crash is leftmost
						else:
							Car.changeLane(car.next_car, lanes[j+1]) # prefer to pass on the left
				else:
					updateCar(car, c, lanes, j, t, tstep, road_len)
				fout.write("|  Lane "+str(j) + ", " + str(car) + "\n")
				#if OUTPUT or DEBUG: print("|  Lane "+str(j) + ", " + str(car) + "\n")
				c = c+1
	# finalize
	fout.close()