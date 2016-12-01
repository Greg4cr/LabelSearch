import random
import string

# Simple integer generator.
class IntGenerator():
    minInt = -32767
    maxInt = 32767

    def generate(self):
        return str(random.randint(self.minInt,self.maxInt))

# Simple character generator.
class CharGenerator():
    minChar = 0
    maxChar = 255

    def generate(self):
        numRepresentation=random.randint(self.minChar,self.maxChar)
        #charRepresentation=chr(numRepresentation)
        return str(numRepresentation)

# Simple floating-point generator.
class FloatGenerator():
    minFloat = -3.4E+38
    maxFloat = 3.4E+38
   
    def generate(self):
        return str(random.uniform(self.minFloat,self.maxFloat))

# Returns an empty string for void (no argument) input
class VoidGenerator():
    def generate(self):
        return ""

# Returns a random variable of the correct datatype from a list of available variables
class AvailableGenerator():
    def generate(self, available, typeToReturn):
        if len(available) > 0:
            # Build set of options
            options=[]
            for option in available:
                if option[1] == typeToReturn: 
                    options.append(option)
                
            # Choose one from that set
            if len(options) > 0:
                return options[random.randint(0,len(options)-1)][0]
            else:
                return ""
        else:
            return ""

# Takes in a datatype, and returns a valid instance for that type.
# Returns it in string form, as the result will be inserted into C code.
class GeneratorFactory():
    available = []
    ig = IntGenerator()
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
    cg = CharGenerator()
    defaultCharMin = 0
    defaultCharMax = 255
    signedCharMin = -127
    signedCharMax = 127
    fg = FloatGenerator()
    defaultFloatMin = 1.2E-38
    defaultFloatMax = 3.4E+38
    doubleMin = 2.3E-308
    doubleMax = 1.7E+308
    longDoubleMin = 3.4E-4932
    longDoubleMax = 1.1E+4932
    vg = VoidGenerator()
    ag = AvailableGenerator()

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
            return self.cg.generate()
        elif typeToGenerate == "signed char":
            self.cg.minChar = self.signedCharMin
            self.cg.maxChar = self.signedCharMax
  
            value = self.cg.generate()

            self.cg.minChar = self.defaultCharMin
            self.cg.maxChar = self.defaultCharMax

            return value
        elif typeToGenerate == "float":
            return self.fg.generate()
        elif typeToGenerate == "double":
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
        elif typeToGenerate == "void" or typeToGenerate == "":
            return self.vg.generate()
        else:
            print("We do not current support input generator for type: "+typeToGenerate)
            return typeToGenerate

#TODO:
# Other primitives
# Pointers
# Typedef/struct
