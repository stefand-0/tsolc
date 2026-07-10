#!/usr/bin/env python3
"""
Sol Compiler - Transpiles Sol language to C, then compiles and runs with clang.

Usage:
    python sol.py <filename.sol> [--run] [--keep-c]

Supports:
    get("path/to/file.sol")  -- import another Sol file
"""

import sys
import os
import stat
import subprocess
from enum import Enum, auto
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass

# =============================================================================
# TOKEN DEFINITIONS
# =============================================================================

class TokenType(Enum):
    IDENTIFIER = auto()
    TYPE = auto()
    NUMBER = auto()
    FLOAT = auto()
    STRING = auto()
    CHAR = auto()

    PUB = auto()
    IN = auto()
    OUT = auto()
    IF = auto()
    ELSEIF = auto()
    ELSE = auto()
    FOR = auto()
    END = auto()
    STRUCT = auto()
    GET = auto()
    MAIN = auto()
    RETURN = auto()
    BREAK = auto()
    CONTINUE = auto()

    ASSIGN = auto()
    COMMA = auto()
    LBRACE = auto()
    RBRACE = auto()
    LPAREN = auto()
    RPAREN = auto()
    SEMICOLON = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    PLUSPLUS = auto()
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    MODULO = auto()
    EQUAL = auto()
    NOTEQUAL = auto()
    LESS = auto()
    LESSEQUAL = auto()
    GREATER = auto()
    GREATEREQUAL = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    DOT = auto()
    COLON = auto()
    ARROW = auto()

    EOF = auto()

KEYWORDS = {
    'pub': TokenType.PUB,
    'in': TokenType.IN,
    'out': TokenType.OUT,
    'if': TokenType.IF,
    'elseif': TokenType.ELSEIF,
    'else': TokenType.ELSE,
    'for': TokenType.FOR,
    'end': TokenType.END,
    'struct': TokenType.STRUCT,
    'get': TokenType.GET,
    'main': TokenType.MAIN,
    'return': TokenType.RETURN,
    'break': TokenType.BREAK,
    'continue': TokenType.CONTINUE,
}

TYPES = {
    'int', 'float', 'char', 'bool', 'string', 'void',
    'int8', 'int16', 'int32', 'int64',
    'uint8', 'uint16', 'uint32', 'uint64',
    'double', 'long', 'short', 'byte',
}

class Token:
    def __init__(self, type: TokenType, value: Any = None, line: int = 0, column: int = 0):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, line={self.line}, col={self.column})"

# =============================================================================
# LEXER
# =============================================================================

