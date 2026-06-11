import unittest

from src.lexer import Lexer, LexicalError


class LexerTest(unittest.TestCase):
    def token_types(self, source: str) -> list[str]:
        return [token.type for token in Lexer(source).tokenize().tokens]

    def test_recognizes_keywords_identifiers_constants_and_symbols(self) -> None:
        source = 'def principal() { int A; A = 10 + 2.5; print "ok"; }'

        self.assertEqual(
            self.token_types(source),
            [
                "def",
                "ident",
                "(",
                ")",
                "{",
                "int",
                "ident",
                ";",
                "ident",
                "=",
                "int_constant",
                "+",
                "float_constant",
                ";",
                "print",
                "string_constant",
                ";",
                "}",
                "EOF",
            ],
        )

    def test_symbol_table_tracks_identifier_occurrences(self) -> None:
        result = Lexer("int A;\nA = B;").tokenize()

        self.assertEqual(result.symbol_table["A"].occurrences, [(1, 5), (2, 1)])
        self.assertEqual(result.symbol_table["B"].occurrences, [(2, 5)])

    def test_invalid_character_reports_position(self) -> None:
        with self.assertRaises(LexicalError) as context:
            Lexer("int A;\n@").tokenize()

        self.assertEqual(context.exception.line, 2)
        self.assertEqual(context.exception.column, 1)

    def test_unclosed_string_reports_lexical_error(self) -> None:
        with self.assertRaises(LexicalError):
            Lexer('print "sem fim').tokenize()

    def test_malformed_float_reports_lexical_error(self) -> None:
        with self.assertRaises(LexicalError):
            Lexer("A = 12.;").tokenize()


if __name__ == "__main__":
    unittest.main()
