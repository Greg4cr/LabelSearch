# Gregory Gay (greg@greggay.com)
# Input generation for structs

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import random
import string

class StructGenerator():
    structDef = []
    inTypeDefs = 0

    def generate(self, generator):
        # Go through struct definition and build result
        preDefinitions = "//"
        structName = "structInput" + str(int(random.random() * 1000000))
        preDefinitions = preDefinitions + structName + ":"
        if self.inTypeDefs == 1: 
            declaration = "    " + self.structDef[0] + " " + structName +" = {"
        else: 
            declaration = "    struct " + self.structDef[0] + " " + structName +" = {"

        for member in self.structDef[1]:
            if member[1][0] == "var":
                value = generator.generate(" ".join(member[1][1]))
                if "//" in value:
                    return "//struct "+self.structDef[0]

                declaration = declaration + "." + member[0] + " = " + value + ", "           
            elif member[1][0] == "pointer":
                # Currently, same as normal variable.
                # Will expand later
                value = generator.generate(" ".join(member[1][1]))
                if "//" in value:
                    return "//struct "+self.structDef[0]

                declaration = declaration + "." + member[0] + " = " + value + ", "           
            elif "array" in member[1][0]:
                name = "structPreDef" + str(int(random.random() * 1000000))
                typeToGenerate = " ".join(member[1][1])
                size = member[1][0].split(",")[1]
                preDefinitions = preDefinitions + "    " + typeToGenerate + " " + name + "[" + size + "] = {"
                for index in range(0,int(size)):
                    value = generator.generate(typeToGenerate)
                    if "//" in value:
                        return "//struct "+self.structDef[0]

                    preDefinitions = preDefinitions + value + ", "
                preDefinitions = preDefinitions[:len(preDefinitions) - 2]
                preDefinitions = preDefinitions + "};\n"
                   
                declaration = declaration + "." + member[0] + " = " + name + ", "
        declaration = declaration[:len(declaration) - 2]
        declaration = declaration + "};\n"
        declaration = preDefinitions + declaration
        print declaration

        return declaration
