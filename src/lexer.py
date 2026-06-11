from __future__ import annotations

from dataclasses import dataclass

from .symbol_table import SymbolTable


KEYWORDS = {
    "def",
    "int",
    "float",
    "string",
    "print",
    "read",
    "return",
    "if",
    "else",
    "for",
    "break",
    "new",
    "null",
}

DELIMITERS = {"(", ")", "{", "}", "[", "]", ",", ";"}
ONE_CHAR_OPERATORS = {"=", "+", "-", "*", "/", "%", "<", ">", "!"}
TWO_CHAR_OPERATORS = {"<=", ">=", "==", "!="}


@dataclass(frozen=True)
class Token:
    type: str
    lexeme: str
    line: int
    column: int

    def display(self) -> str:
        return self.lexeme if self.type == self.lexeme else self.type


class LexicalError(Exception):
    def __init__(self, message: str, line: int, column: int) -> None:
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column

    def __str__(self) -> str:
        return f"Erro lexico na linha {self.line}, coluna {self.column}: {self.message}"


@dataclass
class LexResult:
    tokens: list[Token]
    symbol_table: SymbolTable


class Lexer:
    def __init__(self, source: str) -> None:
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.symbol_table = SymbolTable()

    def tokenize(self) -> LexResult:
        tokens: list[Token] = []

        while not self._is_at_end():
            char = self._peek()

            if char in " \t\r":
                self._advance()
                continue

            if char == "\n":
                self._advance_newline()
                continue

            if char.isalpha() or char == "_":
                tokens.append(self._read_identifier_or_keyword())
                continue

            if char.isdigit():
                tokens.append(self._read_number())
                continue

            if char == '"':
                tokens.append(self._read_string())
                continue

            if char == "/" and self._peek_next() == "/":
                self._skip_line_comment()
                continue

            if char in DELIMITERS:
                tokens.append(self._make_single_char_token())
                continue

            if char in ONE_CHAR_OPERATORS:
                tokens.append(self._read_operator())
                continue

            line, column = self.line, self.column
            raise LexicalError(f"caractere invalido '{char}'", line, column)

        tokens.append(Token("EOF", "EOF", self.line, self.column))
        return LexResult(tokens, self.symbol_table)

    def _read_identifier_or_keyword(self) -> Token:
        start = self.pos
        line, column = self.line, self.column

        while not self._is_at_end() and (self._peek().isalnum() or self._peek() == "_"):
            self._advance()

        lexeme = self.source[start:self.pos]
        token_type = lexeme if lexeme in KEYWORDS else "ident"
        if token_type == "ident":
            self.symbol_table.add(lexeme, line, column)
        return Token(token_type, lexeme, line, column)

    def _read_number(self) -> Token:
        start = self.pos
        line, column = self.line, self.column

        while not self._is_at_end() and self._peek().isdigit():
            self._advance()

        if not self._is_at_end() and self._peek() == ".":
            self._advance()
            if self._is_at_end() or not self._peek().isdigit():
                lexeme = self.source[start:self.pos]
                raise LexicalError(f"float malformado '{lexeme}'", line, column)
            while not self._is_at_end() and self._peek().isdigit():
                self._advance()
            return Token("float_constant", self.source[start:self.pos], line, column)

        return Token("int_constant", self.source[start:self.pos], line, column)

    def _read_string(self) -> Token:
        line, column = self.line, self.column
        self._advance()
        chars: list[str] = []

        while not self._is_at_end() and self._peek() != '"':
            if self._peek() == "\n":
                raise LexicalError("string sem fechamento", line, column)
            if self._peek() == "\\" and self._peek_next() in {'"', "\\"}:
                self._advance()
            chars.append(self._advance())

        if self._is_at_end():
            raise LexicalError("string sem fechamento", line, column)

        self._advance()
        lexeme = '"' + "".join(chars) + '"'
        return Token("string_constant", lexeme, line, column)

    def _read_operator(self) -> Token:
        line, column = self.line, self.column
        char = self._advance()
        maybe_two = char + self._peek()

        if maybe_two in TWO_CHAR_OPERATORS:
            self._advance()
            return Token(maybe_two, maybe_two, line, column)

        if char == "!":
            raise LexicalError("operador invalido '!'", line, column)

        return Token(char, char, line, column)

    def _make_single_char_token(self) -> Token:
        line, column = self.line, self.column
        char = self._advance()
        return Token(char, char, line, column)

    def _skip_line_comment(self) -> None:
        while not self._is_at_end() and self._peek() != "\n":
            self._advance()

    def _advance(self) -> str:
        char = self.source[self.pos]
        self.pos += 1
        self.column += 1
        return char

    def _advance_newline(self) -> None:
        self.pos += 1
        self.line += 1
        self.column = 1

    def _peek(self) -> str:
        if self._is_at_end():
            return "\0"
        return self.source[self.pos]

    def _peek_next(self) -> str:
        next_pos = self.pos + 1
        if next_pos >= len(self.source):
            return "\0"
        return self.source[next_pos]

    def _is_at_end(self) -> bool:
        return self.pos >= len(self.source)
