# Gregory Gay (greg@greggay.com)
# Predicate parsing and translation to cost functions.
# Based on code by Ruslan Spivak (https://ruslanspivak.com/lsbasi-part7/)
# Cost functions and normalization function are based on those defined in: 
# Arcuri, Andrea. "It really does matter how you normalize the branch distance in search-based software testing."
# Software Testing, Verification and Reliability 23.2 (2013): 119-147.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

###############################################################################
#                                                                             #
#  LEXER                                                                      #
#                                                                             #
###############################################################################

# Token types
#
# EOF (end-of-file) token is used to indicate that
# there is no more input left for lexical analysis
ATOM, LT, LTE, GT, GTE, EQ, NEQ, AND, OR, NOT, LPAREN, RPAREN, EOF = (
    'ATOM', 'LT', 'LTE', 'GT', 'GTE', 'EQ', 'NEQ', 'AND', 'OR', 'NOT', '(', ')', 'EOF'
)

class Token(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        """String representation of the class instance.

        Examples:
            Token(INTEGER, 3)
            Token(PLUS, '+')
            Token(MUL, '*')
        """
        return 'Token({type}, {value})'.format(
            type=self.type,
            value=repr(self.value)
        )

    def __repr__(self):
        return self.__str__()

class Lexer(object):
    def __init__(self, text):
        print text
        # client string input, e.g. "4 + 2 * 3 - 6 / 2"
        self.text = text
        # self.pos is an index into self.text
        self.pos = 0
        self.current_char = self.text[self.pos]

    def error(self):
        raise Exception('Invalid character')

    def advance(self):
        """Advance the `pos` pointer and set the `current_char` variable."""
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None  # Indicates end of input
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def atom(self):
        """Return a multicharacter atom consumed from the input."""
        result = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        return result

    # Look ahead at next token
    def look_ahead(self):
        if self.pos < len(self.text):
            current_pos = self.pos
            token = self.get_next_token()
            self.pos = current_pos
            self.current_char = self.text[self.pos]

            return token
        else:
            return Token(EOF, None)

    def get_next_token(self):
        """Lexical analyzer (also known as scanner or tokenizer)

        This method is responsible for breaking a sentence
        apart into tokens. One token at a time.
        """
        while self.current_char is not None:

            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isalnum() or self.current_char == '_':
                return Token(ATOM, self.atom())

            if self.current_char == '<':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(LTE, '<=')
                else:
                    return Token(LT, '<')

            if self.current_char == '>':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(GTE, '>=')
                else:
                    return Token(GT, '>')

            if self.current_char == '=':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(EQ, '==')
                else:
                    raise Exception("Illegal use of assignment in predicate")

            if self.current_char == '!':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(NEQ, '!=')
                else:
                    return Token(NOT, '!')

            if self.current_char == '&':
                self.advance()
                if self.current_char == '&':
                    self.advance()
                    return Token(AND, '&&')
                else:
                    raise Exception("Illegal use of bitwise AND")

            if self.current_char == '|':
                self.advance()
                if self.current_char == '|':
                    self.advance()
                    return Token(OR, '||')
                else:
                    raise Exception("Illegal use of bitwise OR")

            if self.current_char == '(':
                self.advance()
                return Token(LPAREN, '(')

            if self.current_char == ')':
                self.advance()
                return Token(RPAREN, ')')

            self.error()

        return Token(EOF, None)

###############################################################################
#                                                                             #
#  PARSER                                                                     #
#                                                                             #
###############################################################################

class AST(object):
    pass

class BinOp(AST):
    def __init__(self,left,op,right):
        self.left = left
        self.token = self.op = op
        self.right = right

class Atom(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class BoolVar(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value
   
class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        # Set current token to the first token taken from the input
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception("Invalid syntax")

    def eat(self, token_type):
        # compare the current token type with the passed token
        # type and if they match then "eat" the current token
        # and assign the next token to the self.current_token,
        # otherwise raise an exception.
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def factor(self,propagateNot,boolVar):
        """factor : (NOT)* ATOM | (NOT)* LPAREN notExpr RPAREN
           Second argument - used to determine if an ATOM is a boolean variable that is not part of a term.
           (i.e., x in (x && (y < 4))
        """
        token = self.current_token

        if token.type == NOT:
            self.eat(NOT)
            token = self.current_token
            if token.type == ATOM:
                self.eat(ATOM)
                if propagateNot == 0:
                    token.value = "!"+token.value
                    if boolVar == 1:
                        return BoolVar(token)
                    else:
                        return Atom(token)
                else:
                    if boolVar == 1:
                        return BoolVar(token)
                    else:
                        return Atom(token)
            elif token.type == LPAREN:
                self.eat(LPAREN)
                if propagateNot == 0:
                    node = self.expr(1)
                else:
                    # If !(!(x)), cancel out the NOT
                    node = self.expr(0)
                self.eat(RPAREN)
                return node
        elif token.type == ATOM:
            self.eat(ATOM)
            if propagateNot == 1:
               token.value = "!"+token.value
               if boolVar == 1:
                   return BoolVar(token)
               else:
                   return Atom(token)
            else:
               if boolVar == 1:
                   return BoolVar(token)
               else:
                   return Atom(token)
        elif token.type == LPAREN:
            self.eat(LPAREN)
            node = self.expr(propagateNot)
            self.eat(RPAREN)
            return node

    def term(self, propagateNot):
        """
        term   : factor ((LT | LTE | GT | GTE | EQ | NEQ) factor)*
        """
        nextToken = self.lexer.look_ahead()
        if nextToken.type in (LT, LTE, GT, GTE, EQ, NEQ):
            node = self.factor(0,0)
        else:
            node = self.factor(propagateNot,1)

        while self.current_token.type in (LT, LTE, GT, GTE, EQ, NEQ):
            token = self.current_token

            if propagateNot == 1:
                # NOT (x == 3) becomes (x != 3), etc.
                # Transform the operator if a NOT is being propagated, then stop propagating the NOT to the right side of the expression.
                if token.type == LT:
                    self.eat(LT)
                    token = Token(GTE, '>=')
                elif token.type == LTE:
                    self.eat(LTE)
                    token = Token(GT, '>')
                elif token.type == GT:
                    self.eat(GT)
                    token = Token(LTE, '<=')
                elif token.type == GTE:
                    self.eat(GTE)
                    token = Token(LT, '<')
                elif token.type == EQ:
                    self.eat(EQ)
                    token = Token(NEQ, '!=')
                elif token.type == NEQ:
                    self.eat(NEQ)
                    token = Token(EQ, '==')
            else:
                if token.type == LT:
                    self.eat(LT)
                elif token.type == LTE:
                    self.eat(LTE)
                elif token.type == GT:
                    self.eat(GT)
                elif token.type == GTE:
                    self.eat(GTE)
                elif token.type == EQ:
                    self.eat(EQ)
                elif token.type == NEQ:
                    self.eat(NEQ)

            node = BinOp(left=node, op=token, right=self.factor(0,0))

        return node

    def expr(self, propagateNot):
        """
        expr   : term ((AND | OR) term)*
        term   : factor ((LT | LTE | GT | GTE | EQ | NEQ) factor)*
        factor : (NOT)* ATOM | (NOT)* LPAREN expr RPAREN
        """
        node = self.term(propagateNot)

        while self.current_token.type in (AND, OR):
            token = self.current_token
            if token.type == AND:
                self.eat(AND)
            elif token.type == OR:
                self.eat(OR)

            node = BinOp(left=node, op=token, right=self.term(propagateNot))

        return node
        
    '''
    def notExpr(self,propagateNot):
        """
        notExpr: NOT expr | expr
        expr   : term ((AND | OR) term)*
        term   : factor ((LT | LTE | GT | GTE | EQ | NEQ) factor)*
        factor : (NOT)* ATOM | (NOT)* LPAREN expr RPAREN
        """

        if self.current_token.type == NOT:
            self.eat(NOT)
            if propagateNot == 0:
                node = self.expr(1)
            else:
                # If !(!(X)) seen, the two NOTs cancel out.
                node = self.expr(0)
        else:
            node = self.expr(propagateNot)

        return node
    '''

    def parse(self):
        return self.expr(0)

###############################################################################
#                                                                             #
#  INTERPRETER                                                                #
#                                                                             #
###############################################################################

class NodeVisitor(object):
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))

class Interpreter(NodeVisitor):
    def __init__(self, parser):
        self.parser = parser

    def visit_BinOp(self, node):
        if node.op.type == LT:
            return "("+self.visit(node.left)+" - "+self.visit(node.right)+" < 0 ? 0 : ("+self.visit(node.left)+" - "+self.visit(node.right)+") + scoreEpsilon)"
        elif node.op.type == LTE:
            return "("+self.visit(node.left)+" - "+self.visit(node.right)+" <= 0 ? 0 : ("+self.visit(node.left)+" - "+self.visit(node.right)+") + scoreEpsilon)"
        elif node.op.type == GT:
            return "("+self.visit(node.right)+" - "+self.visit(node.left)+" < 0 ? 0 : ("+self.visit(node.right)+" - "+self.visit(node.left)+") + scoreEpsilon)"
        elif node.op.type == GTE:
            return "("+self.visit(node.right)+" - "+self.visit(node.left)+" <= 0 ? 0 : ("+self.visit(node.right)+" - "+self.visit(node.left)+") + scoreEpsilon)"
        elif node.op.type == EQ:
            return "(abs("+self.visit(node.left)+" - "+self.visit(node.right)+") == 0 ? 0 : abs("+self.visit(node.left)+" - "+self.visit(node.right)+") + scoreEpsilon)"
        elif node.op.type == NEQ:
            return "(abs("+self.visit(node.left)+" - "+self.visit(node.right)+") != 0 ? 0 : scoreEpsilon)"
        elif node.op.type == AND:
            return "("+self.visit(node.left)+" + "+self.visit(node.right)+")" 
        elif node.op.type == OR:
            return "("+self.visit(node.left)+" < "+self.visit(node.right)+" ? "+self.visit(node.left)+" : "+self.visit(node.right)+")" 

    def visit_BoolVar(self, node):
        return "("+node.value+" ? 0 : scoreEpsilon)"

    def visit_Atom(self, node):
        return node.value

    def interpret(self):
        tree = self.parser.parse()
        return self.visit(tree)

def main():
    while True:
        try:
            try:
                text = raw_input('predicate> ')
            except NameError:  # Python3
                text = input('predicate> ')
        except EOFError:
            break
        if not text:
            continue

        lexer = Lexer(text)
        parser = Parser(lexer)
        interpreter = Interpreter(parser)
        result = interpreter.interpret()
        print(result)

if __name__ == '__main__':
    main()
