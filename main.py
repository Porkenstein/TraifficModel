# main.py
from car import *
from math import *
from sys import *

DEBUG = True  #output debug info
OUTPUT = True #output at each time step
NLANES = 4

# sunset increases accident frequency due to poor visibility
# model from noon - 7pm
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



if __name__ == "__main__":
	print("||| \n||| TRAFFIC JAMBULATOR 1000\n|||   by Derek Stotz and Charles Parsons\n|||\n")
	
	ncars = []
	
	len = int(input("Enter length:         "))
	ncars.append(int(input("Enter ncars in lane1: ")))
	ncars.append(int(input("Enter ncars in lane2: ")))
	ncars.append(int(input("Enter ncars in lane3: ")))
	ncars.append(int(input("Enter ncars in lane4: ")))
	tstep = int(input("Enter timestep:       "))
	tmax = int(input("Enter timemax:        "))
	# lanes = int(input("Enter lanes: ")) the model is specifically for I-60 between the 71 and the 15
	foutname = input("Enter output file:    ")
	
	lanes = [[],[],[],[]] # 4 lanes
	pcar = None
	ccar = None
	# create cars
	for j in range(0, NLANES):
		for i in range(0, ncars[j]):
			pcar = ccar
			ccar = Car(i)
			ccar.prev_car = pcar
			pcar.next_car = ccar
			lanes[j].append(ccar)
			if DEBUG: print("Making Car " + str(i))
			
	fout = open(foutname, mode="w")
	
	# iterate at each time step
	for i in range(0, tmax+1):
		for j in range(0, NLANES):
			fout.write("\n\nT = " + str(i) + "------------\n")
			if OUTPUT or DEBUG: print("\n\nT = " + str(i) + "------------\n")
			for c in lanes[j]:
				c.update(tstep)
				fout.write("|  Lane "+str(j) + ", " + str(c) + "\n")
			if OUTPUT or DEBUG: print("|  Lane "+str(j) + ", " + str(c) + "\n")
				
	# finalize
	fout.close()