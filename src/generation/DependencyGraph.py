# Gregory Gay (greg@greggay.com)
# Visitors that crawl the AST of the C program to pull function and state 
# information and generate the dependency map

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


import sys
from pycparser import c_ast, c_generator

class DependencyMapVisitor(c_ast.NodeVisitor):

    # Dependency Map
    dependencyMap=[]
    # Generator to get C code from a node
    generator = c_generator.CGenerator()
    # List of functions
    functions=[]
    # List of state variables
    stateVariables=[]
    # Current function being examined
    currentFunction=[]
    # Variable status flag
    status="use"

    def __init__(self,functions,stateVariables):
        self.functions=functions
        self.stateVariables=stateVariables

    # When we hit a function definition, grab the function code and look for defs and uses of state variables.
    def visit_FuncDef(self, node):
        # Discard anything seen before we started examining this function
        self.currentFunction=[]
        self.currentFunction.append(node.decl.name)
        # Add empty variable mapping
        self.currentFunction.append([])
        # Crawl through function body for variables uses/defs
        self.visit(node.body)
        # Add to map
        self.dependencyMap.append(self.currentFunction)
        self.currentFunction=[]

    # When we hit an assignment, flip the flag to "def" instead of "use"
    def visit_Assignment(self, node):
        # Make sure this is an "=" assignment. "+=", etc count as uses for our purposes (initialization check)
        if node.op == "=":
            if "obligations" not in self.generator.visit(node.lvalue):
                # LHS is the variable being assigned
                self.status="def"
                self.visit(node.lvalue)
                # Reset before moving on
                self.status="use"
                self.visit(node.rvalue)
        else:
            self.visit(node.lvalue)
            self.visit(node.rvalue)

    # Do the same for unary operations that make assignments.
    # Note that these are both defs and uses
    #def visit_UnaryOp(self, node):
    #    if "++" in node.op or "--" in node.op:
    #        self.status="def"
    #    self.visit(node.expr)
    #    self.status="use"

    # We want to record function calls as well to indicate dependencies.
    # Function arguments can also use state variables
    def visit_FuncCall(self, node):
        self.currentFunction[1].append([node.name.name,"function"])
        args=self.generator.visit(node.args)
        for var in self.stateVariables:
            if var[0] in args:
                self.currentFunction[1].append([var[0],"use"])
                break

    # When we visit a variable reference, add it to the list, along with its status.
    def visit_ID(self, node):
        if node.name!="obligations" and node.name!="scoreEpsilon":
            found=0
            for var in self.stateVariables:
                if node.name == var[0]:
                    found=1
                    break  
 
            if found==1:
                self.currentFunction[1].append([node.name,self.status])

class ProgramDataVisitor(c_ast.NodeVisitor):

    # Function List
    functions=[]

    # Global variable list
    stateVariables=[]

    # Generator to get C code from a node
    generator = c_generator.CGenerator()

    # When we hit a function definition, grab the function name, return type, and arguments.
    def visit_FuncDef(self, node):
        function=[]
        # Name
        function.append(node.decl.name)

        # Return type
        function.append(node.decl.type.type.type.names)

        # Arguments
        args=self.generator.visit(node.decl.type.args).split(",")
        
        function.append(args)
        self.functions.append(function)
     
    # Decl nodes correspond to global variables.
    def visit_Decl(self, node):
        # Get name, type, status (variable, array, pointer), and declared value (if any).
        # Make sure that it is not the obligations array.
        if node.name != "obligations" and node.name != "scoreEpsilon":
            var=[]
            var.append(node.name)
            # Handle based on type
            if type(node.type) is c_ast.TypeDecl:
                # Status
                var.append("var")
                # Type
                var.append(node.type.type.names)
                # Initial Value
                var.append(self.generator.visit(node.init))
                self.stateVariables.append(var)
            if type(node.type) is c_ast.ArrayDecl:
                var.append("array")
                # Type
                var.append(node.type.type.type.names)
                # Initial Value
                var.append(self.generator.visit(node.init))
                self.stateVariables.append(var)
            if type(node.type) is c_ast.PtrDecl:
                # Status
                var.append("pointer")
                # Type
                var.append(node.type.type.type.names)
                # Initial value
                var.append(self.generator.visit(node.init))
                self.stateVariables.append(var)
