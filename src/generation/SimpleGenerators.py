import random

# Simple integer generator.
class IntGenerator():
    minInt = -2147483647
    maxInt = 2147483647

    def generate(self):
        return str(random.randint(self.minInt,self.maxInt))

# Returns an empty string for void (no argument) input
class VoidGenerator():
    def generate(self):
        return ""

# Returns a random variable of the correct datatype from a list of available variables
class AvailableGenerator():
    def generate(self, available, typeToReturn):
        if len(available) > 0:
            found = 0
            while found == 0:
                choice=available[random.randint(0,len(available)-1)]
                if choice[1] == typeToReturn:
                    found=1
       
            return choice[0]
        else:
            return ""

# Takes in a datatype, and returns a valid instance for that type.
# Returns it in string form, as the result will be inserted into C code.
class GeneratorFactory():
    available = []
    ig = IntGenerator()
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
        elif typeToGenerate == "void":
            return self.vg.generate()
        else:
            print("We do not current support input generator for type: "+typeToGenerate)
            return typeToGenerate

#TODO:
# Other primitives
# Pointers
# Typedef/struct
# Arrays of all types (probably handle outside of Generators - keep Generators for each entry
