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

class Num(Token):
    def __init__(self, v):
        super().__init__(Tag.NUM)
        self.value_ = v

class Word(Token):
    def __init__(self, t, s):
        super().__init__(t)
        self.lexeme_ = s

class Lexer():
    def __init__(self, program_string):
        self.program_string_ = program_string
        self.line_ = 1
        self.char_idx_ = 0
        self.words_ = dict()
        self.Reserve(Word(Tag.TRUE, "true"))
        self.Reserve(Word(Tag.FALSE, "false"))

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

class LexedInfixArithmeticParser():
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
            tmp = self.lookahead_;
            self.Match(self.lookahead_.tag_)
            print(f"{tmp.value_} ", end="")
        elif self.lookahead_.tag_ == Tag.ID:
            tmp = self.lookahead_;
            self.Match(self.lookahead_.tag_)
            print(f"{tmp.lexeme_} ", end="")
        elif self.lookahead_.tag_ == ord('('):
            self.Match(ord('('))
            self.expr();
            self.Match(ord(')'))
        else:
            print("Syntax error1!")

    def rest(self):
        if self.lookahead_.tag_ == ord('*'):
            self.Match(ord('*'))
            self.factor()
            self.rest()
            print("* ", end="")
        elif self.lookahead_.tag_ == ord('/'):
            self.Match(ord('/'))
            self.factor()
            self.rest()
            print("/ ", end="")
        else:
            pass

    def term(self):
        self.factor()
        self.rest()

    def expr(self):
        self.term()
        while True:
            if self.lookahead_.tag_ == ord('+'):
                self.Match(ord('+'))
                self.term()
                print("+ ", end="")
                continue
            elif self.lookahead_.tag_ == ord('-'):
                self.Match(ord('-'))
                self.term()
                print("- ", end="")
            break

    def Parse(self):
        self.expr()
        print()

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


for line in sys.stdin:
    if "" == line.rstrip():
        break
    program_string = line.rstrip()
    LexedInfixArithmeticParser(program_string).Parse()
