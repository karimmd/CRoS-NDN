#!/usr/bin/env python
# -*- Mode: python; py-indent-offset: 4; indent-tabs-mode: nil; coding: utf-8; -*-
from datetime import datetime 
from subprocess import call 
from sys import argv 
import os 
import subprocess 
import workerpool 
import multiprocessing 
import argparse 
import random
######################################################################
######################################################################
######################################################################
parser = argparse.ArgumentParser(description='Simulation runner') 

parser.add_argument('scenarios', metavar='scenario', type=str, nargs='*', 
			help='Scenario to run') 

parser.add_argument('-l', '--list', dest="list", action='store_true', default=False, 
			help='Get list of available scenarios') 

parser.add_argument('-s', '--simulate', dest="simulate", action='store_true', default=False,
                    help='Run simulation and postprocessing (false by default)') 

parser.add_argument('-g', '--no-graph', dest="graph", action='store_false', default=True,
                    help='Do not build a graph for the scenario (builds a graph by default)')
                    
parser.add_argument('-r', '--rm', dest="rmresults", action='store_true', default=False,
                    help='Clean and delete all files in -temp- folder')
                    
parser.add_argument('-u', '--upload', dest="upload", action='store_true', default=False,
                    help='Move gross results to localresults folder and processed results to results folder') 

args = parser.parse_args() 

if not args.list and not args.rmresults and not args.upload and len(args.scenarios)==0:
    print "ERROR: at least one scenario need to be specified"
    parser.print_help()
    exit (1) 

if args.list:
    print "Available scenarios: " 
else:
    if args.simulate:
        print "Simulating the following scenarios: " + ",".join (args.scenarios)
    if args.graph:
        print "Building graphs for the following scenarios: " + ",".join (args.scenarios)
        
    if args.rmresults:
        print "Cleaning all files in -temp- folder!"
        print "Erasing directory: " + os.getcwd() + "/temp/*"
        os.system("rm -r ./temp/*")
        exit(0)
    if args.upload:
        print "Move gross results to localresults folder and processed results to results folder"
        now = datetime.now()
        nowstr = now.strftime("%Y%m%d-%H%M%S")
        os.mkdir("./localresults/%s" % nowstr)
        os.mkdir("./results/%s" % nowstr)
        os.system("mv ./temp/var* ./localresults/%s/" % nowstr)
        os.system("mv ./temp/* ./results/%s/" % nowstr)
        exit(0)
        
######################################################################
######################################################################
######################################################################
class SimulationJob (workerpool.Job):
    "Job to simulate things"
    def __init__ (self, cmdline):
        self.cmdline = cmdline
    def run (self):
        print (" ".join (self.cmdline))
        subprocess.check_call(" ".join (self.cmdline), shell=True)
        subprocess.call (" ".join (self.cmdline), shell=True) 

pool = workerpool.WorkerPool(size = multiprocessing.cpu_count()) 

class Processor:
    def run (self):
        if args.list:
            print " " + self.name
            return
           
        if "all" not in args.scenarios and self.name not in args.scenarios:
            return
        if args.list:
            pass
        else:
            if args.simulate:
                self.simulate ()
                pool.join ()
            if args.graph:
                self.graph ()
    def graph (self):
        os.system("rm ./temp/*.png")
        os.system("rm ./temp/*.txt")
        self.postprocess ()
	
