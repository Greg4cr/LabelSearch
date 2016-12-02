import random
import string

# TODO
# Struct
# Multidimensional arrays
# Unions
# Pointers

# Simple integer generator.
class IntGenerator():
    minInt = -32767
    maxInt = 32767

    def generate(self):
        return str(random.randint(self.minInt,self.maxInt))

# Original char generator produced characters.
# Instead, we are not generating integers in the appropriate range.
# This reduces the chance of issues in producing printed file output.
# Leaving this code block in case this changes later. 

# Simple character generator.
#class CharGenerator():
#    minChar = 0
#    maxChar = 255

#    def generate(self):
#        numRepresentation=random.randint(self.minChar,self.maxChar)
#        #charRepresentation=chr(numRepresentation)
#        return str(numRepresentation)

# Simple floating-point generator.
class FloatGenerator():
    minFloat = -3.4E+38
    maxFloat = 3.4E+38
   
    def generate(self):
        return str(random.uniform(self.minFloat,self.maxFloat))

# Simple boolean generator. Uses 0 for false and 1 for true. 
# Compatible with C99 _Bool/bool. 
# May conflict with program-specific implementations of bool.
class BoolGenerator():
    def generate(self):
        return str(random.randint(0,1))

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
    # Global constants used to bound the range of values generated.
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
    bg = BoolGenerator()
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
            typeToGenerate == "signed short" or typeToGenerate == "signed short int" or \
            typeToGenerate == "int16_t" or typeToGenerate == "int_fast16_t" or typeToGenerate == "int_least16_t":
            self.ig.minInt = self.shortIntMin
            self.ig.maxInt = self.shortIntMax

            value = self.ig.generate()

            self.ig.minInt = self.defaultIntMin
            self.ig.maxInt = self.defaultIntMax

            return value
        elif typeToGenerate == "unsigned short" or typeToGenerate == "unsigned short int" or \
            typeToGenerate == "uint16_t" or typeToGenerate == "uint_fast16_t" or typeToGenerate == "uint_least16_t": 
            self.ig.minInt = self.unsignedIntMin
            self.ig.maxInt = self.unsignedShortMax

            value = self.ig.generate()

            self.ig.minInt = self.defaultIntMin
            self.ig.maxInt = self.defaultIntMax

            return value
        elif typeToGenerate == "long" or typeToGenerate == "long int" or \
            typeToGenerate == "signed long" or typeToGenerate == "signed long int" or \
            typeToGenerate == "int32_t" or typeToGenerate == "int_fast32_t" or typeToGenerate == "int_least32_t":
            self.ig.minInt = self.longIntMin
            self.ig.maxInt = self.longIntMax

            value = self.ig.generate()

            self.ig.minInt = self.defaultIntMin
            self.ig.maxInt = self.defaultIntMax

            return value
        elif typeToGenerate == "unsigned long" or typeToGenerate == "unsigned long int" or \
            typeToGenerate == "uint32_t" or typeToGenerate == "uint_fast32_t" or typeToGenerate == "uint_least32_t": 
            self.ig.minInt = self.unsignedIntMin
            self.ig.maxInt = self.unsignedLongMax

            value = self.ig.generate()

            self.ig.minInt = self.defaultIntMin
            self.ig.maxInt = self.defaultIntMax

            return value
        elif typeToGenerate == "long long" or typeToGenerate == "long long int" or \
            typeToGenerate == "signed long long" or typeToGenerate == "signed long long int" or \
            typeToGenerate == "int64_t" or typeToGenerate == "int_fast64_t" or \
            typeToGenerate == "int_least64_t" or typeToGenerate == "intmax_t":
            self.ig.minInt = self.longLongIntMin
            self.ig.maxInt = self.longLongIntMax

            value = self.ig.generate()

            self.ig.minInt = self.defaultIntMin
            self.ig.maxInt = self.defaultIntMax

            return value
        elif typeToGenerate == "unsigned long long" or typeToGenerate == "unsigned long long int" or \
            typeToGenerate == "uint64_t" or typeToGenerate == "uint_fast64_t" or \
            typeToGenerate == "uint_least64_t" or typeToGenerate == "uintmax_t": 
            self.ig.minInt = self.unsignedIntMin
            self.ig.maxInt = self.unsignedLongLongMax

            value = self.ig.generate()

            self.ig.minInt = self.defaultIntMin
            self.ig.maxInt = self.defaultIntMax

            return value
        elif typeToGenerate == "char" or typeToGenerate == "unsigned char" or \
            typeToGenerate == "uint8_t" or typeToGenerate == "uint_fast8_t" or typeToGenerate == "uint_least8_t":
            self.ig.minInt = self.defaultCharMin
            self.ig.maxInt = self.defaultCharMax

            value = self.ig.generate()

            self.ig.minInt = self.defaultIntMin
            self.ig.maxInt = self.defaultIntMax

            return value
        elif typeToGenerate == "signed char" or \
            typeToGenerate == "int8_t" or typeToGenerate == "int_fast8_t" or typeToGenerate == "int_least8_t":
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
        else:
            print("We do not current support input generation for type: "+typeToGenerate)
            # Signifies to caller that this type is not supported.
            return "//"+typeToGenerate