class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens = []

    def error(self, msg: str):
        raise SyntaxError(f"{msg} at line {self.line}, column {self.column}")

    def advance(self) -> str:
        char = self.source[self.position]
        self.position += 1
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char

    def peek(self, offset: int = 0) -> str:
        pos = self.position + offset
        if pos >= len(self.source):
            return '\0'
        return self.source[pos]

    def add_token(self, type: TokenType, value: Any = None):
        self.tokens.append(Token(type, value, self.line, self.column))

    def tokenize(self) -> List[Token]:
        while self.position < len(self.source):
            char = self.peek()

            if char.isspace():
                self.advance()
                continue

            if char == '/' and self.peek(1) == '/':
                while self.position < len(self.source) and self.peek() != '\n':
                    self.advance()
                continue

            if char == '/' and self.peek(1) == '*':
                self.advance(); self.advance()
                while self.position < len(self.source) - 1:
                    if self.peek() == '*' and self.peek(1) == '/':
                        self.advance(); self.advance()
                        break
                    self.advance()
                continue

            if char == '-' and self.peek(1) == '>':
                self.advance(); self.advance()
                self.add_token(TokenType.ASSIGN, '->')
                continue

            if char == '+' and self.peek(1) == '+':
                self.advance(); self.advance()
                self.add_token(TokenType.PLUSPLUS, '++')
                continue

            if char == '&' and self.peek(1) == '&':
                self.advance(); self.advance()
                self.add_token(TokenType.AND, '&&')
                continue

            if char == '|' and self.peek(1) == '|':
                self.advance(); self.advance()
                self.add_token(TokenType.OR, '||')
                continue

            if char == '=' and self.peek(1) == '=':
                self.advance(); self.advance()
                self.add_token(TokenType.EQUAL, '==')
                continue

            if char == '!' and self.peek(1) == '=':
                self.advance(); self.advance()
                self.add_token(TokenType.NOTEQUAL, '!=')
                continue

            if char == '<' and self.peek(1) == '=':
                self.advance(); self.advance()
                self.add_token(TokenType.LESSEQUAL, '<=')
                continue

            if char == '>' and self.peek(1) == '=':
                self.advance(); self.advance()
                self.add_token(TokenType.GREATEREQUAL, '>=')
                continue

            if char == '=' and self.peek(1) == '>':
                self.advance(); self.advance()
                self.add_token(TokenType.ARROW, '=>')
                continue

            single_tokens = {
                ',': TokenType.COMMA,
                '{': TokenType.LBRACE,
                '}': TokenType.RBRACE,
                '(': TokenType.LPAREN,
                ')': TokenType.RPAREN,
                ';': TokenType.SEMICOLON,
                '[': TokenType.LBRACKET,
                ']': TokenType.RBRACKET,
                '+': TokenType.PLUS,
                '-': TokenType.MINUS,
                '*': TokenType.MULTIPLY,
                '/': TokenType.DIVIDE,
                '%': TokenType.MODULO,
                '<': TokenType.LESS,
                '>': TokenType.GREATER,
                '!': TokenType.NOT,
                '.': TokenType.DOT,
                ':': TokenType.COLON,
            }
            if char in single_tokens:
                self.advance()
                self.add_token(single_tokens[char], char)
                continue

            if char == '"':
                self.advance()
                start_line, start_col = self.line, self.column
                value = ""
                while self.position < len(self.source) and self.peek() != '"':
                    if self.peek() == '\\':
                        self.advance()
                        esc = self.advance()
                        value += {'n': '\n', 't': '\t', 'r': '\r', '\\': '\\', '"': '"', '0': '\0'}.get(esc, esc)
                    else:
                        value += self.advance()
                if self.position >= len(self.source):
                    self.error("Unterminated string literal")
                self.advance()
                self.tokens.append(Token(TokenType.STRING, value, start_line, start_col))
                continue

            if char == "'":
                self.advance()
                start_line, start_col = self.line, self.column
                value = ""
                if self.peek() == '\\':
                    self.advance()
                    esc = self.advance()
                    value = {'n': '\n', 't': '\t', 'r': '\r', '\\': '\\', '"': '"', '0': '\0', "'": "'"}.get(esc, esc)
                else:
                    value = self.advance()
                if self.peek() != "'":
                    self.error("Unterminated char literal")
                self.advance()
                self.tokens.append(Token(TokenType.CHAR, value, start_line, start_col))
                continue

            if char.isdigit():
                start_line, start_col = self.line, self.column
                value = ""
                while self.position < len(self.source) and self.peek().isdigit():
                    value += self.advance()
                if self.peek() == '.' and self.peek(1).isdigit():
                    value += self.advance()
                    while self.position < len(self.source) and self.peek().isdigit():
                        value += self.advance()
                    self.tokens.append(Token(TokenType.FLOAT, float(value), start_line, start_col))
                else:
                    self.tokens.append(Token(TokenType.NUMBER, int(value), start_line, start_col))
                continue

            if char.isalpha() or char == '_':
                start_line, start_col = self.line, self.column
                value = ""
                while self.position < len(self.source) and (self.peek().isalnum() or self.peek() == '_'):
                    value += self.advance()
                if value in KEYWORDS:
                    self.tokens.append(Token(KEYWORDS[value], value, start_line, start_col))
                elif value in TYPES:
                    self.tokens.append(Token(TokenType.TYPE, value, start_line, start_col))
                else:
                    self.tokens.append(Token(TokenType.IDENTIFIER, value, start_line, start_col))
                continue

            self.error(f"Unexpected character: {char!r}")

        self.add_token(TokenType.EOF, None)
        return self.tokens

# =============================================================================
# AST NODES
# =============================================================================

@dataclass
class Program:
    declarations: List[Any]

@dataclass
class ImportStmt:
    path: str

@dataclass
class FuncDecl:
    name: str
    params: List[Tuple[str, str]]
    return_type: Optional[str]
    body: 'Block'
    is_pub: bool = False

@dataclass
class StructDecl:
    name: str
    fields: List[Tuple[str, str]]
    is_pub: bool = False

@dataclass
class Block:
    statements: List[Any]

@dataclass
class VarDecl:
    name: str
    var_type: str
    initializer: Optional[Any] = None

@dataclass
class Assignment:
    target: Any
    value: Any

@dataclass
class IfStmt:
    condition: Any
    then_branch: Block
    elseifs: List[Tuple[Any, Block]]
    else_branch: Optional[Block]

@dataclass
class ForStmt:
    init: Optional[Any]
    condition: Optional[Any]
    increment: Optional[Any]
    body: Block

