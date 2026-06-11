from __future__ import annotations

from dataclasses import dataclass

from .grammar import EPSILON, EOF, GRAMMAR, START_SYMBOL, ParseTable, Production, build_parse_table
from .lexer import Token


class GrammarConflictError(Exception):
    pass


@dataclass
class SyntaxErrorInfo(Exception):
    message: str
    line: int
    column: int
    non_terminal: str | None = None
    token_type: str | None = None
    sentential_form: str | None = None

    def __str__(self) -> str:
        parts = [f"Erro sintatico na linha {self.line}, coluna {self.column}: {self.message}"]
        if self.non_terminal and self.token_type:
            parts.append(f"Entrada vazia na tabela M[{self.non_terminal}, {self.token_type}].")
        if self.sentential_form:
            parts.append(f"Forma sentencial: {self.sentential_form}")
        if self.non_terminal:
            parts.append(f"Nao-terminal mais a esquerda: {self.non_terminal}")
        if self.token_type:
            parts.append(f"Token atual: {self.token_type}")
        return "\n".join(parts)


class Parser:
    def __init__(self, tokens: list[Token], parse_table: ParseTable | None = None) -> None:
        self.tokens = tokens
        self.position = 0
        self.parse_table = parse_table if parse_table is not None else self._build_table_once()

    def parse(self) -> None:
        stack = [EOF, START_SYMBOL]

        while stack:
            top = stack.pop()
            current = self._current()

            if top == EPSILON:
                continue

            if top == current.type == EOF:
                return

            if top not in GRAMMAR:
                if top == current.type:
                    self.position += 1
                    continue
                raise SyntaxErrorInfo(
                    message=f"esperado '{top}', encontrado '{current.type}'",
                    line=current.line,
                    column=current.column,
                    token_type=current.type,
                    sentential_form=self._format_stack(stack, top),
                )

            production = self.parse_table.get((top, current.type))
            if production is None:
                raise SyntaxErrorInfo(
                    message="entrada vazia na tabela de reconhecimento sintatico",
                    line=current.line,
                    column=current.column,
                    non_terminal=top,
                    token_type=current.type,
                    sentential_form=self._format_stack(stack, top),
                )

            self._push_production(stack, production)

        current = self._current()
        if current.type != EOF:
            raise SyntaxErrorInfo(
                message=f"entrada restante apos fim da pilha: '{current.type}'",
                line=current.line,
                column=current.column,
                token_type=current.type,
            )

    def _current(self) -> Token:
        if self.position >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[self.position]

    def _push_production(self, stack: list[str], production: Production) -> None:
        if production == (EPSILON,):
            return
        for symbol in reversed(production):
            stack.append(symbol)

    def _format_stack(self, stack: list[str], current_top: str) -> str:
        pending = [current_top] + list(reversed(stack))
        return " ".join(symbol for symbol in pending if symbol != EOF)

    def _build_table_once(self) -> ParseTable:
        table, conflicts = build_parse_table()
        if conflicts:
            details = "; ".join(
                f"M[{conflict.non_terminal}, {conflict.terminal}]"
                for conflict in conflicts
            )
            raise GrammarConflictError(f"conflitos na tabela LL(1): {details}")
        return table
