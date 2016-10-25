# Gregory Gay (greg@greggay.com)
# Instrumentation for search-based generation of label-covering tests

# Assumes that the program has already been annotated with labels.
# Label format: pc_label(predicate, identifier,criterion)
# Replaces labels with cost functions, 
# placed in code where they are to be evaluated. 
# Also adds array to contain scores.

# Command line options:
# -p <annotated program>
# -l <labels file, if non-standard name used, default= <program>.labels
# -o <filename of instrumented version, optional, default = <program>_instrumented.c>

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import getopt
import sys
import os
from BinaryTree import *

class Instrumentation(): 

    k = 1

    # Central process of instrumentation
    def instrument(self,program,labelFile,outFile):
        # Get number of obligations
        numObs=self.getNumObs(labelFile)
        
        # Read in C file and add instrumentation
        instrumented=[]
        code=open(program,'r')
        includes=1
        partial="-1"
        for line in code:
            # Insert obligations array as a global variable after all include statements are over. 
            # Also insert the constant used in cost functions.
            if "#includes" not in line and includes==1:
                includes=0
                instrumented.append("float obligations["+str(numObs)+"];")
                instrumented.append("int k = "+self.k+";")
                instrumented.append(line)
            # Replace labels with scores
            if "pc_label(" in line:
                if ");" in line:
                    print "-----"
                    print line
                    print self.replaceLabel(line.strip())
                else:
                    partial=line.strip()
            elif partial != "-1":
                partial=partial+line.strip()
                if ");" in line:
                    print "-----"
                    print partial
                    print self.replaceLabel(partial)
                    partial="-1"
            else:
                instrumented.append(line)
                    
        code.close()
        
        # Print instrumented code to file
        self.writeOutFile(instrumented,outFile)

    # Gets number of obligations from label file
    def getNumObs(self,labelFile):
        labels=open(labelFile, 'r')
        maxNum=0
 
        lNum=0
        for label in labels:
            lNum+=1
            if lNum > 1:
                words=label.strip().split(",")
                if int(words[0]) > maxNum:
                    maxNum=int(words[0])

        labels.close()
        return maxNum

    # Replace label with score calculation
    def replaceLabel(self,label):
        # Split label into parts to extract predicate and identifier
        adjustedLabel=label[label.index("pc_label(")+9:label.index(");")]
        words=adjustedLabel.strip().split(",")
        # Prepare new expression
        newLabel="obligation["+words[1]+"]="

        # Break down predicate into cost function
       # tree=self.buildParseTree(words[0])
       # printTree(tree)

        return newLabel

    # Write results to a CSV file
    def writeOutFile(self,instrumented,outFile):
        where = open(outFile, 'w')
       
        for line in instrumented:
            where.write(line+"\n")

        where.close()
 
    # Set constant used in cost functions
    def setK(self,k):
        self.k = k

def main(argv):
    instrumenter = Instrumentation()
    program = ""
    outFile = ""
    labelFile = ""
    k = 1

    try:
        opts, args = getopt.getopt(argv,"hp:l:o:k:")
    except getopt.GetoptError:
        print 'Instrumentation.py -p <program name> -l <label file> -o <output filename> -k <constant to use for cost functions>'
      	sys.exit(2)
  		
    for opt, arg in opts:
        if opt == "-h":
            print 'Instrumentation.py -p <program name> -l <label file> -o <output filename> -k <constant to use for cost functions>'
            sys.exit()
      	elif opt == "-p":
            if arg == "":
                raise Exception('No program specified')
            else:
                program = arg
        elif opt == "-o":
            outFile = arg
        elif opt == "-l":
            labelFile= arg
        elif opt == "-k":
            k = int(opt)

    if labelFile == "":
        labelFile = program[:program.index(".c")]+".labels"

    if outFile == "":
        outFile = program[:program.index(".c")]+"_instrumented.c"

    if program == '':
        raise Exception('No program specified')
    else:
        instrumenter.setK(k)
	instrumenter.instrument(program,labelFile,outFile)

# Call into main
if __name__ == '__main__':
    main(sys.argv[1:])
