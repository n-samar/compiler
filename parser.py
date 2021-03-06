#!/usr/bin/env python3

import sys

class Token():
    def __init__(self, t):
        self.tag_ = t

class Tag():
    NUM = 256
    ID = 257
    TRUE = 258
    FALSE = 259
    EOF = 260
    TYPE = 261
    WHILE = 262
    IF = 263

class Num(Token):
    def __init__(self, v):
        super().__init__(Tag.NUM)
        self.value_ =  v

    def Visit(self):
        print(f"{self.value_}")

    def name(self):
        return self.value_

class Word(Token):
    def __init__(self, t, s):
        super().__init__(t)
        self.lexeme_ = s

    def Visit(self):
        print(f"{self.lexeme_}")

    def name(self):
        return self.lexeme_

def lvalue(expr):
    if isinstance(expr, Word):
            return expr
    print(f"Syntax error4!")

curr_label = 0
def newlabel():
    global curr_label
    newlabel = "__" + str(curr_label)
    curr_label+=1
    return newlabel

curr_tmp = 0
class Temporary():
    def __init__(self):
        global curr_tmp
        self.name_ = "tmp" + str(curr_tmp)
        curr_tmp+=1

    def name(self):
        return self.name_

def rvalue(expr):
    if isinstance(expr, Word) or isinstance(expr, Num):
        return expr
    if isinstance(expr, Op) or isinstance(expr, Rel):
        t = Temporary()
        print(f"{t.name()} = {rvalue(expr.lhs_).name()} {expr.lexeme_} {rvalue(expr.rhs_).name()}")
        return t
    if isinstance(expr, Assign):
        z_prime = rvalue(expr.rhs_)
        print(f"{lvalue(expr.lhs_).name()} = {z_prime.name()}")
        return z_prime
    print(f"Syntax error: not rvalue {type(expr).__name__} {isinstance(expr, Rel)}")

class Lexer():
    def __init__(self, program_string):
        self.program_string_ = program_string
        self.line_ = 1
        self.char_idx_ = 0
        self.words_ = dict()
        self.Reserve(Word(Tag.TRUE, "true"))
        self.Reserve(Word(Tag.FALSE, "false"))
        self.Reserve(Word(Tag.TYPE, "bool"))
        self.Reserve(Word(Tag.TYPE, "char"))
        self.Reserve(Word(Tag.TYPE, "int"))
        self.Reserve(Word(Tag.WHILE, "while"))
        self.Reserve(Word(Tag.IF, "if"))

    def Reserve(self, word) -> None:
        self.words_[word.lexeme_] = word

    def SkipWhitespace(self) -> None:
        while self.char_idx_ < len(self.program_string_) and self.curr_char().isspace():
            if self.curr_char() == '\n':
                self.line_ += 1
            self.char_idx_ += 1

    def curr_char(self):
        if self.char_idx_ < len(self.program_string_):
            return self.program_string_[self.char_idx_]
        return ' '

    def ScanConstant(self) -> Num:
        v = 0
        while self.curr_char().isdigit():
            v = 10*v + int(self.curr_char())
            self.char_idx_ += 1
        return Num(v)

    def ScanIdentifier(self) -> Word:
        s = ""
        while self.curr_char().isalpha() or self.curr_char().isdigit():
            s += self.curr_char()
            self.char_idx_ += 1
        w = self.words_.get(s, None)
        if w != None:
            return w
        w = Word(Tag.ID, s)
        self.Reserve(w)
        return w

    def Scan(self) -> Token:
        self.SkipWhitespace()
        if self.char_idx_ == len(self.program_string_):
            return Token(Tag.EOF)
        if self.curr_char().isdigit():
            return self.ScanConstant()
        if self.curr_char().isalpha():
            return self.ScanIdentifier()
        t = Token(ord(self.curr_char()))
        self.char_idx_ += 1
        return t

class Symbol():
    pass

class Node():
    pass

class Assign(Node):
    def __init__(self, lexeme, lhs, rhs):
        self.lexeme_ = lexeme
        self.lhs_ = lhs
        self.rhs_ = rhs

    def Visit(self):
        pass

class Seq():
    def __init__(self, stmt, stmts):
        self.stmt_ = stmt
        self.stmts_ = stmts

    def Visit(self):
        self.stmt_.Visit()
        if self.stmts_ is not None:
            self.stmts_.Visit()

class Eval():
    def __init__(self, node):
        self.node_ = node

    def Visit(self):
        rvalue(self.node_)

class Op():
    def __init__(self, lexeme, operand0, operand1):
        self.lexeme_ = lexeme
        self.lhs_ = operand0
        self.rhs_ = operand1

    def Visit(self):
        pass

class Rel():
    def __init__(self, lexeme, lhs, rhs):
        self.lexeme_ = lexeme
        self.lhs_ = lhs
        self.rhs_ = rhs

    def Visit(self):
        print(f"{self.lexeme_}")
        self.lhs_.Visit()
        self.rhs_.Visit()

