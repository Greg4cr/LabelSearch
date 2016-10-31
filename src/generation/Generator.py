# Gregory Gay (greg@greggay.com)
# Suite generation for search-based generation of label-covering tests

# Command line options:
# -p <instrumented program>
# -o <name of test suite>

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import getopt
import sys
import os
from pycparser import parse_file, c_parser, c_ast
from DependencyGraph import *

class Generator(): 

    # Program to generate tests for.
    __program=""
    # List of functions in that program.
    __functions=[]
    # List of global (state) variables.
    __stateVariables=[]
    # Dependency map for state information
    __dependencyMap=[]

    # Central process of instrumentation
    def generate(self,outFile):

        if self.getProgram()=="":
            raise Exception("No program set for generation.")

        # Read in program and get list of functions and state variables.
        if self.getFunctions()==[] or self.getStateVariables()==[] or self.getDependencyMap()==[]:
            self.initializeProgramData()

        # Generate test cases
        tests=[]
        # Pass in function list
        # For each unit test, call functions from list, decide whether to add additional method calls

        # Build suite code
        suite=self.buildSuite(tests,outFile)
 
        # Print test suite to file
        self.writeOutFile(suite,outFile)

    # Build suite code
    def buildSuite(self,tests,outFile):
        suite=[]
        # Add includes statements
        suite.append("#include <stdio.h>")
        suite.append("#include \""+self.getProgram()+"\"")

        # Declare test array
        suite.append("\n// Array indexing test entries.\n// tests[0] indicates number of tests\n// tests[1] corresponds to test1(), etc.")
	testDecl="int tests["+str(len(tests)+1)+"]={"+str(len(tests))
        for test in range(0,len(tests)):
            testDecl+=",1"
        suite.append(testDecl+"};")

        # Add code for printing to screen/file and resetting obligation scores.

        suite.append("\n// Flag for printing obligation scores to a CSV file at the end of execution.\nint print = 1;\nchar* fileName = \""+outFile+"sv\";\n\n// Flag for printing obligation scores to the screen at the end of execution.\nint screen = 1;\n\n// Prints obligation scores to the screen\nvoid printScoresToScreen(){\n    printf(\"# Obligation, Score (Unnormalized)\\n\");\n    int obligation;\n    for(obligation=1; obligation<=obligations[0]; obligation++){\n        printf(\"%d, %f\\n\",obligation,obligations[obligation]);\n    }\n}\n\n// Prints obligation scores to a file\nvoid printScoresToFile(){\n    FILE *outFile = fopen(fileName,\"w\");\n    fprintf(outFile, \"# Obligation, Score (Unnormalized)\\n\");\n    int obligation;\n    for(obligation=1; obligation<=obligations[0]; obligation++){\n        fprintf(outFile,\"%d, %f\\n\",obligation,obligations[obligation]);\n    }\n    fclose(outFile);\n}\n\n// Resets obligation scores\nvoid resetObligationScores(){\n    int obligation;\n    for(obligation=1; obligation<=obligations[0]; obligation++){\n        // Set to some high level\n        obligations[obligation] = 1000000.0;\n    }\n}\n")

        suite.append("// Test Cases\n")

	# Append test case code
        for test in range(0,len(tests)):
            suite.append(tests[test])

        # Append test runner and main
        suite.append("// Top-level test runner.\nvoid runner(){\n")
        for test in range(0,len(tests)):
            suite.append("    if(tests["+str(test)+"] == 1)")
            suite.append("        test"+test+"();")

        suite.append("\n    if(screen == 1)\n        printScoresToScreen();\n    if(print == 1)\n        printScoresToFile();\n}\n\nint main(){\n    runner();\n    return(0);\n}\n")

        return suite

    # Read in C file and get list of functions and state variables from it.
    def initializeProgramData(self):
        # Parse the program and generate the AST
        ast = parse_file(self.getProgram(), use_cpp=True)
        #ast.show()      
 
        # Use the ProgramDataVisitor to build the function and global variable lists
        pdVisitor = ProgramDataVisitor()
        pdVisitor.visit(ast)
        self.setFunctions(pdVisitor.functions)
        self.setStateVariables(pdVisitor.stateVariables)
        print self.getFunctions()
        print self.getStateVariables()
        
        # Use the DependencyMapVisitor to build the dependency map
        dpVisitor = DependencyMapVisitor(self.getFunctions(), self.getStateVariables())
        dpVisitor.visit(ast)
        sequenceMap=dpVisitor.dependencyMap
        print sequenceMap
 
        dependencyMap=[]
        # SequenceMap is a list of defs and uses in order. Transform this into the dependency map, just a simple
        # list of variables that must be initialized before the function can be called.
        for function in sequenceMap:
            clearList=self.buildClearList()
            dependencyMap.append(self.processSequence(clearList, function[0], function[1],sequenceMap))

        self.setDependencyMap(dependencyMap)
        print self.getDependencyMap()

    # Process sequence and return a dependency list
    def processSequence(self, clearList, function, sequence, sequenceMap):
        dependencyEntry=[function,[],[]]
        seen=[function]
        # Go through each interaction.
        seqLen=len(sequence)
        interaction=0
        while interaction < seqLen:
            # If we've seen it already, skip it
            if sequence[interaction][0] not in dependencyEntry[1] or sequence[interaction][0] not in dependencyEntry[2]:
                # It will either be a def, a use, or a function call
                if sequence[interaction][1] == "def":
                    # Mark it as init
                    for entry in range(0,len(clearList)):
                        if clearList[entry][0] == sequence[interaction][0]:
                            clearList[entry] = [clearList[entry][0],"init"]
                            if sequence[interaction][0] not in dependencyEntry[2]:
                                dependencyEntry[2].append(sequence[interaction][0])
                            break
                elif sequence[interaction][1] == "use":
                    # If the variable is uninit, then we depend on it being initialized by another function first.
                    for entry in clearList:
                        if entry[0] == sequence[interaction][0]:
                            if entry[1] == "uninit":
                                if sequence[interaction][0] not in dependencyEntry[1]:
                                    dependencyEntry[1].append(sequence[interaction][0])
                            break
                elif sequence[interaction][1] == "function":
                    # If a function is called, put in its interactions and process them.
                    # Only append a function once - if a variable is uninitialized the first time, it doesn't matter if we call it again.
                    if sequence[interaction][0] not in seen:
                        seen.append(sequence[interaction][0])
                        for toInline in sequenceMap:
                            if toInline[0] == sequence[interaction][0]:
                                # Add interactions to the list
                                for line in range(0,len(toInline[1])):
                                    sequence.insert(interaction+line+1,toInline[1][line])
                                seqLen = len(sequence)
                                break
            
            interaction+=1

        return dependencyEntry

    # Build the clear list - a list of global variables that are safe to use.
    def buildClearList(self):
        clearList=[]
        for var in self.getStateVariables():
            if var[3] =='':
                # No initialized value, so not safe
                clearList.append([var[0],"uninit"])
            else:
                clearList.append([var[0],"init"])
 
        return clearList

    # Write instrumented program to a file
    def writeOutFile(self,suite,outFile):
        where = open(outFile, 'w')
       
        for line in suite:
            where.write(line+"\n")

        where.close()

    # Setters for global variables
    def setProgram(self,program):
        self.__program=program

    def setFunctions(self,functions):
        self.__functions=functions

    def setStateVariables(self,stateVariables):
        self.__stateVariables=stateVariables

    def setDependencyMap(self,dependencyMap):
        self.__dependencyMap=dependencyMap

    # Getters for global variables
    def getProgram(self):
        return self.__program

    def getFunctions(self):
        return self.__functions

    def getStateVariables(self):
        return self.__stateVariables

    def getDependencyMap(self):
        return self.__dependencyMap

def main(argv):
    generator = Generator()
    program = ""
    outFile = ""

    try:
        opts, args = getopt.getopt(argv,"hp:o:")
    except getopt.GetoptError:
        print 'Generator.py -p <program name> -o <output filename>'
      	sys.exit(2)
  		
    for opt, arg in opts:
        if opt == "-h":
            print 'Generator.py -p <program name> -o <output filename>'
            sys.exit()
      	elif opt == "-p":
            if arg == "":
                raise Exception('No program specified')
            else:
                program = arg
        elif opt == "-o":
            outFile = arg

    if outFile == "":
        outFile = program[:program.index(".c")]+"_suite.c"

    if program == '':
        raise Exception('No program specified')
    else:
        generator.setProgram(program)
	generator.generate(outFile)

# Call into main
if __name__ == '__main__':
    main(sys.argv[1:])
