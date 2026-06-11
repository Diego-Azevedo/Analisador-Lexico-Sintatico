from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass


EPSILON = "EPSILON"
EOF = "EOF"
START_SYMBOL = "PROGRAM"


Production = tuple[str, ...]
Grammar = dict[str, list[Production]]
FirstSets = dict[str, set[str]]
FollowSets = dict[str, set[str]]
ParseTable = dict[tuple[str, str], Production]


GRAMMAR: Grammar = {
    "PROGRAM": [("PROGRAM_CONTENT",), (EPSILON,)],
    "PROGRAM_CONTENT": [("FUNCLIST",), ("STATEMENT",)],
    "FUNCLIST": [("FUNCDEF", "FUNCLIST_TAIL")],
    "FUNCLIST_TAIL": [("FUNCDEF", "FUNCLIST_TAIL"), (EPSILON,)],
    "FUNCDEF": [("def", "ident", "(", "PARAMLIST", ")", "{", "STATELIST", "}")],
    "PARAMLIST": [("TYPE", "ident", "PARAMLIST_TAIL"), (EPSILON,)],
    "PARAMLIST_TAIL": [(",", "PARAMLIST"), (EPSILON,)],
    "TYPE": [("int",), ("float",), ("string",)],
    "STATEMENT": [
        ("VARDECL", ";"),
        ("ATRIBSTAT", ";"),
        ("PRINTSTAT", ";"),
        ("READSTAT", ";"),
        ("RETURNSTAT", ";"),
        ("IFSTAT",),
        ("FORSTAT",),
        ("BLOCK",),
        ("break", ";"),
        (";",),
    ],
    "BLOCK": [("{", "STATELIST", "}")],
    "VARDECL": [("TYPE", "ident", "ARRAY_DECLS")],
    "ARRAY_DECLS": [("[", "int_constant", "]", "ARRAY_DECLS"), (EPSILON,)],
    "ATRIBSTAT": [("LVALUE", "=", "ATRIB_VALUE")],
    "ATRIB_VALUE": [("ALLOCEXPRESSION",), ("EXPRESSION",)],
    "PRINTSTAT": [("print", "EXPRESSION")],
    "READSTAT": [("read", "LVALUE")],
    "RETURNSTAT": [("return",)],
    "IFSTAT": [("if", "(", "EXPRESSION", ")", "STATEMENT", "ELSE_PART")],
    "ELSE_PART": [("else", "STATEMENT"), (EPSILON,)],
    "FORSTAT": [("for", "(", "ATRIBSTAT", ";", "EXPRESSION", ";", "ATRIBSTAT", ")", "STATEMENT")],
    "STATELIST": [("STATEMENT", "STATELIST"), (EPSILON,)],
    "ALLOCEXPRESSION": [("new", "TYPE", "ALLOC_DIMS")],
    "ALLOC_DIMS": [("[", "NUMEXPRESSION", "]", "ALLOC_DIMS_TAIL")],
    "ALLOC_DIMS_TAIL": [("[", "NUMEXPRESSION", "]", "ALLOC_DIMS_TAIL"), (EPSILON,)],
    "EXPRESSION": [("NUMEXPRESSION", "EXPRESSION_TAIL")],
    "EXPRESSION_TAIL": [("RELOP", "NUMEXPRESSION"), (EPSILON,)],
    "RELOP": [("<",), (">",), ("<=",), (">=",), ("==",), ("!=",)],
    "NUMEXPRESSION": [("TERM", "NUMEXPRESSION_TAIL")],
    "NUMEXPRESSION_TAIL": [("+", "TERM", "NUMEXPRESSION_TAIL"), ("-", "TERM", "NUMEXPRESSION_TAIL"), (EPSILON,)],
    "TERM": [("UNARYEXPR", "TERM_TAIL")],
    "TERM_TAIL": [
        ("*", "UNARYEXPR", "TERM_TAIL"),
        ("/", "UNARYEXPR", "TERM_TAIL"),
        ("%", "UNARYEXPR", "TERM_TAIL"),
        (EPSILON,),
    ],
    "UNARYEXPR": [("+", "FACTOR"), ("-", "FACTOR"), ("FACTOR",)],
    "FACTOR": [
        ("int_constant",),
        ("float_constant",),
        ("string_constant",),
        ("null",),
        ("ident", "FACTOR_IDENT_TAIL"),
        ("(", "NUMEXPRESSION", ")"),
    ],
    "FACTOR_IDENT_TAIL": [("(", "PARAMLISTCALL", ")"), ("LVALUE_TAIL",)],
    "LVALUE": [("ident", "LVALUE_TAIL")],
    "LVALUE_TAIL": [("[", "NUMEXPRESSION", "]", "LVALUE_TAIL"), (EPSILON,)],
    "PARAMLISTCALL": [("ident", "PARAMLISTCALL_TAIL"), (EPSILON,)],
    "PARAMLISTCALL_TAIL": [(",", "PARAMLISTCALL"), (EPSILON,)],
}


