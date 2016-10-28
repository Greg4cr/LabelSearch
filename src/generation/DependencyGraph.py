import sys
from pycparser import c_ast, c_generator

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
