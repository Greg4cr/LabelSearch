# Gregory Gay (greg@greggay.com)
# Central factory that takes in a datatype, and returns a valid instance for that type.
# Returns it in string form, as the result will be inserted into C code.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import random
import string
from SimpleGenerators import *
from StructGenerator import StructGenerator
from UnionGenerator import UnionGenerator

# TODO
# Multidimensional arrays
# Pointers

class GeneratorFactory():
    # Global constants used to bound the range of values generated.
    defaultIntMin = -32767
    defaultIntMax = 32767
    shortIntMin = -32767
    shortIntMax = 32767
    longIntMin = -2147483647
    longIntMax = 2147483647
    longLongIntMin = -9223372036854775807
    longLongIntMax = 9223372036854775807
    unsignedIntMin = 0
    unsignedIntMax = 65535
    unsignedShortMax = 65535
    unsignedLongMax = 4294967295
    unsignedLongLongMax = 18446744073709551615
    defaultCharMin = 0
    defaultCharMax = 255
    signedCharMin = -127
    signedCharMax = 127
    defaultFloatMin = 1.2E-38
    defaultFloatMax = 3.4E+38
    doubleMin = 2.3E-308
    doubleMax = 1.7E+308
    longDoubleMin = 3.4E-4932
    longDoubleMax = 1.1E+4932

    # Information used in generating complex types 
    available = []
    typeDefs = []
    structs = []
    unions = []

    # Generation objects
    ig = IntGenerator()
    fg = FloatGenerator()
    bg = BoolGenerator()
    vg = VoidGenerator()
    ag = AvailableGenerator()
    sg = StructGenerator()
    ug = UnionGenerator()

    def generate(self,typeToGenerate):
        # At a set probability, use an available variable instead of generating a new value.
        if random.random() < 0.25:
            choice = self.ag.generate(self.available,typeToGenerate)
            if choice != "":
                return choice

        if typeToGenerate == "int" or typeToGenerate == "signed int": 
            return self.ig.generate()
        elif typeToGenerate == "short" or typeToGenerate == "short int" or \
            typeToGenerate == "signed short" or typeToGenerate == "signed short int":
            self.ig.minInt = self.shortIntMin
            self.ig.maxInt = self.shortIntMax

            value = self.ig.generate()

            self.ig.minInt = self.defaultIntMin
            self.ig.maxInt = self.defaultIntMax

            return value
        elif typeToGenerate == "unsigned short" or typeToGenerate == "unsigned short int":
            self.ig.minInt = self.unsignedIntMin
            self.ig.maxInt = self.unsignedShortMax

            value = self.ig.generate()

            self.ig.minInt = self.defaultIntMin
            self.ig.maxInt = self.defaultIntMax

            return value
        elif typeToGenerate == "long" or typeToGenerate == "long int" or \
            typeToGenerate == "signed long" or typeToGenerate == "signed long int":
            self.ig.minInt = self.longIntMin
            self.ig.maxInt = self.longIntMax

            value = self.ig.generate()

            self.ig.minInt = self.defaultIntMin
            self.ig.maxInt = self.defaultIntMax

            return value
        elif typeToGenerate == "unsigned long" or typeToGenerate == "unsigned long int":
            self.ig.minInt = self.unsignedIntMin
            self.ig.maxInt = self.unsignedLongMax

            value = self.ig.generate()

            self.ig.minInt = self.defaultIntMin
            self.ig.maxInt = self.defaultIntMax

            return value
        elif typeToGenerate == "long long" or typeToGenerate == "long long int" or \
            typeToGenerate == "signed long long" or typeToGenerate == "signed long long int":
            self.ig.minInt = self.longLongIntMin
            self.ig.maxInt = self.longLongIntMax

            value = self.ig.generate()

            self.ig.minInt = self.defaultIntMin
            self.ig.maxInt = self.defaultIntMax

            return value
        elif typeToGenerate == "unsigned long long" or typeToGenerate == "unsigned long long int":
            self.ig.minInt = self.unsignedIntMin
            self.ig.maxInt = self.unsignedLongLongMax

            value = self.ig.generate()

            self.ig.minInt = self.defaultIntMin
            self.ig.maxInt = self.defaultIntMax

            return value
        elif typeToGenerate == "char" or typeToGenerate == "unsigned char":
            self.ig.minInt = self.defaultCharMin
            self.ig.maxInt = self.defaultCharMax

            value = self.ig.generate()

            self.ig.minInt = self.defaultIntMin
            self.ig.maxInt = self.defaultIntMax

            return value
        elif typeToGenerate == "signed char":
            self.ig.minInt = self.signedCharMin
            self.ig.maxInt = self.signedCharMax
  
            value = self.ig.generate()

            self.ig.minChar = self.defaultIntMin
            self.ig.maxChar = self.defaultIntMax

            return value
        elif typeToGenerate == "float" or typeToGenerate == "float_t":
            # The size of float_t and double_t is compiler dependent.
            # For the sake of safety and test portability, they will be generated as float/double.
            # I.e., FLT_EVAL_METHOD = 0.
            return self.fg.generate()
        elif typeToGenerate == "double" or typeToGenerate == "double_t":
            self.fg.minFloat = self.doubleMin
            self.fg.maxFloat = self.doubleMax

            value = self.fg.generate()

            self.fg.minFloat = self.defaultFloatMin
            self.fg.maxFloat = self.defaultFloatMax
            return value
        elif typeToGenerate == "long double":
            self.fg.minFloat = self.longDoubleMin
            self.fg.maxFloat = self.longDoubleMax

            value = self.fg.generate()

            self.fg.minFloat = self.defaultFloatMin
            self.fg.maxFloat = self.defaultFloatMax
            return value
        elif typeToGenerate == "bool" or typeToGenerate == "_Bool":
            return self.bg.generate()
        elif typeToGenerate == "void" or typeToGenerate == "":
            return self.vg.generate()
        elif "struct " in typeToGenerate:
            structName = typeToGenerate[7:]
            # Look for entry in definitions
            for entry in self.structs:
                if entry[0] == structName:
                    self.sg.structDef = entry
                    return self.sg.generate(self)
            print("We do not have a valid definition for struct: "+structName)
            return "//"+typeToGenerate
        elif "union " in typeToGenerate:
            unionName = typeToGenerate[6:]
            # Look for entry in definitions
            for entry in self.unions:
                if entry[0] == unionName:
                    self.ug.unionDef = entry
                    return self.ug.generate(self)
            print("We do not have a valid definition for union: "+unionName)
            return "//"+typeToGenerate
        else:
            # Check typedefs list
            for entry in self.typeDefs:
                if typeToGenerate == entry[0]:
                    return self.generate(" ".join(entry[1]))
               
            print("We do not current support input generation for type: "+typeToGenerate)
            # Signifies to caller that this type is not supported.
            return "//"+typeToGenerate

