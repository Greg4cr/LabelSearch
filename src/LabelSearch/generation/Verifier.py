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
import copy

class Verifier(): 
    # Test suite, in processable form
    suite = TestSuite()
    
    # Imports a suite from a file and performs verification
    def verifyImport(self,fileName,outFile):
        # Get suite code in an easy-to-process form
        self.suite.setFileName(fileName)
        self.suite.importSuite()
     
        # Perform verification
        self.verify(outFile) 

    # Performs verification on a suite already in-memory
    def verify(self, outFile):
        badTests = []
        # Compile and attempt to run the suite.
        (output, error) = self.compileSuite(self.suite.getFileName())

        if outFile != self.suite.getFileName():
            self.suite.setFileName(outFile)

        # If an executable is produced, compilation succeeded.                    
        if "Segmentation fault" in error:
            #print error
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

            for testNum in range(0,len(self.suite.getTests())):
                # Turn one one test, try to run suite. 
                # If it seg-faults, then turn off that test.
                testList = self.suite.getTestList()
                testList[testNum] = 1
                self.suite.setTestList(testList)
                #print self.suite.getTestList()
                self.suite.writeSuiteFile()
                (output, error) = self.compileSuite(outFile)
                if error != "":
                    #print error
                    testList = self.suite.getTestList()
                    badTests.append(testNum)
                    testList[testNum] = 0
                    self.suite.setTestList(testList)

            # Try to run it one last time
            self.suite.writeSuiteFile()
            (output, error) = self.compileSuite(outFile)
            if error != "":
                raise Exception("Unable to verify.")
            else:
                # Remove bad tests
                print "Separating failing tests: "+str(badTests)
                self.removeBadTests(badTests) 
        else:
            # Print test suite to file
            self.suite.writeSuiteFile()

    # Separate bad tests from suite
    def removeBadTests(self, badTests):
        # Create failing tests directory
        path = os.path.dirname(self.suite.getFileName())+"/failing_tests/"
        if not os.path.isdir(path):
            os.makedirs(path)

        # Create test suite
        failingSuite = TestSuite()
        failingSuite.setFileName(path+"seg_fault.c")

        if os.path.exists(path+"seg_fault.c"):
            # Import existing failing tests
            failingSuite.importSuite()

        fTestList = copy.deepcopy(failingSuite.getTestList())
        fTests = copy.deepcopy(failingSuite.getTests())
        gTests = copy.deepcopy(self.suite.getTests())
        gTestList = copy.deepcopy(self.suite.getTestList())

        for entry in range(0,len(badTests)):
            fTestList.append(0)
            fTests.append(gTests[badTests[entry]-entry])
            del gTests[badTests[entry]-entry]
            gTestList.remove(0)

        # Fix test numbering
        for entry in range(1,len(fTests)+1):
            test = fTests[entry-1]
            num = test.strip().split("test")[1]
            num = num[:num.index("(")]
            if int(num) != entry:
                fTests[entry-1] = test.replace("test"+num,"test"+str(entry))

        for entry in range(1,len(gTests)+1):
            test = gTests[entry-1]
            num = test.strip().split("test")[1]
            num = num[:num.index("(")]
            if int(num) != entry:
                gTests[entry-1] = test.replace("test"+num,"test"+str(entry))

        # Fix test runner for existing suite

        self.suite.setTestList(gTestList)
        self.suite.setTests(gTests)
        gCode = copy.deepcopy(self.suite.getSuiteCode())

        # Suite code, line 11, is where the runner starts
        # After that, there are two lines per test
        deleted = 0
        for line in range(11,len(gCode)-1,2):
            num = gCode[line-deleted][gCode[line-deleted].index("[")+1:gCode[line-deleted].index("]")]
            if int(num) > len(gTestList):
                del gCode[line-deleted]
                del gCode[line-deleted]
                deleted+=2
        self.suite.setSuiteCode(gCode)

        # Create suite code for failing tests
       
        failingSuite.setTestList(fTestList) 
        failingSuite.setTests(fTests) 
        fCode = copy.deepcopy(gCode)
        if len(fTestList) < len(gTestList):
            # If the "good" test list is longer than bad, remove entries from the runner
            deleted = 0
            for line in range(11,len(fCode)-1,2):
                num = fCode[line-deleted][fCode[line-deleted].index("[")+1:fCode[line-deleted].index("]")]
                if int(num) > len(fTestList):
                    del fCode[line-deleted]
                    del fCode[line-deleted]
                    deleted+=2
        elif len(fTestList) > len(gTestList):
            # If the "bad" list is longer, add entries to the runner
            lastLine = fCode[len(fCode)-1]
            lastTest = fCode[len(fCode)-2]
            
            if "runner" not in lastTest:
                lastTest = lastTest.split("test")[1]
                lastTest = int(lastTest[:lastTest.index("(")])
            else:
                lastTest = 0


            del fCode[len(fCode)-1]
            for entry in range(lastTest + 1,len(fTestList)):
                fCode.append("    if(tests[" + str(entry) + "] == 1)\n")
                fCode.append("        test" + str(entry) + "();\n")

            fCode.append(lastLine)     

        failingSuite.setSuiteCode(fCode)
        failingSuite.writeSuiteFile()

    # Compiles and runs suite
    def compileSuite(self, fileName):
        if os.path.isfile(fileName):
            path = os.path.dirname(fileName)
            rmProcess = Popen("rm a.out", stdout = PIPE, stderr = PIPE, shell = True)
            (rOutput, eError) = rmProcess.communicate()
            compileProcess = Popen("gcc " + fileName, stdout = PIPE, stderr = PIPE, shell=True)
            (cOutput, cError) = compileProcess.communicate()
            
            if os.path.isfile("a.out"):
                # Does it execute without segmentation faults?
                process = Popen("./a.out", stdout = PIPE, stderr = PIPE, shell=True)
                (output, error) = process.communicate()
                call("rm a.out", shell=True)
                return (output, error)
            else:
                raise Exception("Suite failed to compile: " + cError)
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
        verifier.verifyImport(fileName,outFile)

# Call into main
if __name__ == '__main__':
    main(sys.argv[1:])
