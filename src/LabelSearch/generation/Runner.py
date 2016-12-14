# Gregory Gay (greg@greggay.com)
# Executes the test suite and updates the obligation scores.

# Command line options:
# -s <test suite filename>

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import getopt
import sys
import os
from subprocess import Popen, call, PIPE, STDOUT
from ..structures.TestSuite import TestSuite
from Verifier import Verifier

class Runner(): 
    # Test suite, in processable form
    suite = TestSuite()

    # Imports a suite from a file and executes it
    def runImport(self,fileName):
        # Get suite code in an easy-to-process form
        self.suite.setFileName(fileName)
        self.suite.importSuite()
     
        # Perform verification
        self.run() 

    # Execute a suite already in-memory
    def run(self):
        # Compile and attempt to run the suite.
        (output, error) = self.compileSuite()

        # If an executable is produced, compilation succeeded.                    
        if "Segmentation fault" in error:
            # If there is a segmentation fault, perform verification and re-run.
            #print error
            print "Performing Verification"
            
            verifier = Verifier()
            verifier.suite = self.suite
            verifier.verify(self.suite.getFileName())
            print "Attempting to rerun."
            self.suite.importSuite()
            self.run()  
        else:
            # If it ran sucessfully, import the obligation scores and recalculate the suite score.
            self.suite.importObligations(os.path.basename(self.suite.getFileName()) + "sv")
            rmProcess = Popen("rm "+os.path.basename(self.suite.getFileName()) + "sv", stdout = PIPE, stderr = PIPE, shell = True)
            (rOutput, eError) = rmProcess.communicate()

            #print self.suite.getObligations()
            #print self.suite.getScore()

    # Compiles and runs suite
    def compileSuite(self):
        fileName = self.suite.getFileName()
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
    runner = Runner()
    fileName = ""

    try:
        opts, args = getopt.getopt(argv,"hs:")
    except getopt.GetoptError:
        print 'Runner.py -s <test suite filename>'
      	sys.exit(2)
  		
    for opt, arg in opts:
        if opt == "-h":
            print 'Runner.py -s <test suite filename>'
            sys.exit()
      	elif opt == "-s":
            if arg == "":
                raise Exception('No filename specified')
            else:
               fileName = arg

    if fileName == "":
        raise Exception('No suite filename specified')
    else:
        runner.runImport(fileName)

# Call into main
if __name__ == '__main__':
    main(sys.argv[1:])
