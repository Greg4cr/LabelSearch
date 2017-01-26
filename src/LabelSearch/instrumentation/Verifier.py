# Gregory Gay (greg@greggay.com)
# Verify obligations to ensure that they compile. 
# If they do not, comment them out and replace with dummy score.

# Command line options:
# -s <program filename>
# -o <output filename, if different from suite filename>

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import getopt
import sys
import os
from subprocess import Popen, call, PIPE, STDOUT

class Verifier(): 

    # Text of instrumented program
    program = []

    # Imports the instrumented program
    def importProgram(self,fileName):
        code = open(fileName, "r")

        for line in code:
            self.program.append(line)

        code.close()

    # Write the program to a file
    def writeProgram(self,outFile):
        where = open(outFile, "w")

        for line in self.program:
            where.write(line)
 
        where.close()

    # Identify the obligations to fix
    def getObligationList(self, errorMessage):
        obligations = []
        # Get each line with the word error in it.
        lines = errorMessage.split("error:")
        for line in lines:
            words = line.split(" ")
            for word in words:
                # Look for the obligation expression
                if "obligation" in word and "=" in word:
                    parts = word.split("=")
                    if parts[0] not in obligations:
                        obligations.append(parts[0])

        return obligations

    # Fix obligations in program
    def fixObligations(self, obligations):
        for entry in range(0,len(self.program)):
            if "obligations[" in self.program[entry]:
                words = self.program[entry].split("=")
                if words[0] in obligations:
                    self.program[entry] = "// Removed as non-compiling\n" + "// " + self.program[entry] + words[0] + " = 1000000;\n"

    # Performs verification on a suite already in-memory
    def verify(self, fileName, outFile):
        self.importProgram(fileName)

        # Compile and attempt to run the suite.
        (output, error) = self.compileProgram(outFile)

        while error != "" and "error:" in error:
            if "obligations" in error:
                print "Compilation error - attempting to fix obligations"
                obligations = self.getObligationList(error)
                print obligations
                self.fixObligations(obligations)
                (output, error) = self.compileProgram(outFile)
            else:
                print "Compilation error due to non-obligation issue:\n" + error
                error = ""

    # Compiles and runs suite
    def compileProgram(self, fileName):
        self.writeProgram(fileName)

        if os.path.isfile(fileName):
            path = os.path.dirname(fileName)
            compileProcess = Popen("gcc " + fileName + " -lm", stdout = PIPE, stderr = PIPE, shell=True)
            (cOutput, cError) = compileProcess.communicate()
            rmProcess = Popen("rm a.out", stdout = PIPE, stderr = PIPE, shell = True)
            (rOutput, eError) = rmProcess.communicate()
            return (cOutput, cError)        
        else:
            raise Exception("The program file does not exist.")

def main(argv):
    verifier = Verifier()
    fileName = ""
    outFile = ""

    try:
        opts, args = getopt.getopt(argv,"hs:o:")
    except getopt.GetoptError:
        print 'Verifier.py -s <program filename> -o <output filename>'
      	sys.exit(2)
  		
    for opt, arg in opts:
        if opt == "-h":
            print 'Verifier.py -s <program filename> -o <output filename>'
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
