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

class Generator(): 

    # Central process of instrumentation
    def generate(self,program,outFile):

        # Read in program and get list of functions.
        functions=self.getListOfFunctions(program)

        # Generate test cases
        tests=[]
        # Pass in function list
        # For each unit test, call functions from list, decide whether to add additional method calls

        # Build suite code
        suite=self.buildSuite(program,tests,outFile)
 
        # Print test suite to file
        self.writeOutFile(suite,outFile)

    # Build suite code
    def buildSuite(self,program,tests,outFile):
        suite=[]
        # Add includes statements
        suite.append("#include <stdio.h>")
        suite.append("#include \""+program+"\"")

        # Declare test array
        suite.append("\n// Array indexing test entries.\n// tests[0] indicates number of tests\n// tests[1] corresponds to test1(), etc.")
	testDecl="int tests["+str(len(tests)+1)+"]={"+str(len(tests))
        for test in range(0,len(tests)):
            testDecl+=",1"
        suite.append(testDecl+"};")

        # Add code for printing to screen/file

        suite.append("\n// Flag for printing obligation scores to a CSV file at the end of execution.\nint print = 1;\nchar* fileName = \""+outFile+"sv\";\n\n// Flag for printing obligation scores to the screen at the end of execution.\nint screen = 1;\n\n// Prints obligation scores to the screen\nvoid printScoresToScreen(){\n    printf(\"# Obligation, Score (Unnormalized)\\n\");\n    int obligation;\n    for(obligation=1; obligation<=obligations[0]; obligation++){\n        printf(\"%d, %f\\n\",obligation,obligations[obligation]);\n    }\n}\n\n// Prints obligation scores to a file\nvoid printScoresToFile(){\n    FILE *outFile = fopen(fileName,\"w\");\n    fprintf(outFile, \"# Obligation, Score (Unnormalized)\\n\");\n    int obligation;\n    for(obligation=1; obligation<=obligations[0]; obligation++){\n        fprintf(outFile,\"%d, %f\\n\",obligation,obligations[obligation]);\n    }\n    fclose(outFile);\n}\n\n// Test Cases")

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

    # Read in C file and get list of functions from it.
    def getListOfFunctions(self,program):
        code=open(program,'r')
        functions=[]
        
        # Two recognition rules
        # 1: At bracket depth = 0
        # 2: Has parameters (at least parentheses for them)
        depth=0
        for line in code:
            if depth == 0:
                if "(" in line:
                    words=line.strip().split(" ")
                    declaration=words[0]+","+words[1].replace(";","")
                    declaration=declaration[:declaration.index("(")]+","+declaration[declaration.index("("):]
                    if declaration not in functions:
                        functions.append(declaration)

            if "{" in line:
                depth+=1

            if "}" in line:
                depth-=1
                
        code.close()
        return functions

    # Write instrumented program to a file
    def writeOutFile(self,suite,outFile):
        where = open(outFile, 'w')
       
        for line in suite:
            where.write(line+"\n")

        where.close()

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
	generator.generate(program,outFile)

# Call into main
if __name__ == '__main__':
    main(sys.argv[1:])