@dataclass
class ForEachStmt:
    var_name: str
    iterable: Any
    body: Block

@dataclass
class ReturnStmt:
    value: Optional[Any]

@dataclass
class BreakStmt:
    pass

@dataclass
class ContinueStmt:
    pass

@dataclass
class ExprStmt:
    expr: Any

@dataclass
class BinaryOp:
    op: str
    left: Any
    right: Any

@dataclass
class UnaryOp:
    op: str
    operand: Any

@dataclass
class CallExpr:
    name: str
    args: List[Any]

@dataclass
class GetExpr:
    obj: Any
    field: str

@dataclass
class IndexExpr:
    obj: Any
    index: Any

@dataclass
class Identifier:
    name: str

@dataclass
class NumberLiteral:
    value: int

@dataclass
class FloatLiteral:
    value: float

@dataclass
class StringLiteral:
    value: str

@dataclass
class CharLiteral:
    value: str

@dataclass
class BoolLiteral:
    value: bool

@dataclass
class ArrayLiteral:
    elements: List[Any]

# =============================================================================
# PARSER
# =============================================================================

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0

    def current(self) -> Token:
        return self.tokens[self.position]

    def peek(self, offset: int = 0) -> Token:
        pos = self.position + offset
        if pos >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[pos]

    def advance(self) -> Token:
        tok = self.current()
        if self.position < len(self.tokens) - 1:
            self.position += 1
        return tok

    def expect(self, type: TokenType, msg: str = None) -> Token:
        if self.current().type != type:
            raise SyntaxError(
                f"Expected {type.name} but got {self.current().type.name}"
                f"{(' (' + msg + ')') if msg else ''} at line {self.current().line}"
            )
        return self.advance()

    def match(self, *types: TokenType) -> bool:
        return self.current().type in types

    def parse_identifier(self) -> Token:
        if self.match(TokenType.IDENTIFIER, TokenType.MAIN, TokenType.GET):
            return self.advance()
        raise SyntaxError(f"Expected identifier but got {self.current().type.name} at line {self.current().line}")

    def parse(self) -> Program:
        declarations = []
        while not self.match(TokenType.EOF):
            declarations.append(self.parse_declaration())
        return Program(declarations)

    def parse_declaration(self):
        is_pub = False
        if self.match(TokenType.PUB):
            self.advance()
            is_pub = True

        if self.match(TokenType.STRUCT):
            return self.parse_struct_decl(is_pub)
        elif self.match(TokenType.GET):
            return self.parse_import_stmt()
        else:
            return self.parse_func_decl(is_pub)

    def parse_import_stmt(self) -> ImportStmt:
        self.expect(TokenType.GET)
        self.expect(TokenType.LPAREN)
        path = self.expect(TokenType.STRING).value
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.SEMICOLON)
        return ImportStmt(path)

    def parse_struct_decl(self, is_pub: bool) -> StructDecl:
        self.expect(TokenType.STRUCT)
        name = self.parse_identifier().value
        self.expect(TokenType.LBRACE)
        fields = []
        while not self.match(TokenType.RBRACE):
            # C-style: type name;
            ftype = self.parse_type()
            fname = self.parse_identifier().value
            self.expect(TokenType.SEMICOLON)
            fields.append((fname, ftype))
        self.expect(TokenType.RBRACE)
        return StructDecl(name, fields, is_pub)

    def parse_func_decl(self, is_pub: bool) -> FuncDecl:
        name = self.parse_identifier().value
        self.expect(TokenType.LPAREN)
        params = []
        if not self.match(TokenType.RPAREN):
            params.append(self.parse_param())
            while self.match(TokenType.COMMA):
                self.advance()
                params.append(self.parse_param())
        self.expect(TokenType.RPAREN)

        return_type = None
        if self.match(TokenType.OUT):
            self.advance()
            return_type = self.parse_type()

        body = self.parse_block()
        return FuncDecl(name, params, return_type, body, is_pub)

    def parse_param(self) -> Tuple[str, str]:
        if self.match(TokenType.IN):
            self.advance()
        # C-style: type name
        ptype = self.parse_type()
        name = self.parse_identifier().value
        return (name, ptype)

    def parse_type(self) -> str:
        if self.match(TokenType.TYPE):
            base = self.advance().value
        elif self.match(TokenType.IDENTIFIER):
            base = self.advance().value
        else:
            raise SyntaxError(f"Expected type at line {self.current().line}")
        if self.match(TokenType.LBRACKET):
            self.advance()
            self.expect(TokenType.RBRACKET)
            base += "[]"
        return base

    def parse_block(self) -> Block:
        self.expect(TokenType.LBRACE)
        statements = []
        while not self.match(TokenType.RBRACE):
            statements.append(self.parse_statement())
        self.expect(TokenType.RBRACE)
        return Block(statements)

    def parse_statement(self):
        if self.match(TokenType.IF):
            return self.parse_if_stmt()
        if self.match(TokenType.FOR):
            return self.parse_for_stmt()
        if self.match(TokenType.OUT):
            return self.parse_return_stmt()
        if self.match(TokenType.RETURN):
            return self.parse_return_stmt()
        if self.match(TokenType.BREAK):
            self.advance()
            self.expect(TokenType.SEMICOLON)
            return BreakStmt()
        if self.match(TokenType.CONTINUE):
            self.advance()
            self.expect(TokenType.SEMICOLON)
            return ContinueStmt()
        if self.match(TokenType.GET):
            return self.parse_import_stmt()

        # Variable declaration: type name -> value;  OR  name type -> value;
        if self.match(TokenType.IDENTIFIER, TokenType.MAIN, TokenType.GET, TokenType.TYPE):
            if self.peek(1).type == TokenType.TYPE or self.peek(1).type == TokenType.IDENTIFIER:
                return self.parse_var_decl()
            expr = self.parse_expression()
            if self.match(TokenType.ASSIGN):
                self.advance()
                value = self.parse_expression()
                self.expect(TokenType.SEMICOLON)
                return Assignment(expr, value)
            self.expect(TokenType.SEMICOLON)
            return ExprStmt(expr)

        expr = self.parse_expression()
        self.expect(TokenType.SEMICOLON)
        return ExprStmt(expr)

    def parse_var_decl(self) -> VarDecl:
        # C-style: type name -> value;  (primary)
        # Also supports: name type -> value;  (legacy)
        if self.match(TokenType.TYPE):
            vtype = self.parse_type()
            name = self.parse_identifier().value
        else:
            name = self.parse_identifier().value
            vtype = self.parse_type()
        init = None
        if self.match(TokenType.ASSIGN):
            self.advance()
            init = self.parse_expression()
        self.expect(TokenType.SEMICOLON)
        return VarDecl(name, vtype, init)

    def parse_if_stmt(self) -> IfStmt:
        self.expect(TokenType.IF)
        condition = self.parse_expression()
        then_branch = self.parse_block()
        elseifs = []
        while self.match(TokenType.ELSEIF):
            self.advance()
            cond = self.parse_expression()
            block = self.parse_block()
            elseifs.append((cond, block))
        else_branch = None
        if self.match(TokenType.ELSE):
            self.advance()
            else_branch = self.parse_block()
        self.expect(TokenType.END)
        return IfStmt(condition, then_branch, elseifs, else_branch)

    def parse_for_stmt(self):
        self.expect(TokenType.FOR)
        if self.match(TokenType.IDENTIFIER, TokenType.MAIN, TokenType.GET) and self.peek(1).type == TokenType.IN:
            var_name = self.parse_identifier().value
            self.advance()  # consume 'in'
            iterable = self.parse_expression()
            body = self.parse_block()
            self.expect(TokenType.END)
            return ForEachStmt(var_name, iterable, body)

        init = None
        if not self.match(TokenType.SEMICOLON):
            if (self.match(TokenType.IDENTIFIER, TokenType.MAIN, TokenType.GET, TokenType.TYPE) and
               (self.peek(1).type == TokenType.TYPE or self.peek(1).type == TokenType.IDENTIFIER)):
                init = self.parse_var_decl()
            else:
                init = self.parse_expression()
                if self.match(TokenType.ASSIGN):
                    self.advance()
                    val = self.parse_expression()
                    init = Assignment(init, val)
                self.expect(TokenType.SEMICOLON)

        if init is None or isinstance(init, (VarDecl, Assignment)):
            if init is None:
                self.expect(TokenType.SEMICOLON)

        condition = None
        if not self.match(TokenType.SEMICOLON):
            condition = self.parse_expression()
        self.expect(TokenType.SEMICOLON)

        increment = None
        if not self.match(TokenType.LBRACE):
            increment = self.parse_expression()
            if self.match(TokenType.ASSIGN):
                self.advance()
                val = self.parse_expression()
                increment = Assignment(increment, val)

        body = self.parse_block()
        self.expect(TokenType.END)
        return ForStmt(init, condition, increment, body)

    def parse_return_stmt(self) -> ReturnStmt:
        if self.match(TokenType.OUT):
            self.advance()
        elif self.match(TokenType.RETURN):
            self.advance()
        value = None
        if not self.match(TokenType.SEMICOLON):
            value = self.parse_expression()
        self.expect(TokenType.SEMICOLON)
        return ReturnStmt(value)

    def parse_expression(self):
        return self.parse_or()

    def parse_or(self):
        left = self.parse_and()
        while self.match(TokenType.OR):
            op = self.advance().value
            right = self.parse_and()
            left = BinaryOp(op, left, right)
        return left

    def parse_and(self):
        left = self.parse_equality()
        while self.match(TokenType.AND):
            op = self.advance().value
            right = self.parse_equality()
            left = BinaryOp(op, left, right)
        return left

    def parse_equality(self):
        left = self.parse_comparison()
        while self.match(TokenType.EQUAL, TokenType.NOTEQUAL):
            op = self.advance().value
            right = self.parse_comparison()
            left = BinaryOp(op, left, right)
        return left

    def parse_comparison(self):
        left = self.parse_term()
        while self.match(TokenType.LESS, TokenType.LESSEQUAL, TokenType.GREATER, TokenType.GREATEREQUAL):
            op = self.advance().value
            right = self.parse_term()
            left = BinaryOp(op, left, right)
        return left

    def parse_term(self):
        left = self.parse_factor()
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op = self.advance().value
            right = self.parse_factor()
            left = BinaryOp(op, left, right)
        return left

    def parse_factor(self):
        left = self.parse_unary()
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            op = self.advance().value
            right = self.parse_unary()
            left = BinaryOp(op, left, right)
        return left

    def parse_unary(self):
        if self.match(TokenType.NOT, TokenType.MINUS):
            op = self.advance().value
            operand = self.parse_unary()
            return UnaryOp(op, operand)
        return self.parse_postfix()

    def parse_postfix(self):
        expr = self.parse_primary()
        while True:
            if self.match(TokenType.LPAREN):
                expr = self.parse_call(expr)
            elif self.match(TokenType.LBRACKET):
                self.advance()
                index = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                expr = IndexExpr(expr, index)
            elif self.match(TokenType.DOT):
                self.advance()
                field = self.parse_identifier().value
                expr = GetExpr(expr, field)
            elif self.match(TokenType.PLUSPLUS):
                self.advance()
                expr = UnaryOp('++', expr)
            else:
                break
        return expr

    def parse_call(self, callee):
        self.expect(TokenType.LPAREN)
        args = []
        if not self.match(TokenType.RPAREN):
            args.append(self.parse_expression())
            while self.match(TokenType.COMMA):
                self.advance()
                args.append(self.parse_expression())
        self.expect(TokenType.RPAREN)
        name = callee.name if isinstance(callee, Identifier) else None
        return CallExpr(name, args)

    def parse_primary(self):
        if self.match(TokenType.NUMBER):
            return NumberLiteral(self.advance().value)
        if self.match(TokenType.FLOAT):
            return FloatLiteral(self.advance().value)
        if self.match(TokenType.STRING):
            return StringLiteral(self.advance().value)
        if self.match(TokenType.CHAR):
            return CharLiteral(self.advance().value)
        if self.match(TokenType.IDENTIFIER, TokenType.MAIN, TokenType.GET):
            return Identifier(self.advance().value)
        if self.match(TokenType.LPAREN):
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr
        if self.match(TokenType.LBRACKET):
            return self.parse_array_literal()
        raise SyntaxError(f"Unexpected token {self.current().type.name} at line {self.current().line}")

    def parse_array_literal(self):
        self.expect(TokenType.LBRACKET)
        elements = []
        if not self.match(TokenType.RBRACKET):
            elements.append(self.parse_expression())
            while self.match(TokenType.COMMA):
                self.advance()
                elements.append(self.parse_expression())
        self.expect(TokenType.RBRACKET)
        return ArrayLiteral(elements)

