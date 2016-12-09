# Gregory Gay (greg@greggay.com)
# Simple input generators
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import random
import string

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
