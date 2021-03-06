# Gregory Gay (greg@greggay.com)
# Data structure representing a test suite.
# Consists of a test list, test code, suite code, and obligation scores.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import sys
import os

class TestSuite(): 
    # Overall suite structure. Contains place-markers for tests and the test list.
    __suiteCode = []
    # List of tests. Value of 1 means that the test is "turned on" - i.e., we are allowed to execute it.
    # Value of 0 means that the runner will not execute it.
    __testList = []
    # Test code, corresponds to entries in the test list.
    __tests = []
    # Obligation scores
    __obligations = []
    # Current score of the suite.
    __score = 1000000000
    # File name
    __fileName = "suite.c"
    # Normalizing constant used in score calculation
    __normConst = 1.0

    # Read in suite file and populate non-score data members
    def importSuite(self):
        testList = []
        tests = []
        suiteCode = []
        testNum = -1

        code = open(self.getFileName(), 'r')

        for line in code:
            if "int tests[" in line:
                parts = line.strip().split(",")
                for testIndex in range(0,len(parts)):
                    toAppend = parts[testIndex]
                    if "{" in toAppend:
                        toAppend = toAppend[toAppend.index("{")+1:]
                    if "}" in toAppend:
                        toAppend = toAppend[:toAppend.index("}")]

                    testList.append(int(toAppend))

                del testList[0]                
                suiteCode.append("//TESTLIST")
            elif "void test" in line:
                if testNum == 0:
                    suiteCode.append("//TESTS")

                testNum += 1
                tests.append("")
                tests[testNum] += line
            elif "void runner()" in line:
                prevComment = tests[testNum][tests[testNum].index("//"):]
                tests[testNum] = tests[testNum][:tests[testNum].index("//")]
                testNum = -1
                suiteCode.append(prevComment)
                suiteCode.append(line)
            elif testNum == -1:
                suiteCode.append(line)
            elif testNum > -1:
                tests[testNum] += line

        code.close()

        self.setTestList(testList)
        self.setTests(tests)
        self.setSuiteCode(suiteCode)

    # Write modified suite to a file
    def writeSuiteFile(self):
        where = open(self.getFileName(), "w")
        for line in self.getSuiteCode():
            if line == "//TESTLIST":
                tests = self.getTestList()
                out = "int tests[" + str(len(tests) + 1) + "] = {" + str(len(tests)) + ", "
                for testIndex in range(0, len(tests)):
                    out = out + str(tests[testIndex]) + ", "
                out = out[:len(out)-2] + "};\n"
                where.write(out)
            elif line == "//TESTS":
                tests = self.getTests()
                for testNum in range(0,len(tests)):
                    where.write(tests[testNum])
            elif line == "//FILENAME":
                out = "char* fileName = \"" + os.path.basename(self.getFileName()) + "sv\";\n"
                where.write(out)
            else:
                where.write(line)

        where.close()

    # Import obligations from file and calculate the overall score
    def importObligations(self, fileName):
        obFile = open(fileName, "r")
        obligations = []
        for line in obFile:
            if "# Obligation" in line:
                obligations.append(0)
            else:
                words = line.strip().split(",")
                obligations.append(float(words[1]))
                obligations[0] += 1

        obFile.close()
        self.setObligations(obligations)
        self.calculateScore()

    # Calculate the suite score
    def calculateScore(self):
        score = 0.0
        obligations = self.getObligations()
        for testIndex in range(1,obligations[0]+1):
            if obligations[testIndex] == 1000000.0:
                score += 1.0
            elif obligations[testIndex] > 0:
                score += (obligations[testIndex] / (obligations[testIndex] + self.getNormalizingConstant()))

        self.setScore(score)

    # Getters and setters
    def getTestList(self):
        return self.__testList

    def getTests(self):
        return self.__tests

    def getSuiteCode(self):
        return self.__suiteCode

    def getFileName(self):
        return self.__fileName

    def getObligations(self):
        return self.__obligations
 
    def getScore(self):
        return self.__score

    def getNormalizingConstant(self):
        return self.__normConst

    def setTestList(self, testList):
        self.__testList = testList

    def setTests(self, tests):
        self.__tests = tests

    def setSuiteCode(self, suiteCode):
        self.__suiteCode = suiteCode

    def setScore(self, score):
        self.__score = score

    def setObligations(self, obligations):
        self.__obligations = obligations

    def setFileName(self, fileName):
        self.__fileName = fileName

    def setNormalizingConstant(self, normConst):
        self.__normConst = normConst

# Call into main
if __name__ == '__main__':
    main(sys.argv[1:])
