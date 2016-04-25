# main.py
from car import *
from math import *
from sys import *

DEBUG = True  #output debug info
OUTPUT = True #output at each time step
NLANES = 4

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
	# create cars
	for j in range(0, NLANES):
		for i in range(0, ncars[j]):
			lanes[j].append(Car(i))
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