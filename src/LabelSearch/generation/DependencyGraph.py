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
        if type(node.name) is c_ast.UnaryOp:
            self.currentFunction[1].append([node.name.expr.name,"function"]) 
        else:
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
    functions = []
    # Global variable list
    stateVariables = []
    # Type definition list
    typeDefs = []
    # Struct definition list
    structs = []
    # Union definition list
    unions = []
    # Enum definition list
    enums = []
    # Generator to get C code from a node
    generator = c_generator.CGenerator()

    # When we hit a function definition, grab the function name, return type, and arguments.
    def visit_FuncDef(self, node):
        function=[]
        # Name
        function.append(node.decl.name)

        # Return type
        if type(node.decl.type.type) is c_ast.PtrDecl:
            rType = []
            if type(node.decl.type.type.type.type) is c_ast.Enum:
                rType = ['*','enum']
                rType.append(node.decl.type.type.type.type.name)
            elif type(node.decl.type.type.type.type) is c_ast.Struct:
                rType = ['*','struct']
                rType.append(node.decl.type.type.type.type.name)
            elif type(node.decl.type.type.type.type) is c_ast.Union:
                rType = ['*','union']
                rType.append(node.decl.type.type.type.type.name)
            else:
                rType = node.decl.type.type.type.type.names
                rType.insert(0,"*")

            function.append(rType)
        elif type(node.decl.type.type.type) is c_ast.Enum:
            rType = ['enum']
            rType.append(node.decl.type.type.type.name)
            function.append(rType)
        elif type(node.decl.type.type.type) is c_ast.Struct:
            rType = ['struct']
            rType.append(node.decl.type.type.type.name)
            function.append(rType)
        elif type(node.decl.type.type.type) is c_ast.Union:
            rType = ['union']
            rType.append(node.decl.type.type.type.name)
            function.append(rType)
        else:
            function.append(node.decl.type.type.type.names)

        # Arguments
        args=self.generator.visit(node.decl.type.args).split(",")
        
        function.append(args)
        self.functions.append(function)
     
    # Decl nodes correspond to global variables and structs.
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
                if type(node.type.type) is c_ast.Struct: 
                    var.append(["struct", node.type.type.name])
                elif type(node.type.type) is c_ast.Union:
                    var.append(["union", node.type.type.name])
                elif type(node.type.type) is c_ast.Enum:
                    var.append(["enum", node.type.type.name])
                else:
                    var.append(node.type.type.names)
                # Initial Value
                var.append(self.generator.visit(node.init))
                self.stateVariables.append(var)
            elif type(node.type) is c_ast.ArrayDecl:
                var.append("array,"+str(node.type.dim.value))
                # Type
                var.append(node.type.type.type.names)
                # Initial Value
                var.append(self.generator.visit(node.init))
                self.stateVariables.append(var)
            elif type(node.type) is c_ast.PtrDecl:
                # Status
                var.append("pointer")
                # Type
                nextLevel = node.type
                # Could have multiple levels of pointer, i.e., **int or ***int
                # We need to dig through until we find the type information
                while type(nextLevel) is c_ast.PtrDecl:
                    nextLevel = nextLevel.type
 
                if type(nextLevel.type) is c_ast.Struct: 
                    var.append(["struct", nextLevel.type.name])
                elif type(nextLevel.type) is c_ast.Union:
                    var.append(["union", nextLevel.type.name])
                elif type(nextLevel.type) is c_ast.Enum:
                    var.append(["enum", nextLevel.type.name])
                else:
                    var.append(nextLevel.type.names)
                # Initial value
                var.append(self.generator.visit(node.init))
                self.stateVariables.append(var)
            elif type(node.type) is c_ast.Struct:
                struct = []
                struct.append(node.type.name)
                struct.append([])
                for decl in node.type.decls:
                    member = []
                    member.append(decl.name)
                    member.append([])
                    if type(decl.type) is c_ast.TypeDecl:
                        # Status
                        member[1].append("var")
                        # Type
                        cType = []
                        if type(decl.type.type) is c_ast.Enum:
                            cType = ['enum']
                            cType.append(decl.type.type.name)
                        elif type(decl.type.type) is c_ast.Struct:
                            cType = ['struct']
                            cType.append(decl.type.type.name)
                        elif type(decl.type.type) is c_ast.Union:
                            cType = ['union']
                            cType.append(decl.type.type.name)
                        else:
                            cType = decl.type.type.names
                        
                        member[1].append(cType)
                    elif type(decl.type) is c_ast.ArrayDecl:
                        member[1].append("array,"+str(decl.type.dim.value))
                        # Type
                        cType = []
                        if type(decl.type.type.type) is c_ast.Enum:
                            cType = ['enum']
                            cType.append(decl.type.type.type.name)
                        elif type(decl.type.type.type) is c_ast.Struct:
                            cType = ['struct']
                            cType.append(decl.type.type.type.name)
                        elif type(decl.type.type.type) is c_ast.Union:
                            cType = ['union']
                            cType.append(decl.type.type.type.name)
                        else:
                            cType = decl.type.type.type.names
                        
                        member[1].append(cType)
                    elif type(decl.type) is c_ast.PtrDecl:
                        member[1].append("pointer")
                        nextLevel = decl.type.type
                        # Could have multiple levels of pointer, i.e., **int or ***int
                        # We need to dig through until we find the type information
                        while type(nextLevel) is c_ast.PtrDecl:
                            nextLevel = nextLevel.type
 
                        # Type
                        cType = []
                        if type(nextLevel.type) is c_ast.Enum:
                            cType = ['enum']
                            cType.append(nextLevel.type.name)
                        elif type(nextLevel.type) is c_ast.Struct:
                            cType = ['struct']
                            cType.append(nextLevel.type.name)
                        elif type(nextLevel.type) is c_ast.Union:
                            cType = ['union']
                            cType.append(nextLevel.type.name)
                        else:
                            cType = nextLevel.type.names
                        
                        member[1].append(cType)

                    struct[1].append(member)
                self.structs.append(struct)

    # TypeDecl nodes indicate type definitions
    def visit_TypeDecl(self, node):
        # Get the name and type of all typedefs.
        if type(node.type) is c_ast.Enum:

            if node.type.name != None:
                self.typeDefs.append([node.declname, ["enum", node.type.name]])
            else:
                self.typeDefs.append([node.declname, ["enum", node.declname]])
        elif type(node.type) is c_ast.Struct:
            if node.type.name != None:
                self.typeDefs.append([node.declname, ["struct", node.type.name]])
            else:
                self.typeDefs.append([node.declname, ["struct", node.declname]])

            # If the structure definition is included, capture it
            if node.type.decls != None:
                struct = []
                if node.type.name != None:
                    struct.append(node.type.name)
                else:
                    struct.append(node.declname)
                struct.append([])
                for decl in node.type.decls:
                    member = []
                    member.append(decl.name)
                    member.append([])
                    if type(decl.type) is c_ast.TypeDecl:
                        # Status
                        member[1].append("var")
                        # Type
                        member[1].append(decl.type.type.names)
                    elif type(decl.type) is c_ast.ArrayDecl:
                        member[1].append("array,"+str(decl.type.dim.value))
                        member[1].append(decl.type.type.type.names)
                    elif type(decl.type) is c_ast.PtrDecl:
                        member[1].append("pointer")
                        member[1].append(decl.type.type.type.names)

                    struct[1].append(member)
                self.structs.append(struct)
        elif type(node.type) is c_ast.Union:
            if node.type.name != None:
                self.typeDefs.append([node.declname, ["union", node.type.name]])
            else:
                self.typeDefs.append([node.declname, ["union", node.declname]])

            # If the structure definition is included, capture it
            if node.type.decls != None:
                union = []
                if node.type.name != None:
                    union.append(node.type.name)
                else:
                    union.append(node.declname)
                union.append([])
                for decl in node.type.decls:
                    member = []
                    member.append(decl.name)
                    member.append([])
                    if type(decl.type) is c_ast.TypeDecl:
                        # Status
                        member[1].append("var")
                        # Type
                        member[1].append(decl.type.type.names)
                    elif type(decl.type) is c_ast.ArrayDecl:
                        member[1].append("array,"+str(decl.type.dim.value))
                        member[1].append(decl.type.type.type.names)
                    elif type(decl.type) is c_ast.PtrDecl:
                        member[1].append("pointer")
                        member[1].append(decl.type.type.type.names)

                    union[1].append(member)
                self.unions.append(union)
        else:
            self.typeDefs.append([node.declname, node.type.names])

