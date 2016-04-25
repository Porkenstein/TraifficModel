# main.py
from car import *
from math import *
from sys import *

DEBUG = True  #output debug info
OUTPUT = True #output at each time step

if __name__ == "__main__":
	print("||| \n||| TRAFFIC JAMBULATOR 1000\n|||   by Derek Stotz and Charles Parsons\n|||\n")
	
	len = int(input("Enter   len: "))
	ncars = int(input("Enter ncars: "))
	tstep = int(input("Enter tstep: "))
	tmax = int(input("Enter  tmax: "))
	foutname = input("Output file: ")
	
	cars = []
	# create cars
	for i in range(0, ncars):
		cars.append(Car(i))
		if DEBUG: print("Making Car " + str(i))
		
	fout = open(foutname, mode="w")
	
	# iterate at each time step
	for i in range(0, tmax):
		fout.write("\n\nT = " + str(i) + "------------\n")
		if OUTPUT or DEBUG: print("\n\nT = " + str(i) + "------------\n")
		for c in cars:
			c.update(tstep)
			fout.write("|  " + str(c) + "\n")
		if OUTPUT or DEBUG: print("|  " + str(c) + "\n")
			
	# finalize
	fout.close()