class Base:
	def __init__ (self, name, script, stratset, nprefix, topo, controller, rate, hellorate, consxint, cons, prodxint, prod, consprefs, consperc, 
ttime, failtime, constime, regrate, fibsize, samplei, lang, varx, maxXaxis, suffix, runs, counter, varset):
		self.name = name
		self.script = script
		self.stratset = stratset
		self.nprefix = nprefix
		self.topo = topo
		self.controller = controller
		self.rate = rate
		self.hellorate = hellorate
		self.consxint = consxint
		self.cons = cons
		self.prodxint = prodxint
		self.prod = prod
		self.consprefs = consprefs
		self.consperc = consperc
		self.ttime = ttime
		self.failtime = failtime
		self.ctime = constime
		self.regrate = regrate
		self.fibsize = fibsize
		self.samplei = samplei
		self.lang = lang
		self.varx = varx
		self.maxXaxis = maxXaxis
		self.suffix = suffix
		self.runs = runs
		self.counter = counter
		self.varset = varset

	def writefiles (self):
		f = open("graphs/variables.r","w")
		f.write("constime=%s + 1" % self.ctime)
		f.write("\nlang='%s'" % self.lang)
		f.write("\nstratset=c(")
		for strat in self.stratset:
			f.write("'%s'," % strat)
		f.write("'null')")
		f.write("\nvarx='%s'" % self.varx)
		f.write("\nvarx2=quote(%s)" % self.varx)
		f.write("\nttime=%s" % self.ttime)
		f.write("\nmaxXaxis=%s" % self.maxXaxis)
		f.close()
			
	def writecmdline (self):
		self.seed = random.randint(1,10000)
		os.mkdir("./temp/%s" % self.suffix)
		f = open("./graphs/varx.r","w")
		f.write("varx1='%s'" % self.counter)
		f.write("\nsuffix='%s'" % self.suffix)
		f.close()
		for strat in self.stratset:
			cmdline = ["LD_LIBRARY_PATH=/usr/local/lib", "./ptimized/%s" % self.script,"--strategy=%s" % strat, "--nprefix=%s" % 
self.nprefix, "--topo=%s" % self.topo, "--consumer=%s" % self.cons, "--producer=%s" % self.prod, "--controller=%s" % self.controller, "--rate=%s" % 
self.rate, "--hellorate=%s" % self.hellorate, "--consxint=%s" % self.consxint, "--prodxint=%s" % self.prodxint, "--consprefs=%s" % self.consprefs, 
"--consperc=%s" % self.consperc, "--time=%s" % self.ttime, "--failtime=%s" % self.failtime, "--constime=%s" % self.ctime, "--regrate=%s" % 
self.regrate, "--fibsize=%s" % self.fibsize, "--seed=%s" % self.seed, "--samplei=%s" % self.samplei, "--suffix=%s" % self.suffix,]
			f = open("./temp/cmdline.log","a")
			f.write("\nCMDLINE: "+ " ".join (cmdline))
			f.close()
			job = SimulationJob (cmdline)
			pool.put (job)

	def writedatafile (self):
		f = open("temp/summaryXaxis.txt","w")
		f.write("%s Strategy ise\n" % self.varx)
		f.close()
		f = open("temp/summarytime.txt","w")
		f.write("%s Strategy TimeSec ise\n" % self.varx)
		f.close()		
	
	def processdata (self):
		self.writefiles()
		self.writedatafile()
		for item in self.varset:
			f = open("temp/summary.txt","w")
			f.write("Strategy TimeSec ise\n")
			f.close()
			run = 0
			while (run < self.runs):
				self.suffix = "var-%s-value-%s-run-%s" % (self.varx, item, run)
				f = open("./graphs/varx.r","w")
				f.write("varx1='%s'" % item)
				f.write("\nsuffix='%s'" % self.suffix)
				f.close()
				subprocess.call ("./graphs/strategy.r", shell=True)
				os.rename("temp/SignallingEfficiency-Time.png","temp/SignallingEfficiency-Time-%s.png" % self.suffix)
				run = run + 1
			subprocess.call ("./graphs/strategy-95.r", shell=True)
			os.rename("temp/summary.txt","temp/summary-%s.txt" % self.suffix)
			os.rename("temp/Error.png","temp/Error-%s.png" % self.suffix)
	        subprocess.call ("./graphs/strategy-xaxis.r", shell=True)

	def processdata1 (self):
		self.writefiles()
		self.writedatafile()
		for item in self.varset:
			f = open("temp/summary.txt","w")
			f.write("Strategy TimeSec ise\n")
			f.close()
			run = 0
			while (run < self.runs):
				self.suffix = "var-%s-value-%s-run-%s" % (self.varx, item, run)
				f = open("./graphs/varx.r","w")
				f.write("varx1='%s'" % item)
				f.write("\nsuffix='%s'" % self.suffix)
				f.close()
				subprocess.call ("./graphs/strategy1.r", shell=True)
				run = run + 1
			subprocess.call ("./graphs/strategy-95v1.r", shell=True)
			os.rename("temp/summary.txt","temp/summary-%s.txt" % self.suffix)
			os.rename("temp/Error.png","temp/Error-%s.png" % self.suffix)
        	subprocess.call ("./graphs/strategy-xaxisv1.r", shell=True)
		subprocess.call ("./graphs/strategy-time.r", shell=True)
		
