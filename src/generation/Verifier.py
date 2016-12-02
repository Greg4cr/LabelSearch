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

class Verifier(): 
    # Test suite, in processable form
    __suiteCode = []
    __testList = ""
    __tests = []


    # Central process of instrumentation
    def verify(self,fileName,outFile):
        # Get suite code in an easy-to-process form
        self.processSuite(fileName)
        print self.getSuiteCode()
        print self.getTestList()
        print self.getTests()
      
        # Compile and attempt to run the suite.
        call("rm a.out", shell=True)
        call("gcc "+fileName, shell=True)

        # If an executable is produced, compilation succeeded.
        if os.path.isfile("a.out"):
            # Does it execute without segmentation faults?
            process = Popen("./a.out", stdout=PIPE, stderr=PIPE, shell=True)
            (output, error) = process.communicate()
            
            if "Segmentation fault" in error:
                print error
                print "Attempting to find source(s) of segmentation faults"
                self.writeSuiteFile(outFile)
            else:
                # Print test suite to file
                self.writeSuiteFile(outFile)
        else:
            raise Exception("Suite failed to compile")

    # Read in suite file and build a list of tests
    def processSuite(self, fileName):
        testList = ""
        tests = []
        suiteCode = []
        testNum = -1

        code = open(fileName, 'r')

        for line in code:
            if "int tests[" in line:
                testList = line
                suiteCode.append("//TESTLIST")
            elif "void test" in line:
                if testNum == 0:
                    suiteCode.append("//TESTS")

                testNum += 1
                tests.append([])
                tests[testNum].append(line)
            elif "void runner()" in line:
                testNum = -1
                suiteCode.append(line)
            elif testNum == -1:
                suiteCode.append(line)
            elif testNum > -1:
                tests[testNum].append(line)

        code.close()

        self.setTestList(testList)
        self.setTests(tests)
        self.setSuiteCode(suiteCode)

    # Write modified suite to a file
    def writeSuiteFile(self, outFile):
        where = open(outFile, "w")
        for line in self.getSuiteCode():
            if line == "//TESTLIST":
                where.write(self.getTestList())
            elif line == "//TESTS":
                tests = self.getTests()
                for testNum in range(0,len(tests)-1):
                    where.write("".join(tests[testNum]))
            else:
                where.write(line)

        where.close()

    # Getters and setters
    def getTestList(self):
        return self.__testList

    def getTests(self):
        return self.__tests

    def getSuiteCode(self):
        return self.__suiteCode

    def setTestList(self, testList):
        self.__testList = testList

    def setTests(self, tests):
        self.__tests = tests

    def setSuiteCode(self, suiteCode):
        self.__suiteCode = suiteCode

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
