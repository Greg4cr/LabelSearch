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

# Takes in a datatype, and returns a valid instance for that type.
# Returns it in string form, as the result will be inserted into C code.
class GeneratorFactory():
    ig = IntGenerator()
    vg = VoidGenerator()

    def generate(self,typeToGenerate):
        if typeToGenerate == "int":
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
