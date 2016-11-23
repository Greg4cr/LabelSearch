import random
import string

# Simple integer generator.
class IntGenerator():
    minInt = -2147483647
    maxInt = 2147483647

    def generate(self):
        return str(random.randint(self.minInt,self.maxInt))

# Simple character generator.
class CharGenerator():
    minChar=0
    maxChar=255

    def generate(self):
        numRepresentation=random.randint(self.minChar,self.maxChar)
        #charRepresentation=chr(numRepresentation)
        return str(numRepresentation)

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
    cg = CharGenerator()
    vg = VoidGenerator()
    ag = AvailableGenerator()

    def generate(self,typeToGenerate):
        if typeToGenerate == "int":
            # At a set probability, use an available variable instead of generating a new value.
            if random.random() < 0.25:
                choice = self.ag.generate(self.available,typeToGenerate)
                if choice != "":
                    return choice
                else:
                    return self.ig.generate()
            else:
                return self.ig.generate()
        elif typeToGenerate == "char" or typeToGenerate == "unsigned char":
            return self.cg.generate()

        elif typeToGenerate == "signed char":
            self.cg.minChar = -128
            self.cg.maxChar = 127
  
            value = self.cg.generate()

            self.cg.minChar = 0
            self.cg.maxChar = 255

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
