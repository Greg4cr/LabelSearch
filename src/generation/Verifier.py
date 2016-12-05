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
      
        # Compile and attempt to run the suite.
        (output, error) = self.compileSuite(fileName)

        # If an executable is produced, compilation succeeded.                    
        if "Segmentation fault" in error:
            print error
            print "Attempting to find source(s) of segmentation faults"
           
            # Turn off all tests
            # This step is repeated twice because of overlapping substrings.
            self.setTestList(self.getTestList().replace(",1,",",0,"))
            self.setTestList(self.getTestList().replace(",1,",",0,"))
            self.setTestList(self.getTestList().replace(",1}",",0}"))

            # See if code runs with no tests enabled
            self.writeSuiteFile(outFile)
            (output, error) = self.compileSuite(outFile)
            if error != "":
                raise Exception("Issue with test execution code, not test suite.")

            for testNum in range(1,len(self.getTests()) + 1):
                # Turn one one test, try to run suite. 
                # If it seg-faults, then turn off that test.
                parts = self.getTestList().split(",")
                testList = parts[0]+","
                #print testNum
                for index in range(1,testNum):
                    testList = testList + parts[index] + ","

                if testNum == len(self.getTests()):
                    testList = testList + "1};\n"
                else:
                    testList = testList + "1,"

                for index in range(testNum+1,len(parts)):
                    testList = testList + parts[index] + ","                
           
                if testList[len(testList) - 1:] == ",":
                    testList = testList[:len(testList) - 1]
 
                self.setTestList(testList)
                #print self.getTestList()
                 
                self.writeSuiteFile(outFile)
                (output, error) = self.compileSuite(outFile)
                if error != "":
                    #print error
                    self.setTestList(",0,".join(self.getTestList().rsplit(",1,",1)))
        else:
            # Print test suite to file
            self.writeSuiteFile(outFile)

    # Compiles and runs suite
    def compileSuite(self, fileName):
        call("rm a.out", shell=True)
        call("gcc "+fileName, shell=True)

        if os.path.isfile("a.out"):
            # Does it execute without segmentation faults?
            process = Popen("./a.out", stdout=PIPE, stderr=PIPE, shell=True)
            (output, error) = process.communicate()
            return (output, error)
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
                for testNum in range(0,len(tests)):
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
