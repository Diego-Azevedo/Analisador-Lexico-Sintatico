import unittest

from src.grammar import build_parse_table, compute_first_sets, compute_follow_sets
from src.lexer import Lexer
from src.parser import Parser, SyntaxErrorInfo


class ParserTest(unittest.TestCase):
    def parse_source(self, source: str) -> None:
        tokens = Lexer(source).tokenize().tokens
        Parser(tokens).parse()

    def test_builds_parse_table_without_conflicts(self) -> None:
        table, conflicts = build_parse_table()

        self.assertFalse(conflicts)
        self.assertIn(("PROGRAM", "def"), table)
        self.assertIn(("STATEMENT", "ident"), table)

    def test_computes_first_and_follow_sets(self) -> None:
        first = compute_first_sets()
        follow = compute_follow_sets()

        self.assertIn("def", first["PROGRAM"])
        self.assertIn("EOF", follow["PROGRAM"])
        self.assertIn("}", follow["STATELIST"])

    def test_accepts_valid_function_program(self) -> None:
        self.parse_source(
            """
            def soma(int A, int B) {
                int R;
                R = A + B;
                print R;
                return;
            }
            def principal() {
                int X;
                int Y;
                int Z;
                X = 1;
                Y = 2;
                Z = soma(X, Y);
                return;
            }
            """
        )

    def test_accepts_control_flow_and_allocation(self) -> None:
        self.parse_source(
            """
            def principal() {
                int A[10];
                int I;
                I = 0;
                for(I = 0; I < 10; I = I + 1) {
                    A[I] = I * 2;
                }
                if (I >= 10) print I; else print 0;
                return;
            }
            """
        )

    def test_rejects_missing_semicolon(self) -> None:
        with self.assertRaises(SyntaxErrorInfo):
            self.parse_source(
                """
                def principal() {
                    int A
                    return;
                }
                """
            )


if __name__ == "__main__":
    unittest.main()
