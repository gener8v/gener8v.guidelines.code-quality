import unittest

from cq_measure.source.lexer import blank, line_starts, scan_source


class LexerTest(unittest.TestCase):
    def test_keeps_length_and_line_breaks(self):
        text = 'const a = "x}y"; // c {\n/* b\n} */ const r = /[}]/g;\nconst t = `${a + `n}`}`;\n'
        scan = scan_source(text)
        self.assertEqual(len(scan.code), len(text))
        self.assertEqual(scan.code.count("\n"), text.count("\n"))
        self.assertNotIn("x}y", scan.code)
        self.assertEqual(scan.code.count("{"), scan.code.count("}"))

    def test_blanks_comments_and_records_them(self):
        scan = scan_source("a(); // first\n/* second\n * third */\n")
        self.assertEqual([(c.line, c.text) for c in scan.comments], [(1, "first"), (2, "second"), (3, "third")])
        self.assertNotIn("first", scan.code)

    def test_division_is_not_a_regex(self):
        scan = scan_source("const x = a / b / c;\n")
        self.assertIn("a / b / c", scan.code)

    def test_regex_literal_is_blanked(self):
        scan = scan_source("const x = /{/.test(y);\n")
        self.assertNotIn("{", scan.code)

    def test_strings_are_recorded(self):
        scan = scan_source("import x from './billing';\n")
        self.assertEqual([value for _start, _end, value in scan.strings], ["./billing"])

    def test_unterminated_string_stops_at_line_end(self):
        scan = scan_source("<p>Don't {x}</p>\nfunction f() {}\n")
        self.assertIn("function f() {}", scan.code)

    def test_char_literals_outside_script(self):
        scan = scan_source("fn f<'a>(x: &'a str) { let c = '{'; }\n", script=False)
        self.assertEqual(scan.code.count("{"), 1)

    def test_helpers(self):
        self.assertEqual(blank("ab\ncd"), "  \n  ")
        self.assertEqual(line_starts("a\nb\n"), [0, 2, 4])


if __name__ == "__main__":
    unittest.main()