# =============================================================================
# C CODE GENERATOR
# =============================================================================

class CGenerator:
    def __init__(self):
        self.output = []
        self.indent_level = 0
        self.structs = {}
        self.functions = {}
        self.local_vars = []

    def indent(self):
        return "    " * self.indent_level

    def emit(self, line: str = ""):
        if line:
            self.output.append(self.indent() + line)
        else:
            self.output.append("")

    def generate(self, program: Program) -> str:
        # Deduplicate while building lookup tables
        seen_structs = set()
        seen_funcs = set()
        for decl in program.declarations:
            if isinstance(decl, StructDecl):
                if decl.name not in seen_structs:
                    seen_structs.add(decl.name)
                    self.structs[decl.name] = decl
            elif isinstance(decl, FuncDecl):
                if decl.name not in seen_funcs:
                    seen_funcs.add(decl.name)
                    self.functions[decl.name] = decl

        self.emit("#include <stdio.h>")
        self.emit("#include <stdlib.h>")
        self.emit("#include <string.h>")
        self.emit("#include <stdint.h>")
        self.emit("#include <stdbool.h>")
        self.emit("")

        # Struct declarations first
        for name in self.structs:
            self.emit_struct_decl(self.structs[name])
        self.emit("")

        # Forward declarations
        for name in self.functions:
            self.emit_forward_decl(self.functions[name])
        self.emit("")

        # Function definitions
        for name in self.functions:
            self.emit_func_decl(self.functions[name])

        return "\n".join(self.output)

    def emit_forward_decl(self, decl: FuncDecl):
        rtype = self.map_type(decl.return_type) if decl.return_type else "void"
        params = ", ".join(f"{self.map_type(t)} {n}" for n, t in decl.params) if decl.params else "void"
        self.emit(f"{rtype} {decl.name}({params});")

    def emit_struct_decl(self, decl: StructDecl):
        self.emit(f"typedef struct {decl.name} {decl.name};")
        self.emit(f"struct {decl.name} {{")
        self.indent_level += 1
        for fname, ftype in decl.fields:
            self.emit(f"{self.map_type(ftype)} {fname};")
        self.indent_level -= 1
        self.emit("};")

    def emit_func_decl(self, decl: FuncDecl):
        rtype = self.map_type(decl.return_type) if decl.return_type else "void"
        params = ", ".join(f"{self.map_type(t)} {n}" for n, t in decl.params) if decl.params else "void"
        self.emit(f"{rtype} {decl.name}({params}) {{")
        self.indent_level += 1
        self.local_vars = [{}]
        for stmt in decl.body.statements:
            self.emit_stmt(stmt)
        self.indent_level -= 1
        self.emit("}")
        self.emit("")

    def map_type(self, sol_type: str) -> str:
        if sol_type is None:
            return "void"
        if sol_type.endswith("[]"):
            base = sol_type[:-2]
            return f"{self.map_type(base)}*"
        mapping = {
            'int': 'int',
            'float': 'float',
            'double': 'double',
            'char': 'char',
            'bool': 'bool',
            'string': 'char*',
            'void': 'void',
            'int8': 'int8_t',
            'int16': 'int16_t',
            'int32': 'int32_t',
            'int64': 'int64_t',
            'uint8': 'uint8_t',
            'uint16': 'uint16_t',
            'uint32': 'uint32_t',
            'uint64': 'uint64_t',
            'long': 'long',
            'short': 'short',
            'byte': 'unsigned char',
        }
        return mapping.get(sol_type, sol_type)

    def emit_stmt(self, stmt):
        if isinstance(stmt, VarDecl):
            self.emit_var_decl(stmt)
        elif isinstance(stmt, Assignment):
            target = self.emit_expr(stmt.target)
            value = self.emit_expr(stmt.value)
            self.emit(f"{target} = {value};")
        elif isinstance(stmt, IfStmt):
            self.emit_if_stmt(stmt)
        elif isinstance(stmt, ForStmt):
            self.emit_for_stmt(stmt)
        elif isinstance(stmt, ForEachStmt):
            self.emit_foreach_stmt(stmt)
        elif isinstance(stmt, ReturnStmt):
            if stmt.value:
                self.emit(f"return {self.emit_expr(stmt.value)};")
            else:
                self.emit("return;")
        elif isinstance(stmt, BreakStmt):
            self.emit("break;")
        elif isinstance(stmt, ContinueStmt):
            self.emit("continue;")
        elif isinstance(stmt, ExprStmt):
            self.emit(f"{self.emit_expr(stmt.expr)};")
        elif isinstance(stmt, Block):
            self.emit_block(stmt)
        else:
            raise RuntimeError(f"Unknown statement type: {type(stmt)}")

    def _emit_var_init(self, stmt: VarDecl) -> str:
        """Generate the initialization part of a variable declaration."""
        ctype = self.map_type(stmt.var_type)
        if stmt.initializer:
            if isinstance(stmt.initializer, ArrayLiteral):
                elements = ", ".join(self.emit_expr(e) for e in stmt.initializer.elements)
                base_type = self.map_type(stmt.var_type[:-2])  # strip "[]"
                return f"{ctype} {stmt.name} = ({base_type}[]){{{elements}}}"
            else:
                init = self.emit_expr(stmt.initializer)
                if isinstance(stmt.initializer, NumberLiteral):
                    init = self.emit_unsigned_literal(stmt.initializer.value, stmt.var_type)
                return f"{ctype} {stmt.name} = {init}"
        else:
            return f"{ctype} {stmt.name}"

    def emit_var_decl(self, stmt: VarDecl):
        self.emit(self._emit_var_init(stmt) + ";")
        self.local_vars[-1][stmt.name] = stmt.var_type

    def emit_unsigned_literal(self, value: int, sol_type: str) -> str:
        if sol_type in ('uint8', 'uint16', 'uint32'):
            return f"{value}U"
        if sol_type == 'uint64':
            return f"{value}ULL"
        return str(value)

    def emit_if_stmt(self, stmt: IfStmt):
        cond = self.emit_expr(stmt.condition)
        self.emit(f"if ({cond}) {{")
        self.indent_level += 1
        for s in stmt.then_branch.statements:
            self.emit_stmt(s)
        self.indent_level -= 1
        self.emit("}")
        for cond, block in stmt.elseifs:
            c = self.emit_expr(cond)
            self.emit(f"else if ({c}) {{")
            self.indent_level += 1
            for s in block.statements:
                self.emit_stmt(s)
            self.indent_level -= 1
            self.emit("}")
        if stmt.else_branch:
            self.emit("else {")
            self.indent_level += 1
            for s in stmt.else_branch.statements:
                self.emit_stmt(s)
            self.indent_level -= 1
            self.emit("}")

    def emit_for_stmt(self, stmt: ForStmt):
        parts = []
        if stmt.init:
            if isinstance(stmt.init, VarDecl):
                parts.append(self._emit_var_init(stmt.init))
            elif isinstance(stmt.init, Assignment):
                parts.append(f"{self.emit_expr(stmt.init.target)} = {self.emit_expr(stmt.init.value)}")
            else:
                parts.append(self.emit_expr(stmt.init))
        else:
            parts.append("")
        parts.append(self.emit_expr(stmt.condition) if stmt.condition else "")
        if stmt.increment:
            if isinstance(stmt.increment, Assignment):
                parts.append(f"{self.emit_expr(stmt.increment.target)} = {self.emit_expr(stmt.increment.value)}")
            else:
                parts.append(self.emit_expr(stmt.increment))
        else:
            parts.append("")
        self.emit(f"for ({parts[0]}; {parts[1]}; {parts[2]}) {{")
        self.indent_level += 1
        for s in stmt.body.statements:
            self.emit_stmt(s)
        self.indent_level -= 1
        self.emit("}")

    def emit_foreach_stmt(self, stmt: ForEachStmt):
        self.emit(f"// foreach: {stmt.var_name} in iterable")
        self.emit("{")
        self.indent_level += 1
        for s in stmt.body.statements:
            self.emit_stmt(s)
        self.indent_level -= 1
        self.emit("}")

    def emit_block(self, block: Block):
        self.emit("{")
        self.indent_level += 1
        for stmt in block.statements:
            self.emit_stmt(stmt)
        self.indent_level -= 1
        self.emit("}")

    def emit_expr(self, expr) -> str:
        if isinstance(expr, NumberLiteral):
            return str(expr.value)
        if isinstance(expr, FloatLiteral):
            return str(expr.value)
        if isinstance(expr, StringLiteral):
            escaped = expr.value.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\t', '\\t')
            return f'"{escaped}"'
        if isinstance(expr, CharLiteral):
            return f"'{expr.value}'"
        if isinstance(expr, BoolLiteral):
            return "true" if expr.value else "false"
        if isinstance(expr, Identifier):
            return expr.name
        if isinstance(expr, BinaryOp):
            left = self.emit_expr(expr.left)
            right = self.emit_expr(expr.right)
            return f"{left} {expr.op} {right}"
        if isinstance(expr, UnaryOp):
            operand = self.emit_expr(expr.operand)
            if expr.op == '++':
                return f"{operand}++"
            return f"{expr.op}{operand}"
        if isinstance(expr, CallExpr):
            args = ", ".join(self.emit_expr(a) for a in expr.args)
            return f"{expr.name}({args})"
        if isinstance(expr, GetExpr):
            obj = self.emit_expr(expr.obj)
            return f"{obj}.{expr.field}"
        if isinstance(expr, IndexExpr):
            obj = self.emit_expr(expr.obj)
            index = self.emit_expr(expr.index)
            return f"{obj}[{index}]"
        if isinstance(expr, ArrayLiteral):
            elements = ", ".join(self.emit_expr(e) for e in expr.elements)
            return f"{{{elements}}}"
        raise RuntimeError(f"Unknown expression type: {type(expr)}")

