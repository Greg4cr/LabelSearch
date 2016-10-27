from pycparser import c_ast

class ProgramDataVisitor(c_ast.NodeVisitor):

    # Function List
    functions=[]

    # Global variable list
    stateVariables=[]

    # When we hit a function definition, grab the function name, return type, and arguments.
    def visit_FuncDef(self, node):
        function=[]
        # Name
        function.append(node.decl.name)
        args=[]
        # Arguments
        for param in node.decl.type.args.params:
            arg=[]
            # Argument Name
            arg.append(param.name)
            # Argument Type
            arg.append(param.type.type.names)
            args.append(arg)

        function.append(args)
        self.functions.append(function)
     
    # Decl nodes correspond to global variables.
    def visit_Decl(self, node):
        # Get name, type, and declared value (if any).
        # Make sure that it is not the obligations array.
        if node.name != "obligations":
            var=[]
            var.append(node.name)
            # Handle based on type
            if type(node.type) is c_ast.TypeDecl:
                print "TD"
                self.stateVariables.append(var)
            if type(node.type) is c_ast.ArrayDecl:
                print "AD"
                self.stateVariables.append(var)
            if type(node.type) is c_ast.PtrDecl:
                print "PD"
                self.stateVariables.append(var)
