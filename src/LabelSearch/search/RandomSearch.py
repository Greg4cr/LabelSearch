# Gregory Gay (greg@greggay.com)
# Simple random search. Will generate suites until the budget runs out,
# returning the best seen.

# Command line options:
# -p <instrumented program>
# -o <basename of test suite, default is (instrumented program)_suite.c>
# -l <maximum single test length, default is 10 steps (assignments or calls)>
# -m <maximum test suite size, default is 25>
# -b <search budget, default is 120 seconds>
# -n <population size, default is 100>

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import copy
import getopt
import sys
import os
import time
import re
from subprocess import Popen, call, PIPE, STDOUT
from ..generation.Generator import Generator
from ..structures.TestSuite import TestSuite

class RandomSearch(): 

    # Suite generator
    generator = Generator()
    # Program filename
    program = ""
    # Suite basename
    outFile = ""
    # Search budget
    budget = 120
    # Population
    population = 100
    # Max suite size
    maxSuiteSize = 25.0
    # Max test length
    maxLength = 10.0


    # Central search
    def search(self):
        # Set up generator
        self.generator.setProgram(self.program)
        self.generator.maxLength = self.maxLength
        self.generator.maxSuiteSize = self.maxSuiteSize
        
        bestScore = 1000000
        bestSuite = TestSuite()

        generation = 0
        startTime = time.time()
        elapsedTime = 0
        while elapsedTime < self.budget:
            generation += 1
            # Generate test suites
            suites = []
            for index in range(0,self.population):
                if ".c" in self.outFile:
                    suiteName = self.outFile[:self.outFile.index(".c")] + str(index) + ".c"
                else:
                    suiteName = self.outFile + str(index) + ".c"

                suites.append(self.generator.generate(suiteName))            
                # Are they better than what has been seed to date?
                if suites[index].getScore() < bestScore:
                    bestSuite = copy.deepcopy(suites[index])
                    bestScore = bestSuite.getScore()

            # What is the best suite seen?
            print "Generation " + str(generation) + ":"
            print "Best Score: " + str(bestScore)
            print bestSuite.getObligations()

            # Clean up suites we aren't keeping
            suiteName = bestSuite.getFileName()
            newName = re.sub("\d+", "_best",suiteName)
            bestSuite.setFileName(newName)
            bestSuite.writeSuiteFile()

            for index in range(0, self.population):
                suiteName = suites[index].getFileName()
                rmProcess = Popen("rm " + suiteName + "*", stdout = PIPE, stderr = PIPE, shell = True)
                (rOutput, eError) = rmProcess.communicate()

            # Calculate time
            currentTime = time.time()
            elapsedTime = currentTime - startTime
            print "Elapsed Time: " + str(elapsedTime)

def main(argv):
    search = RandomSearch()
    program = ""
    outFile = ""
    maxSuiteSize = 25.0
    maxLength = 10.0
    budget = 120
    populationSize = 100

    try:
        opts, args = getopt.getopt(argv,"hp:o:l:m:b:n:")
    except getopt.GetoptError:
        print 'RandomSearch.py -p <program name> -o <output filename> -l <max individual test length> -m <max suite size> -b <search budget> -n <population size>'
      	sys.exit(2)
  		
    for opt, arg in opts:
        if opt == "-h":
            print 'RandomSearch.py -p <program name> -o <output filename> -l <max individual test length> -m <max suite size> -b <search budget> -n <population size>'
            sys.exit()
      	elif opt == "-p":
            if arg == "":
                raise Exception('No program specified')
            else:
                program = arg
        elif opt == "-o":
            outFile = arg
        elif opt == "-l":
            maxLength = float(arg)
        elif opt == "-m":
            maxSuiteSize = float(arg)
        elif opt == "-b":
            budget = int(arg)
        elif opt == "-p":
            populationSize = int(arg)

    if program == "":
        raise Exception('No program specified')
    else:
        if outFile == "":
            outFile = program[:program.index(".c")]+"_suite"
        search.budget = budget
        search.population = populationSize
        search.maxLength = maxLength
        search.maxSuiteSize = maxSuiteSize
        search.program = program
        search.outFile = outFile
	search.search()

# Call into main
if __name__ == '__main__':
    main(sys.argv[1:])