# =============================================================================
# IMPORT RESOLVER
# =============================================================================

class ImportResolver:
    """Resolves get("path") imports by recursively loading and merging Sol files."""

    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.loaded = set()
        self.all_declarations = []
        self.seen_funcs = set()
        self.seen_structs = set()

    def resolve(self, source_path: str) -> Program:
        self._load_file(source_path)
        return Program(self.all_declarations)

    def _resolve_path(self, path: str) -> str:
        if os.path.isabs(path):
            return path
        return os.path.normpath(os.path.join(self.base_dir, path))

    def _load_file(self, source_path: str):
        abs_path = self._resolve_path(source_path)
        abs_path = os.path.abspath(abs_path)

        if abs_path in self.loaded:
            return
        self.loaded.add(abs_path)

        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"Import not found: {source_path} (resolved to {abs_path})")

        with open(abs_path, 'r') as f:
            source = f.read()

        lexer = Lexer(source)
        tokens = lexer.tokenize()

        parser = Parser(tokens)
        ast = parser.parse()

        file_dir = os.path.dirname(abs_path)

        for decl in ast.declarations:
            if isinstance(decl, ImportStmt):
                imported_path = decl.path
                if not os.path.isabs(imported_path):
                    imported_path = os.path.join(file_dir, imported_path)
                self._load_file(imported_path)
            elif isinstance(decl, FuncDecl):
                if decl.name not in self.seen_funcs:
                    self.seen_funcs.add(decl.name)
                    self.all_declarations.append(decl)
            elif isinstance(decl, StructDecl):
                if decl.name not in self.seen_structs:
                    self.seen_structs.add(decl.name)
                    self.all_declarations.append(decl)
            else:
                self.all_declarations.append(decl)

