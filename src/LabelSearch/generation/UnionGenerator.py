# Gregory Gay (greg@greggay.com)
# Input generation for unions
# Almost the same as structs, but unions are intended to only have one value available at once.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import random
import string

class UnionGenerator():
    unionDef = []
    inTypeDefs = 0

    def generate(self, generator):
        # Go through union definition and build result
        preDefinitions = "//"
        unionName = "unionInput" + str(int(random.random() * 1000000))
        preDefinitions = preDefinitions + unionName + ":"
        if self.inTypeDefs == 1: 
            declaration = "    " + self.unionDef[0] + " " + unionName +" = {"
        else: 
            declaration = "    union " + self.unionDef[0] + " " + unionName +" = {"

        # Choose a random member
        member = random.choice(self.unionDef[1])

        if member[1][0] == "var":
            value = generator.generate(" ".join(member[1][1]))
            if "//" in value:
                return "//union "+self.unionDef[0]

            declaration = declaration + "." + member[0] + " = " + value
        elif member[1][0] == "pointer":
            # Currently, same as normal variable.
            # Will expand later
            value = generator.generate(" ".join(member[1][1]))
            if "//" in value:
                return "//union "+self.unionDef[0]

            declaration = declaration + "." + member[0] + " = " + value      
        elif "array" in member[1][0]:
            varNum = str(int(random.random() * 1000000))
            if varNum in preDefinitions:
                done = 0
                while done == 0:
                    varNum = str(int(random.random() * 1000000))
                    if varNum not in preDefinitions:
                        done = 1

            name = "unionPreDef" + varNum 
            typeToGenerate = " ".join(member[1][1])
            size = member[1][0].split(",")[1]
            preDefinitions = preDefinitions + "    " + typeToGenerate + " " + name + "[" + size + "] = {"
            for index in range(0,int(size)):
                value = generator.generate(typeToGenerate)
                if "//" in value:
                    return "//union "+self.unionDef[0]

                preDefinitions = preDefinitions + value + ", "

            preDefinitions = preDefinitions[:len(preDefinitions) - 2]
            preDefinitions = preDefinitions + "};\n"       
            declaration = declaration + "." + member[0] + " = " + name

        declaration = declaration + "};\n"
        declaration = preDefinitions + declaration
        #print declaration

        return declaration