class OneRunOneStrategy (Processor):
	def __init__ (self, parameters):
		self.parameters = parameters
		self.name = parameters.name
	def simulate (self):
		self.parameters.writefiles()
		self.parameters.writecmdline()
	
	def postprocess (self):
		subprocess.call ("./graphs/strategy1.r", shell=True)
		pass 

class ConsumerRate (Processor):
	def __init__ (self, parameters):
		self.parameters = parameters
		self.name = parameters.name
		
	def simulate (self):
		self.parameters.writefiles()
		for counter in self.parameters.varset:
			run = 0
			while (run < self.parameters.runs):
				self.parameters.suffix = "var-%s-value-%s-run-%s" % (self.parameters.varx, counter,run)
				self.parameters.rate = counter
				self.parameters.counter = counter
				self.parameters.writecmdline()
				run = run + 1
	
	def postprocess (self):
		self.parameters.processdata1() 

class HelloRate (Processor):
	def __init__ (self, parameters):
		self.parameters = parameters
		self.name = parameters.name
		
	def simulate (self):
		self.parameters.writefiles()
		for counter in self.parameters.varset:
			run = 0
			while (run < self.parameters.runs):
				self.parameters.suffix = "var-%s-value-%s-run-%s" % (self.parameters.varx, counter,run)
				self.parameters.hellorate = counter
				self.parameters.counter = counter
				self.parameters.writecmdline()
				run = run + 1
	
	def postprocess (self):
		self.parameters.processdata1()

class Topo (Processor):
        def __init__ (self, parameters):
                self.parameters = parameters
                self.name = parameters.name

        def simulate (self):
                self.parameters.writefiles()
                for counter in self.parameters.varset:
                        run = 0
                        while (run < self.parameters.runs):
								self.parameters.cons = random.randint(1,10000)
								self.parameters.prod = random.randint(1,10000)
								self.parameters.controller = random.randint(1,10000)
								self.parameters.suffix = "var-%s-value-%s-run-%s" % (self.parameters.varx, counter,run)
								self.parameters.topo = counter
								self.parameters.counter = counter
								self.parameters.writecmdline()
								run = run + 1

		def postprocess (self):
				self.parameters.processdata1()

class PrefixChangeProbability (Processor):
	def __init__ (self, parameters):
		self.parameters = parameters
		self.name = parameters.name
		
	def simulate (self):
		self.parameters.writefiles()
		for counter in self.parameters.varset:
			run = 0
			while (run < self.parameters.runs):
				self.parameters.suffix = "var-%s-value-%s-run-%s" % (self.parameters.varx, counter,run)
				self.parameters.consperc = counter
				self.parameters.counter = counter
				self.parameters.writecmdline()
				run = run + 1
	
	def postprocess (self):
		self.parameters.processdata1()				

class NumberofPrefixes (Processor):
	def __init__ (self, parameters):
		self.parameters = parameters
		self.name = parameters.name
		
	def simulate (self):
		self.parameters.writefiles()
		for counter in self.parameters.varset:
			run = 0
			while (run < self.parameters.runs):
				self.parameters.suffix = "var-%s-value-%s-run-%s" % (self.parameters.varx, counter,run)
				self.parameters.nprefix = counter
				self.parameters.consprefs = counter
				self.parameters.counter = counter
				self.parameters.writecmdline()
				run = run + 1
	
	def postprocess (self):
		self.parameters.processdata1()	

