# Gregory Gay (greg@greggay.com)
# Suite generation for search-based generation of label-covering tests

# Command line options:
# -p <instrumented program>
# -o <name of test suite>
# -l <maximum single test length, default is 10 steps (assignments or calls)>
# -m <maximum test suite size, default is 25>

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import getopt
import sys
import os
import random
import copy
from subprocess import call
from pycparser import parse_file, c_parser, c_ast
from DependencyGraph import *
from GeneratorFactory import GeneratorFactory
from Verifier import Verifier
from Runner import Runner
from ..structures.TestSuite import TestSuite

class Generator(): 

    # Program to generate tests for.
    __program = ""
    # List of functions in that program.
    __functions = []
    # List of global (state) variables.
    __stateVariables = []
    # List of type definitions.
    __typeDefs = []
    # List of struct definitions.
    __structs = []
    # List of union definitions.
    __unions = []
    # List of enum definitions.
    __enums = []
    # Dependency map for state information
    __dependencyMap = []
    # Max suite size
    maxSuiteSize = 25.0
    # Max test length
    maxLength = 10.0
    # Max array size when generating input
    maxArraySize = 25
    # Object that verifies that suites compile and do not cause segmentation fault
    verifier = Verifier()
    # Object that runs suites and calculates their score
    runner = Runner()

    # Central process of instrumentation
    def generate(self,outFile):

        if self.getProgram()=="":
            raise Exception("No program set for generation.")

        # Read in program and get list of functions and state variables.
        if self.getFunctions()==[] or self.getStateVariables()==[] or self.getDependencyMap()==[]:
            self.initializeProgramData()

        suite = TestSuite()
        # Generate test cases
        suite.setTests(self.buildSuite())
        testList = []
        for entry in suite.getTests():
            testList.append(1)
        suite.setTestList(testList)
        #print(suite.getTests())

        # Build suite code
        suite.setSuiteCode(self.buildCode(suite,outFile))

        # Print test suite to file
        suite.setFileName(outFile)
        suite.writeSuiteFile()

        # Perform suite verification
        self.verifier.suite = suite
        self.verifier.verify(outFile)
 
        # Run the suite and calculate its score
        self.runner.suite = suite
        self.runner.run()

        return suite

    # Build test suite
    def buildSuite(self):
        suite=[]
        done=0
        generator = GeneratorFactory()
        generator.typeDefs = self.getTypeDefs()
        generator.structs = self.getStructs()
        generator.unions = self.getUnions()

        while done == 0:
            # Use a degrading temperature to control the probability of adding an additional test
            temperature=(self.maxSuiteSize-float(len(suite)))/self.maxSuiteSize
            if random.random() < temperature: 
                chance=random.random()
                numStateful=len(self.getDependencyMap()[0])
                numStateless=len(self.getDependencyMap()[1])
 
                # Add a stateless test if the random number is less than 0.5
                # Or, if there are only stateless funtions 

                # If there are no functions to choose from, throw an exception
                if numStateful == 0 and numStateless == 0:
                    raise Exception("There are no functions to test")  
                # If there are no state-affecting functions, choose a stateless one
                elif numStateful == 0:
                    suite.append(self.buildStatelessTest(generator,str(len(suite)+1)))
                # If there are no stateless functions, choose a stateful one 
                elif numStateless == 0:
                    suite.append(self.buildStatefulTest(generator,str(len(suite)+1)))
                # If there are both, decide based on random number
                else:
                    if chance < 0.5:
                        suite.append(self.buildStatelessTest(generator,str(len(suite)+1)))
                    else:
                        suite.append(self.buildStatefulTest(generator,str(len(suite)+1)))
              
            else:
               done = 1
            
        return suite

    # Build a non-state-affecting test case
    def buildStatelessTest(self,inputGenerator,testID):
        # Choose a function that does not affect global state
        unsupportedType = 0
        index=random.randint(0,len(self.getDependencyMap()[1])-1)
        functionName=self.getDependencyMap()[1][index][0]
                    
        # Find function
        for function in self.getFunctions():
            if function[0] == functionName:
                returnType=" ".join(function[1])
                inputs=function[2]
                break

        test="void test"+testID+"(){\n"
        call="    "

        # If return is not void, assign it to a variable
        if returnType != "void":
            call=call+returnType+" call = "

        call=call+functionName+"("


        # Generate inputs
        createdVars = ""
        for inputChoice in inputs:
            words=inputChoice.strip().split()
            inputName=words[len(words)-1]
            typeToGenerate=" ".join(words[:len(words)-1])
            
            # Is is an array?
            if "[" in inputName:
                size = inputName[inputName.index("[")+1:inputName.index("]")]
                if size == "":
                    size = random.randint(1,self.maxArraySize)
                else:
                    size = int(size)  
                inputNameNoArray=inputName[:inputName.index("[")]
                createdVarName="inputFor"+functionName+inputNameNoArray
                createdVar="    "+typeToGenerate+" "+createdVarName+"["+str(size)+"] = {"
                for entry in range(0,size):
                    value=inputGenerator.generate(typeToGenerate)
                    if "//" in value:
                        if "structInput" in value or "unionInput" in value:
                            toAdd = value.split(":    ")[1]
                            value = value.split(":    ")[0]
                            value = value[2:]
                            createdVars = createdVars + "    " + toAdd 
                        else:
                            value=value[2:]
                            createdVar = "// "+createdVar
                            unsupportedType = 1

                    createdVar=createdVar+value+", "
                createdVar = createdVar[:len(createdVar)-2] + "};\n"
                createdVars = createdVars + createdVar
                call = call + createdVarName+", "
            else:
                value = inputGenerator.generate(typeToGenerate)
                if "//" in value:
                    if "structInput" in value or "unionInput" in value:
                        toAdd = value.split(":    ")[1]
                        value = value.split(":    ")[0]
                        value = value[2:]
                        call = "    " + toAdd + call
                    else:
                        value=value[2:]
                        unsupportedType = 1

                call=call+value+", "

        call = call[:len(call)-2]+");\n"
        if unsupportedType == 1:
            call ="// "+call
        call = createdVars + call

        test=test+call
        test=test+"}\n\n"
            
        return test
 
    # Build a state-impacting test case
    def buildStatefulTest(self,inputGenerator,testID):
        # Test length
        length=0
        # Variables created in the test, available for use as input to other functions
        avail=[]
        inputGenerator.available=avail

        # Get the list of clear global variables
        clearVars=self.buildClearList()
        # Build initial test declaration
        test="void test"+testID+"(){\n    resetStateVariables();\n"

        # Set the length temperature
        ldone=0
        while ldone == 0:
            ltemperature = (self.maxLength-float(length)) / self.maxLength

            # Continue adding steps as long as random < ltemperature
            if random.random() < ltemperature: 
                # Can either make an assignment or call a function
                inputGenerator.available = self.addClearToAvailable(avail,clearVars)
                actionTaken = 0
                makeAssignment = 0
                unsupportedType = 0
                while actionTaken==0:
                    if random.random() < 0.5 or makeAssignment == 1:
                        # Make an assignment
                        call="    "
                        # Choose a state variable
                        index = random.randint(0,len(self.getStateVariables())-1)
                        var = self.getStateVariables()[index]
                        if var[1]=="var":
                            value = inputGenerator.generate(" ".join(var[2]))
                            if "//" in value:
                                if "structInput" in value or "unionInput" in value:
                                    toAdd = value.split(":    ")[1]
                                    value = value.split(":    ")[0]
                                    value = value[2:]
                                    call = "    " + toAdd + call
                                else:
                                    value = value[2:]
                                    unsupportedType=1

                            call = call+var[0]+" = "+value+";\n"
                            if unsupportedType == 1:
                                call = "// " + call

                        elif var[1]=="pointer":
                            # Right now, this is the same as a normal variable. 
                            # In the future, will expand
                            value = inputGenerator.generate(" ".join(var[2]))
                            if "//" in value:
                                if "structInput" in value or "unionInput" in value:
                                    toAdd = value.split(":    ")[1]
                                    value = value.split(":    ")[0]
                                    value = value[2:]
                                    call = "    " + toAdd + call
                                else:
                                    value = value[2:]
                                    unsupportedType=1

                            call=call+var[0]+" = "+value+";\n"
                            if unsupportedType == 1:
                                call = "// " + call

                        elif "array" in var[1]:
                            # If the array is uninit, assign values to whole array
                            # Otherwise, either choose an index or assign values
                            initWhole=random.random()
                            for varInit in clearVars:
                                if varInit[0]==var[0]:
                                    if varInit[1]=="uninit":
                                        initWhole=1
                                        break
                            
                            if initWhole > 0.5:
                                for index in range(0,int(var[1].split(",")[1])):
                                    value = inputGenerator.generate(" ".join(var[2]))
                                    if "//" in value:
                                        if "structInput" in value or "unionInput" in value:
                                            toAdd = value.split(":    ")[1]
                                            value = value.split(":    ")[0]
                                            value = value[2:]
                                            call = "    " + toAdd + call
                                        else:
                                            value = value[2:]
                                            unsupportedType = 1
                                    
                                    if unsupportedType == 1:
                                        call = call + "//" + var[0] + "[" + str(index) + "] = " + value + ";\n    "
                                    else:
                                        call = call + var[0] + "[" + str(index) + "] = " + value + ";\n    "

                                call = call[:len(call)-4]
                            else: 
                                aindex = random.randint(0,int(var[1].split(",")[1])-1)
                                value = inputGenerator.generate(" ".join(var[2]))
                                if "//" in value:
                                    if "structInput" in value or "unionInput" in value:
                                        toAdd = value.split(":    ")[1]
                                        value = value.split(":    ")[0]
                                        value = value[2:]
                                        call = "    " + toAdd + call
                                    else:
                                        value = value[2:]
                                        unsupportedType = 1

                                call = call + var[0] + "[" + str(aindex) + "] = " + value + ";\n"
                        
                                if unsupportedType == 1:
                                    call = "// " + call

                        test=test+call
                        actionTaken=1

                        # Mark as init in clear var list
                        if unsupportedType == 0:
                            for varIndex in range(0,len(clearVars)):
                                if clearVars[varIndex][0]==var[0]:
                                    clearVars[varIndex][1]="init";
                                    break
                    else:
                        # Choose a function that can be used with the current clear list
                        options=[]
                        for index in range(0,len(self.getDependencyMap()[0])):
                            options.append(index)

                        # If no functions can be used, we will make an assignment.
                        while len(options) > 0:
                            index=random.randint(0,len(self.getDependencyMap()[0])-1)
                            if index in options:
                                for identifier in range(0,len(options)):
                                    if options[identifier]==index:
                                        options.remove(index)
                                        break

                                functionName=self.getDependencyMap()[0][index][0]
                            
                                # Check its needs against the clear list
                                allInit=1
                                for entry in self.getDependencyMap()[0][index][1]:
                                    for var in clearVars:
                                        if entry==var[0]:
                                            if var[1]=="uninit":
                                                allInit=0
                                            break
                                    if allInit==0:
                                        break

                                if allInit==1:
                                    # This is a function we can use
                                    
                                    # Find function
                                    for function in self.getFunctions():
                                        if function[0] == functionName:
                                            returnType=" ".join(function[1])
                                            inputs=function[2]
                                            break

                                    call="    "
                                    # If return is not void, assign it to a variable
                                    if returnType != "void":
                                        call=call+returnType+" call"+str(length)+" = "
                                        avail.append(["call"+str(length),returnType])

                                    call=call+functionName+"("
                                    # Generate inputs

                                    createdVars=""

                                    for inputChoice in inputs: 
                                        words=inputChoice.strip().split()
                                        inputName=words[len(words)-1]
                                        typeToGenerate=" ".join(words[:len(words)-1])

                                        # Is is an array?
                                        if "[" in inputName:
                                            size = inputName[inputName.index("[")+1:inputName.index("]")]
                                            if size == "":
                                                size = random.randint(1,self.maxArraySize)
                                            else:
                                                size = int(size)  
                                            inputNameNoArray=inputName[:inputName.index("[")]
                                            createdVarName="inputFor"+functionName+inputNameNoArray+str(length)
                                            createdVar="    "+typeToGenerate+" "+createdVarName+"["+str(size)+"] = {"
                                            for entry in range(0,size):
                                                value = inputGenerator.generate(typeToGenerate)
                                                if "//" in value:
                                                    if "structInput" in value or "unionInput" in value:
                                                        toAdd = value.split(":    ")[1]
                                                        value = value.split(":    ")[0]
                                                        value = value[2:]
                                                        createdVars = createdVars + "    " + toAdd 
                                                    else:
                                                        value = value[2:]
                                                        unsupportedType = 1
                                                        createdVar = "//" + createdVar

                                                createdVar = createdVar + value + ", "

                                            createdVar = createdVar[:len(createdVar)-2]+"};\n"
                                            createdVars = createdVars + createdVar
                                            call = call + createdVarName+", "
                                        else:
                                            value = inputGenerator.generate(typeToGenerate)
                                            if "//" in value:
                                                if "structInput" in value or "unionInput" in value:
                                                    toAdd = value.split(":    ")[1]
                                                    value = value.split(":    ")[0]
                                                    value = value[2:]
                                                    call = "    " + toAdd + call
                                                else:
                                                    value = value[2:]
                                                    unsupportedType = 1

                                            call = call + value + ", "

                                    call = call[:len(call)-2]+");\n"
                                    if unsupportedType == 1:
                                        call = "//" + call

                                    call = createdVars + call
                                    test = test + call

                                    # Update clear list
                                    if unsupportedType == 0:
                                        for provides in self.getDependencyMap()[0][index][2]:
                                            for var in range(0,len(clearVars)):
                                                if clearVars[var][0]==provides:
                                                    clearVars[var][1]="init";
                                                    break

                                    actionTaken=1
                                    break
                            # If no functions can be used, we will make an assignment.
                            makeAssignment=1
                    length+=1
            else:
                ldone=1
        test=test+"}\n\n"
        inputGenerator.available=[]
        return test

    # Append initialized global variables to the available list for generation
    def addClearToAvailable(self,available,clear):
        combined=copy.deepcopy(available)
        for var in clear:
            if var[1] == "init":
                if "[" in var[2]:
                    returnType=var[2].split("[")[0]
                    length=var[2].split("[")[1]
                    length=int(length[:len(length)-1])
                    for index in range(0,length):
                        combined.append([var[0]+"["+str(index)+"]",returnType])
                else:
                    combined.append([var[0],var[2]])

        return combined

    # Build suite code
    def buildCode(self,suite,outFile):
        code=[]
        # Add includes statements
        code.append("#include <stdio.h>\n")
        code.append("#include \""+os.path.basename(self.getProgram())+"\"")

        # Declare test array
        code.append("\n// Array indexing test entries.\n// tests[0] indicates number of tests\n// tests[1] corresponds to test1(), etc.\n")
        code.append("//TESTLIST")

        # Add code for printing to screen/file and resetting obligation scores.

        code.append("\n// Flag for printing obligation scores to a CSV file at the end of execution.\nint print = 1;\n")
        code.append("//FILENAME")
        code.append("\n// Flag for printing obligation scores to the screen at the end of execution.\nint screen = 1;\n\n// Prints obligation scores to the screen\nvoid printScoresToScreen(){\n    printf(\"# Obligation, Score (Unnormalized)\\n\");\n    int obligation;\n    for(obligation=1; obligation<=obligations[0]; obligation++){\n        printf(\"%d, %f\\n\",obligation,obligations[obligation]);\n    }\n}\n\n// Prints obligation scores to a file\nvoid printScoresToFile(){\n    FILE *outFile = fopen(fileName,\"w\");\n    fprintf(outFile, \"# Obligation, Score (Unnormalized)\\n\");\n    int obligation;\n    for(obligation=1; obligation<=obligations[0]; obligation++){\n        fprintf(outFile,\"%d, %f\\n\",obligation,obligations[obligation]);\n    }\n    fclose(outFile);\n}\n\n// Resets obligation scores\nvoid resetObligationScores(){\n    int obligation;\n    for(obligation=1; obligation<=obligations[0]; obligation++){\n        // Set to some high level\n        obligations[obligation] = 1000000.0;\n    }\n}\n")

        # Add state reset
        code.append(self.buildReset())

        code.append("// Test Cases\n")
        code.append("//TESTS")

        # Append test runner and main
        code.append("// Top-level test runner.\nvoid runner(){\n")
        for test in range(1,len(suite.getTestList())+1):
            code.append("    if(tests["+str(test)+"] == 1)\n")
            code.append("        test"+str(test)+"();\n")

        code.append("\n    if(screen == 1)\n        printScoresToScreen();\n    if(print == 1)\n        printScoresToFile();\n}\n\nint main(){\n    runner();\n    return(0);\n}\n")

        return code

    # Take the list of global variables and build a state reset function that can be called by test cases.
    def buildReset(self):
        code="// Resets values of all state values with declared initial values.\nvoid resetStateVariables(){\n"
        for var in self.getStateVariables():
            if var[3] !='':
                # Has an initial value.
                if var[1]=="var" or var[1] =="pointer":
                    code=code+"    "+var[0]+" = "+var[3]+";\n"
                elif var[1]=="array":
                    values=var[3].strip().split(",")
                    for index in range(0,len(values)):
                        code=code+"    "+var[0]+"["+str(index)+"] = "+str(values[index]).strip()+";\n"
        code=code+"}\n\n"

        return code

    # Read in C file and get list of functions and state variables from it.
    def initializeProgramData(self):
        # Parse the program and generate the AST
        ast = parse_file(self.getProgram(), use_cpp=True, cpp_path = "gcc", cpp_args=['-E',r'-Iutils/fake_libc_include'])
        #ast.show()      
 
        # Use the ProgramDataVisitor to build the function, type def, and global variable lists
        pdVisitor = ProgramDataVisitor()
        pdVisitor.visit(ast)
        self.setFunctions(pdVisitor.functions)
        self.setStateVariables(pdVisitor.stateVariables)
        self.setTypeDefs(pdVisitor.typeDefs)
        self.setStructs(pdVisitor.structs)
        self.setUnions(pdVisitor.unions)
        self.setEnums(pdVisitor.enums)
        print self.getFunctions()
        print self.getStateVariables()
        print self.getTypeDefs()
        print self.getStructs()
        print self.getUnions()
        print self.getEnums()
        
        # Use the DependencyMapVisitor to build the dependency map
        dpVisitor = DependencyMapVisitor(self.getFunctions(), self.getStateVariables())
        dpVisitor.visit(ast)
        sequenceMap=dpVisitor.dependencyMap
        print sequenceMap
 
        # Dependency map has two lists - stateful functions and stateless functions
        dependencyMap=[[],[]]
        # SequenceMap is a list of defs and uses in order. Transform this into the dependency map, just a simple
        # list of variables that must be initialized before the function can be called.
        for function in sequenceMap:
            clearList=self.buildClearList()
            dependencyEntry=self.processSequence(clearList, function[0], function[1],sequenceMap)
            # If the uses and provides lists are empty, this is not a state-based function
            if dependencyEntry[1]==[] and dependencyEntry[2]==[]:
                dependencyMap[1].append(dependencyEntry)
            else:
                dependencyMap[0].append(dependencyEntry)

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
            returnType=" ".join(var[2]) 
            if "array" in var[1]:
                returnType=returnType+"["+var[1].split(",")[1]+"]"

            if var[3] =='':
                # No initialized value, so not safe
                clearList.append([var[0],"uninit",returnType])
            else:
                clearList.append([var[0],"init",returnType])
 
        return clearList

    # Setters for global variables
    def setProgram(self,program):
        self.__program = program

    def setFunctions(self,functions):
        self.__functions = functions

    def setStateVariables(self,stateVariables):
        self.__stateVariables = stateVariables

    def setDependencyMap(self,dependencyMap):
        self.__dependencyMap = dependencyMap

    def setTypeDefs(self, typeDefs):
        self.__typeDefs = typeDefs

    def setStructs(self, structs):
        self.__structs = structs

    def setUnions(self, unions):
        self.__unions = unions

    def setEnums(self, enums):
        self.__enums = enums

    # Getters for global variables
    def getProgram(self):
        return self.__program

    def getFunctions(self):
        return self.__functions

    def getStateVariables(self):
        return self.__stateVariables

    def getDependencyMap(self):
        return self.__dependencyMap

    def getTypeDefs(self):
        return self.__typeDefs

    def getStructs(self):
        return self.__structs

    def getUnions(self):
        return self.__unions

    def getEnums(self):
        return self.__enums

def main(argv):
    generator = Generator()
    program = ""
    outFile = ""
    maxSuiteSize = 25.0
    maxLength = 10.0

    try:
        opts, args = getopt.getopt(argv,"hp:o:l:m:")
    except getopt.GetoptError:
        print 'Generator.py -p <program name> -o <output filename> -l <max individual test length> -m <max suite size>'
      	sys.exit(2)
  		
    for opt, arg in opts:
        if opt == "-h":
            print 'Generator.py -p <program name> -o <output filename> -l <max individual test length> -m <max suite size>'
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

    if program == '':
        raise Exception('No program specified')
    else:
        if outFile == "":
            outFile = program[:program.index(".c")]+"_suite.c"

        generator.maxSuiteSize=maxSuiteSize
        generator.maxLength=maxLength
        generator.setProgram(program)
	suite = generator.generate(outFile)

# Call into main
if __name__ == '__main__':
    main(sys.argv[1:])
