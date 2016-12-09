# Gregory Gay (greg@greggay.com)
# Verifies that generated suites run without segmentation faults.
# Tests that cause segmentation faults are commented-out, but left in, as they often indicate faults.

# Command line options:
# -s <test suite filename>
# -o <output filename, if different from suite filename>

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import getopt
import sys
import os
from subprocess import Popen, call, PIPE, STDOUT
from ..structures.TestSuite import TestSuite

class Verifier(): 
    # Test suite, in processable form
    suite = TestSuite()

    # Central process of instrumentation
    def verify(self,fileName,outFile):
        # Get suite code in an easy-to-process form
        self.suite.setFileName(fileName)
        self.suite.importSuite()
      
        # Compile and attempt to run the suite.
        (output, error) = self.compileSuite(fileName)

        if outFile != fileName:
            self.suite.setFileName(outFile)

        # If an executable is produced, compilation succeeded.                    
        if "Segmentation fault" in error:
            print error
            print "Attempting to find source(s) of segmentation faults"
           
            # Turn off all tests
            # This step is repeated twice because of overlapping substrings.
            testList = self.suite.getTestList()
            for entry in range(0,len(testList)):
                if testList[entry] == 1:
                    testList[entry] = 0
            self.suite.setTestList(testList)

            # See if code runs with no tests enabled
            
            self.suite.writeSuiteFile()
            (output, error) = self.compileSuite(outFile)
            if error != "":
                raise Exception("Issue with test execution code, not test suite.")

            for testNum in range(0,len(self.getTests())):
                # Turn one one test, try to run suite. 
                # If it seg-faults, then turn off that test.
                testList = self.suite.getTestList()
                testList[testNum] = 1
                self.suite.setTestList(testList)
                #print self.getTestList()
                self.suite.writeSuiteFile()
                (output, error) = self.compileSuite(outFile)
                if error != "":
                    #print error
                    testList = self.suite.getTestList()
                    testList[testNum] = 0
                    self.suite.setTestList(testList)
        else:
            # Print test suite to file
            self.suite.writeSuiteFile()

    # Compiles and runs suite
    def compileSuite(self, fileName):
        if os.path.isfile(fileName):
            path = os.path.dirname(fileName)
            call("rm a.out", shell=True)
            call("gcc " + fileName, shell=True)
            
            if os.path.isfile("a.out"):
                # Does it execute without segmentation faults?
                process = Popen("./a.out", stdout=PIPE, stderr=PIPE, shell=True)
                (output, error) = process.communicate()
                call("rm a.out", shell=True)
                return (output, error)
            else:
                raise Exception("Suite failed to compile")
        else:
            raise Exception("The suite file does not exist.")

def main(argv):
    verifier = Verifier()
    fileName = ""
    outFile = ""

    try:
        opts, args = getopt.getopt(argv,"hs:o:")
    except getopt.GetoptError:
        print 'Verifier.py -s <test suite filename> -o <output filename>'
      	sys.exit(2)
  		
    for opt, arg in opts:
        if opt == "-h":
            print 'Verifier.py -s <test suite filename> -o <output filename>'
            sys.exit()
      	elif opt == "-s":
            if arg == "":
                raise Exception('No filename specified')
            else:
               fileName = arg
        elif opt == "-o":
            outFile = arg

    if outFile == "":
        outFile = fileName

    if fileName == "":
        raise Exception('No suite filename specified')
    else:
        verifier.verify(fileName,outFile)

# Call into main
if __name__ == '__main__':
    main(sys.argv[1:])
