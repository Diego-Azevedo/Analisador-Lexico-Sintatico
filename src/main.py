from __future__ import annotations

import sys
from pathlib import Path

from .lexer import Lexer, LexicalError, Token
from .parser import GrammarConflictError, Parser, SyntaxErrorInfo


def format_tokens(tokens: list[Token]) -> str:
    visible_tokens = [token.display() for token in tokens if token.type != "EOF"]
    return "[" + ", ".join(visible_tokens) + "]"


def run(path: Path) -> int:
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Erro ao ler arquivo '{path}': {exc}")
        return 1

    try:
        lex_result = Lexer(source).tokenize()
    except LexicalError as exc:
        print(exc)
        return 1

    print("TOKENS:")
    print(format_tokens(lex_result.tokens))
    print()
    print("SYMBOL TABLE:")
    print(lex_result.symbol_table.format())
    print()

    try:
        Parser(lex_result.tokens).parse()
    except (GrammarConflictError, SyntaxErrorInfo) as exc:
        print(exc)
        return 1

    print("Analise sintatica concluida com sucesso.")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("Uso: python -m src.main <arquivo.lcc>")
        return 1
    return run(Path(args[0]))


if __name__ == "__main__":
    raise SystemExit(main())