class FIBSize (Processor):
	def __init__ (self, parameters):
		self.parameters = parameters
		self.name = parameters.name
		
	def simulate (self):
		self.parameters.writefiles()
		for counter in self.parameters.varset:
			run = 0
			while (run < self.parameters.runs):
				self.parameters.suffix = "var-%s-value-%s-run-%s" % (self.parameters.varx, counter,run)
				self.parameters.fibsize = counter
				self.parameters.counter = counter
				self.parameters.writecmdline()
				run = run + 1
	
	def postprocess (self):
		self.parameters.processdata1()	
		
try:
    # Simulation, processing, and graph building
	baseparameters = Base (name="linkfailure",
					script="linkfail",			
					stratset=["CRoS-NDN",],
					nprefix=1,
					topo="topo-3-way.txt",
					controller="Ctr1",
					rate=20,
					hellorate=0.1,
					consxint=1,
					cons = "Src1",
					prodxint=1,
					prod = "Prd1",
					consprefs=1,
					consperc=10,
					ttime=3001,
					failtime=1,
					constime=0,
					regrate=20,
					fibsize=100,
					samplei=50,
					lang="en",
					varx="rrate",
					maxXaxis=11,
					suffix="single-run",
					runs=2,
					counter=1,
					varset=[20,])
	baseexperiment = OneRunOneStrategy (parameters = baseparameters)
	baseexperiment.run ()
	
	rate = [2, 20, 200,]
	rateparameters = baseparameters
	rateparameters.name = "consumerrate"
	rateparameters.varset = rate
	rateparameters.varx = "rrate"
	rateexperiment = ConsumerRate (parameters = rateparameters)
	rateexperiment.run ()
	
	#stratset=["CRoS-NDN", "OSPFLike",]
	fibcompareparameters = rateparameters
	fibcompareparameters.name = "fibcomparerate"
	fibcompareparameters.nprefix = 200
	#fibcompareparameters.stratset = stratset
	fibcompareparameters.consprefs = 200
	fibcompareparameters.fibsize = 300
	fibcompareparameters.script = "linkfail-fibcompare-cprand"
	fibcompareparameters.runs = 10
	#fibcompareparameters.ttime=5001
	fibcompareexperiment = ConsumerRate (parameters = fibcompareparameters)
	fibcompareexperiment.run()	
	
	prefixchangeprobability = [5, 20, 80,]
	fibcompareparameters1 = fibcompareparameters
	fibcompareparameters1.name = "fibcompareprefixchange"
	fibcompareparameters1.varset = prefixchangeprobability
	fibcompareparameters1.varx = "consperc"	
	fibcompareparameters1.fibsize = 100
	fibcompareparameters1.rate = 20
	fibcompareparameters1.script = "linkfail-fibcompare-cprand"
	fibcompareexperiment1 = PrefixChangeProbability (parameters = fibcompareparameters1)
	fibcompareexperiment1.run()	
	
	numberofprefixes = [40, 80, 160,]
	fibcompareparameters2 = fibcompareparameters
	fibcompareparameters2.name = "fibcomparenumberofprefixes"
	fibcompareparameters2.varset = numberofprefixes
	fibcompareparameters2.varx = "nprefix"	
	fibcompareparameters2.fibsize = 30
	fibcompareparameters2.rate = 20
	fibcompareparameters2.script = "linkfail-fibcompare-cprand"
	fibcompareexperiment2 = NumberofPrefixes (parameters = fibcompareparameters2)
	fibcompareexperiment2.run()		

	numberofprefixes2 = [3,]
	fibcompareparameters3 = fibcompareparameters
	fibcompareparameters3.name = "cwindownprefix"
	fibcompareparameters3.varset = numberofprefixes2
	fibcompareparameters3.varx = "nprefix"	
	fibcompareparameters3.fibsize = 3
	fibcompareparameters3.ttime = 120
	fibcompareparameters3.fibsize = 3
	fibcompareparameters3.samplei = 5
	fibcompareparameters2.runs = 2
	fibcompareparameters3.script = "linkfail-cwindow-nprefix"
	fibcompareexperiment3 = NumberofPrefixes (parameters = fibcompareparameters3)
	fibcompareexperiment3.run()		
	
	numberofprefixes3 = [5, 10, 20,]
	fibcompareparameters4 = fibcompareparameters3
	fibcompareparameters4.name = "ccbrnprefix"
	fibcompareparameters4.script = "linkfail-ccbr-nprefix"
	fibcompareparameters4.runs = 10
	fibcompareparameters4.samplei = 50
	fibcompareparameters4.ttime = 3000
	fibcompareparameters4.varset = numberofprefixes3
	fibcompareparameters4.fibsize = 10
	fibcompareexperiment4 = NumberofPrefixes (parameters = fibcompareparameters4)
	fibcompareexperiment4.run()	

	fibsize1 = [1, 5, 10,]
	fibcompareparameters5 = fibcompareparameters4
	fibcompareparameters5.name = "fibsize"
	fibcompareparameters5.varset = fibsize1
	fibcompareparameters5.varx = "fibsize"
	fibcompareparameters5.nprefix = 10
	fibcompareparameters5.consprefs = 10
	fibcompareexperiment5 = FIBSize (parameters = fibcompareparameters5)
	fibcompareexperiment5.run()	
	
	fibsize2 = [5, 10, 20,]
	fibsize3 = [5,]
	fibcompareparameters6 = fibcompareparameters5
	fibcompareparameters6.name = "linkrecovery"
	fibcompareparameters6.varset = fibsize2
	fibcompareparameters6.script = "linkrecovery-ccbr-nprefix"	
	fibcompareparameters6.ttime = 3000
	fibcompareparameters6.failtime = 3
	fibcompareparameters6.nprefix = 10
	fibcompareparameters6.consprefs = 10
	fibcompareexperiment6 = FIBSize (parameters = fibcompareparameters6)
	fibcompareexperiment6.run()	
	
	lifetime = ["25ms", "500ms", "2s",]
	fibcompareparameters7 = fibcompareparameters6
	fibcompareparameters7.name = "lifetime"
	fibcompareparameters7.varset = lifetime
	fibcompareparameters7.script = "linkrecovery-ccbr-lifetime"
	fibcompareparameters7.varx = "consperc"
	fibcompareparameters7.fibsize = 20
	fibcompareexperiment7 = PrefixChangeProbability (parameters = fibcompareparameters7)
	fibcompareexperiment7.run()		
	
	hellorate = [0.2, 0.1, 0.05]
	helloparameters = baseparameters
	helloparameters.name = "hellorate"
	helloparameters.varset = hellorate
	helloparameters.varx = "hellorate"
	helloexperiment = HelloRate (parameters = helloparameters)
	helloexperiment.run ()

	helloparameters1 = helloparameters
	helloparameters1.name = "helloratedetail"
	helloparameters1.failtime = 2
	helloparameters1.ttime = 201
	helloparameters1.runs = 1
	helloparameters1.samplei = 5
	helloexperiment1 = HelloRate (parameters = helloparameters1)
	helloexperiment1.run ()

	topologies = ["4755.txt", "topo-3-way.txt", "1221.txt", "1755.txt", "3257.txt",]
	topologies2 = ["5", "11", "279", "163", "191",]
	topoparameters = baseparameters
	topoparameters.name = "topologies"
	topoparameters.varset = topologies
	topoparameters.varx = "topo"
	topoparameters.script = "strategy-comparev5"
	topoparameters.controller = 0
	topoparameters.hellorate = 0.05
	topoparameters.failtime = 0
	topoparameters.ttime = 250
	topoparameters.runs = 20
	topoparameters.samplei = 10
	topoexperiment = Topo (parameters = topoparameters)
	topoexperiment.run ()
	
	
finally:
    pool.join ()
    pool.shutdown ()