@dataclass(frozen=True)
class TableConflict:
    non_terminal: str
    terminal: str
    existing: Production
    new: Production


def non_terminals(grammar: Grammar = GRAMMAR) -> set[str]:
    return set(grammar)


def terminals(grammar: Grammar = GRAMMAR) -> set[str]:
    nts = non_terminals(grammar)
    result = {EOF}
    for productions in grammar.values():
        for production in productions:
            for symbol in production:
                if symbol != EPSILON and symbol not in nts:
                    result.add(symbol)
    return result


def compute_first_sets(grammar: Grammar = GRAMMAR) -> FirstSets:
    first: FirstSets = defaultdict(set)

    for terminal in terminals(grammar):
        first[terminal].add(terminal)
    first[EPSILON].add(EPSILON)
    for nt in non_terminals(grammar):
        first[nt]

    changed = True
    while changed:
        changed = False
        for nt, productions in grammar.items():
            for production in productions:
                before = len(first[nt])
                first[nt].update(first_of_sequence(production, first))
                changed = changed or len(first[nt]) != before

    return dict(first)


def first_of_sequence(sequence: Production, first_sets: FirstSets) -> set[str]:
    result: set[str] = set()

    if not sequence or sequence == (EPSILON,):
        return {EPSILON}

    for symbol in sequence:
        symbol_first = first_sets.get(symbol, {symbol})
        result.update(symbol_first - {EPSILON})
        if EPSILON not in symbol_first:
            break
    else:
        result.add(EPSILON)

    return result


def compute_follow_sets(grammar: Grammar = GRAMMAR, start_symbol: str = START_SYMBOL) -> FollowSets:
    first = compute_first_sets(grammar)
    follow: FollowSets = defaultdict(set)
    for nt in non_terminals(grammar):
        follow[nt]
    follow[start_symbol].add(EOF)

    changed = True
    while changed:
        changed = False
        for nt, productions in grammar.items():
            for production in productions:
                for index, symbol in enumerate(production):
                    if symbol not in grammar:
                        continue
                    beta = production[index + 1 :]
                    first_beta = first_of_sequence(beta, first)
                    before = len(follow[symbol])
                    follow[symbol].update(first_beta - {EPSILON})
                    if EPSILON in first_beta or not beta:
                        follow[symbol].update(follow[nt])
                    changed = changed or len(follow[symbol]) != before

    return dict(follow)


def build_parse_table(grammar: Grammar = GRAMMAR) -> tuple[ParseTable, list[TableConflict]]:
    first = compute_first_sets(grammar)
    follow = compute_follow_sets(grammar)
    table: ParseTable = {}
    conflicts: list[TableConflict] = []

    for nt, productions in grammar.items():
        alternative_firsts = [first_of_sequence(production, first) for production in productions]
        explicit_first = set().union(*(symbols - {EPSILON} for symbols in alternative_firsts))

        for production, production_first in zip(productions, alternative_firsts):
            for terminal in production_first - {EPSILON}:
                _insert_table_entry(table, conflicts, nt, terminal, production)

            if EPSILON in production_first:
                for terminal in follow[nt] - explicit_first:
                    _insert_table_entry(table, conflicts, nt, terminal, production)

    return table, conflicts


def _insert_table_entry(
    table: ParseTable,
    conflicts: list[TableConflict],
    non_terminal: str,
    terminal: str,
    production: Production,
) -> None:
    key = (non_terminal, terminal)
    existing = table.get(key)
    if existing is not None and existing != production:
        conflicts.append(TableConflict(non_terminal, terminal, existing, production))
        return
    table[key] = production
