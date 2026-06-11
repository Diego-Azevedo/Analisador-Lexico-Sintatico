from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SymbolInfo:
    lexeme: str
    occurrences: list[tuple[int, int]] = field(default_factory=list)

    def add_occurrence(self, line: int, column: int) -> None:
        self.occurrences.append((line, column))


class SymbolTable:
    def __init__(self) -> None:
        self._symbols: dict[str, SymbolInfo] = {}

    def add(self, lexeme: str, line: int, column: int) -> None:
        symbol = self._symbols.setdefault(lexeme, SymbolInfo(lexeme))
        symbol.add_occurrence(line, column)

    def items(self) -> list[SymbolInfo]:
        return [self._symbols[key] for key in sorted(self._symbols)]

    def __contains__(self, lexeme: str) -> bool:
        return lexeme in self._symbols

    def __getitem__(self, lexeme: str) -> SymbolInfo:
        return self._symbols[lexeme]

    def format(self) -> str:
        if not self._symbols:
            return "(vazia)"
        lines = []
        for symbol in self.items():
            occurrences = ", ".join(f"({line}, {column})" for line, column in symbol.occurrences)
            lines.append(f"{symbol.lexeme} -> [{occurrences}]")
        return "\n".join(lines)