class While():
    def __init__(self, cond, body, start_label = newlabel(), end_label = newlabel()):
        self.cond_ = cond
        self.body_ = body
        self.start_label_ = start_label
        self.end_label_ = end_label

    def Visit(self):
        n = rvalue(self.cond_)
        print(f"{self.start_label_}:")
        print(f"ifFalse {n.name()} goto {self.end_label_}")
        self.body_.Visit()
        print(f"goto {self.start_label_}")
        print(f"{self.end_label_}:")

class If():
    def __init__(self, cond, body, label = newlabel()):
        self.cond_ = cond
        self.body_ = body
        self.label_ = label

    def Visit(self):
        n = rvalue(self.cond_)
        print(f"ifFalse {n.name()} goto {self.label_}")
        self.body_.Visit()
        print(f"{self.label_}:")


class LexedParser():
    def __init__(self, program_string):
        self.lexer_ = Lexer(program_string)
        self.char_idx_ = 0
        self.lookahead_ = self.NextToken()

    def NextToken(self):
        token = self.lexer_.Scan()
        return token

    def Match(self, tag : int) -> None:
        if self.lookahead_.tag_ == tag:
            self.lookahead_ = self.NextToken()
        else:
            print("Syntax error0!")
            exit()

    def factor(self):
        if self.lookahead_.tag_ == Tag.NUM:
            tmp = self.lookahead_
            self.Match(self.lookahead_.tag_)
            return tmp
        elif self.lookahead_.tag_ == Tag.ID:
            tmp = self.lookahead_
            self.Match(self.lookahead_.tag_)
            s = self.top_env_.Get(tmp.lexeme_)
            return tmp
        elif self.lookahead_.tag_ == ord('('):
            self.Match(ord('('))
            node = self.expr()
            self.Match(ord(')'))
            return node
        else:
            print("Syntax error1!")

    def rest_factor(self, factor_node):
        if self.lookahead_.tag_ == ord('*'):
            self.Match(ord('*'))
            node = Op('*', factor_node, self.factor())
            node = self.rest_factor(node)
            return node
        elif self.lookahead_.tag_ == ord('/'):
            self.Match(ord('/'))
            node = Op('/', factor_node, self.factor())
            node = self.rest_factor(node)
            return node
        else:
            return factor_node

    def term(self):
        factor_node = self.factor()
        return self.rest_factor(factor_node)

    def add(self):
        node = self.term()
        while True:
            if self.lookahead_.tag_ == ord('+'):
                self.Match(ord('+'))
                node = Op("+", node, self.term())
                continue
            elif self.lookahead_.tag_ == ord('-'):
                self.Match(ord('-'))
                node = Op("-", node, self.term())
            return node

    def expr_rest(self, node):
        if self.lookahead_.tag_ == ord('='):
            self.Match(ord('='))
            return self.expr_rest(Assign('=', node, self.expr()))
        else:
            return node

    def rel_rest(self, node):
        if self.lookahead_.tag_ == ord('<'):
            self.Match(ord('<'))
            return self.rel_rest(Rel('<', node, self.add()))
        else:
            return node

    def rel(self):
        node = self.add()
        return self.rel_rest(node)

    def expr(self):
        node = self.rel()
        return self.expr_rest(node)

    def program(self):
        self.top_env_ = None
        return self.block()

    def block(self):
        self.Match(ord('{'))
        self.saved_env_ = self.top_env_
        self.top_env_ = Env(self.top_env_)
        self.decls()
        node = self.stmts()
        self.Match(ord('}'))
        self.top_env_ = self.saved_env_
        return node

    def stmt(self):
        if self.lookahead_.tag_ == ord('{'):
            return self.block()
        elif self.lookahead_.tag_ == Tag.WHILE:
            self.Match(Tag.WHILE)
            self.Match(ord('('))
            cond = self.expr()
            self.Match(ord(')'))
            body = self.stmt()
            return While(cond, body)
        elif self.lookahead_.tag_ == Tag.IF:
            self.Match(Tag.IF)
            self.Match(ord('('))
            cond = self.expr()
            self.Match(ord(')'))
            body = self.stmt()
            return If(cond, body)
        else:
            node = Eval(self.expr())
            self.Match(ord(';'))
            return node

    def stmts(self):
        if self.lookahead_.tag_ == ord('}'):
            return None
        else:
            return Seq(self.stmt(), self.stmts())

    def decls(self):
        if self.lookahead_.tag_ == Tag.TYPE:
            self.decl()
            self.decls()
        else:
            pass

    def decl(self):
        s = Symbol()
        s.type_ = self.lookahead_.lexeme_
        self.Match(Tag.TYPE)
        self.top_env_.Put(self.lookahead_.lexeme_, s)
        self.Match(Tag.ID)
        self.Match(ord(';'))

    def Parse(self):
        return self.program()

class Env():
    def __init__(self, parent_env):
        self.parent_env_ = parent_env
        self.table_ = dict()

    def Get(self, s):
        curr_env = self
        while curr_env != None:
            if curr_env.table_.get(s, None) != None:
                return curr_env.table_.get(s, None)
            curr_env = curr_env.parent_env_
        return None

    def Put(self, s, symbol):
        self.table_[s] = symbol


program_string = sys.stdin.read()
syntax_tree = LexedParser(program_string).Parse()

syntax_tree.Visit()