# =============================================================================
# DRIVER
# =============================================================================

def find_c_compiler() -> str:
    for compiler in ['clang', 'gcc', 'cc']:
        try:
            subprocess.run([compiler, '--version'], capture_output=True, check=False)
            return compiler
        except FileNotFoundError:
            continue
    raise RuntimeError("No C compiler found (tried: clang, gcc, cc). Please install clang or gcc.")

def compile_sol(source_path: str, run: bool = False, keep_c: bool = False) -> str:
    base_dir = os.path.dirname(os.path.abspath(source_path)) or os.getcwd()

    resolver = ImportResolver(base_dir)
    ast = resolver.resolve(source_path)

    generator = CGenerator()
    c_code = generator.generate(ast)

    base = os.path.splitext(source_path)[0]
    c_path = base + ".c"
    with open(c_path, 'w') as f:
        f.write(c_code)
    print(f"Generated C code: {c_path}")

    compiler = find_c_compiler()
    exe_path = base
    if sys.platform == 'win32':
        exe_path += ".exe"

    cmd = [compiler, c_path, "-o", exe_path, "-Wall", "-Wextra", "-std=c11"]
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("Compilation failed:")
        print(result.stderr)
        raise RuntimeError("Compilation failed")

    # FIX: Make executable on Unix-like systems — catch ALL exceptions, OR permissions
    if sys.platform != 'win32':
        try:
            current_mode = os.stat(exe_path).st_mode
            os.chmod(exe_path, current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
            print(f"Set executable permissions on {exe_path}")
        except Exception as e:
            print(f"Warning: Could not chmod {exe_path}: {e}")

    print(f"Compiled executable: {exe_path}")

    if not keep_c:
        os.remove(c_path)
        print(f"Removed intermediate C file: {c_path}")

    if run:
        # Ensure executable permissions before running, then run with ./ prefix
        if sys.platform != 'win32':
            try:
                current_mode = os.stat(exe_path).st_mode
                if not (current_mode & stat.S_IXUSR):
                    os.chmod(exe_path, current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
                    print(f"Set executable permissions before running")
            except Exception as e:
                print(f"Warning: Could not ensure executable permissions: {e}")
        
        print(f"\n--- Running {exe_path} ---")
        result = subprocess.run([f"./{os.path.basename(exe_path)}"], 
                              capture_output=True, text=True,
                              cwd=os.path.dirname(exe_path) or '.')
        print(result.stdout, end="")
        if result.stderr:
            print("stderr:", result.stderr, end="")
        print(f"--- Exit code: {result.returncode} ---")

    return exe_path

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    source_path = sys.argv[1]
    run = '--run' in sys.argv
    keep_c = '--keep-c' in sys.argv

    if not os.path.exists(source_path):
        print(f"Error: File not found: {source_path}")
        sys.exit(1)

    compile_sol(source_path, run=run, keep_c=keep_c)

if __name__ == "__main__":
    main()