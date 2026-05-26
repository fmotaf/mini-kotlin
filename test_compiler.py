import unittest
import sys
import io

from lexer_kt import tokenize
from parser_kt import Parser
from ast_kt import (
    Program, FunDecl, Param, VarDecl, Assignment, IfStmt, WhileStmt,
    ReturnStmt, PrintStmt, BinaryOp, UnaryOp, Literal, Identifier, FunCall
)
from semantic_kt import SemanticAnalyzer


def tokenize_full(code):
    return tokenize(code)


def parse(code):
    tokens = tokenize_full(code)
    parser = Parser(tokens)
    return parser.parse_program()


# ============================================================
# LEXER TESTS
# ============================================================

class TestLexer(unittest.TestCase):

    def assert_token(self, tokens, index, expected_type, expected_value=None):
        self.assertLess(index, len(tokens), f"Token index {index} out of range (only {len(tokens)} tokens)")
        t = tokens[index]
        self.assertEqual(t[0], expected_type, f"Token {index}: expected {expected_type}, got {t[0]} ({t[1]})")
        if expected_value is not None:
            self.assertEqual(t[1], expected_value, f"Token {index} value: expected {expected_value!r}, got {t[1]!r}")

    def test_keywords(self):
        code = "fun val var if else while return"
        tokens = tokenize_full(code)
        types = [t[0] for t in tokens if t[0] not in ('SKIP',)]
        self.assertIn('FUN', types)
        self.assertIn('VAL', types)
        self.assertIn('VAR', types)
        self.assertIn('IF', types)
        self.assertIn('ELSE', types)
        self.assertIn('WHILE', types)
        self.assertIn('RETURN', types)

    def test_logical_keywords(self):
        code = "and or not true false"
        tokens = tokenize_full(code)
        types = [t[0] for t in tokens if t[0] not in ('SKIP',)]
        self.assertIn('AND', types)
        self.assertIn('OR', types)
        self.assertIn('NOT', types)
        self.assertIn('TRUE', types)
        self.assertIn('FALSE', types)

    def test_println(self):
        tokens = tokenize_full("println(x)")
        self.assert_token(tokens, 0, 'PRINTLN', 'println')

    def test_types(self):
        code = "Int Double String Boolean Unit"
        tokens = tokenize_full(code)
        types = [t[0] for t in tokens if t[0] not in ('SKIP',)]
        for t in types:
            self.assertEqual(t, 'TYPE')

    def test_number_integer(self):
        tokens = tokenize_full("42")
        self.assert_token(tokens, 0, 'NUMBER', '42')

    def test_number_double(self):
        tokens = tokenize_full("3.14")
        self.assert_token(tokens, 0, 'NUMBER', '3.14')

    def test_string(self):
        tokens = tokenize_full('"hello"')
        self.assert_token(tokens, 0, 'STRING', '"hello"')

    def test_assign(self):
        tokens = tokenize_full("=")
        self.assert_token(tokens, 0, 'ASSIGN', '=')

    def test_eq(self):
        tokens = tokenize_full("==")
        self.assert_token(tokens, 0, 'EQ', '==')

    def test_neq(self):
        tokens = tokenize_full("!=")
        self.assert_token(tokens, 0, 'NEQ', '!=')

    def test_ge(self):
        tokens = tokenize_full(">=")
        self.assert_token(tokens, 0, 'GE', '>=')

    def test_le(self):
        tokens = tokenize_full("<=")
        self.assert_token(tokens, 0, 'LE', '<=')

    def test_gt(self):
        tokens = tokenize_full(">")
        self.assert_token(tokens, 0, 'GT', '>')

    def test_lt(self):
        tokens = tokenize_full("<")
        self.assert_token(tokens, 0, 'LT', '<')

    def test_operators(self):
        code = "+ - * / ( ) : , ."
        tokens = tokenize_full(code)
        types = [t[0] for t in tokens if t[0] not in ('SKIP',)]
        expected = ['PLUS', 'MINUS', 'STAR', 'SLASH', 'LPAREN', 'RPAREN', 'COLON', 'COMMA', 'DOT']
        for e in expected:
            self.assertIn(e, types)

    def test_identifier(self):
        tokens = tokenize_full("x _myVar")
        tokens = [t for t in tokens if t[0] not in ('SKIP',)]
        self.assert_token(tokens, 0, 'ID')
        self.assert_token(tokens, 1, 'ID')

    def test_comment(self):
        code = "// isso e um comentario\n"
        tokens = tokenize_full(code)
        self.assertEqual(len(tokens), 1)  # apenas NEWLINE

    def test_newline(self):
        tokens = tokenize_full("a\nb\n")
        newlines = [t for t in tokens if t[0] == 'NEWLINE']
        self.assertEqual(len(newlines), 2)

    def test_indent_dedent(self):
        code = "fun main()\n  val x = 1\n  val y = 2\n"
        tokens = tokenize_full(code)
        types = [t[0] for t in tokens]
        self.assertIn('INDENT', types)
        self.assertIn('DEDENT', types)

    def test_nested_indent(self):
        code = "fun main()\n  if true\n    val x = 1\n  val y = 2\n"
        tokens = tokenize_full(code)
        types = [t[0] for t in tokens]
        self.assertEqual(types.count('INDENT'), 2)
        self.assertEqual(types.count('DEDENT'), 2)

    def test_lexical_error(self):
        tokens = tokenize_full("x @")
        self.assertGreater(len(tokens), 0)

    def test_inconsistent_indentation(self):
        code = "fun main()\n  val x = 1\n    val y = 2\n z = 3\n"
        original_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            tokenize_full(code)
            output = sys.stdout.getvalue()
        finally:
            sys.stdout = original_stdout
        self.assertNotEqual(output.strip(), "")

    def test_assignment_before_eq(self):
        code = "x = 5\ny == 3\n"
        tokens = tokenize_full(code)
        assign_tokens = [t for t in tokens if t[0] in ('ASSIGN', 'EQ')]
        self.assertEqual(assign_tokens[0][0], 'ASSIGN')
        self.assertEqual(assign_tokens[1][0], 'EQ')


# ============================================================
# PARSER TESTS
# ============================================================

class TestParser(unittest.TestCase):

    def test_program_empty(self):
        prog = parse("")
        self.assertIsInstance(prog, Program)

    def test_var_decl_val(self):
        prog = parse("fun main()\n  val x = 10\n")
        self.assertIsInstance(prog.statements[0], FunDecl)
        fd = prog.statements[0]
        self.assertIsInstance(fd.body[0], VarDecl)
        vd = fd.body[0]
        self.assertEqual(vd.kind, 'val')
        self.assertEqual(vd.name, 'x')

    def test_var_decl_var(self):
        prog = parse("fun main()\n  var y = 20.5\n")
        fd = prog.statements[0]
        vd = fd.body[0]
        self.assertEqual(vd.kind, 'var')
        self.assertIsInstance(vd.value, Literal)

    def test_assignment(self):
        prog = parse("fun main()\n  x = 10\n")
        fd = prog.statements[0]
        stmt = fd.body[0]
        self.assertIsInstance(stmt, Assignment)
        self.assertEqual(stmt.name, 'x')

    def test_fun_decl(self):
        prog = parse("fun soma(a: Int, b: Int)\n  return a + b\n")
        fd = prog.statements[0]
        self.assertIsInstance(fd, FunDecl)
        self.assertEqual(fd.name, 'soma')
        self.assertEqual(len(fd.params), 2)
        self.assertEqual(fd.params[0].name, 'a')
        self.assertEqual(fd.params[1].type_name, 'Int')

    def test_fun_decl_no_params(self):
        prog = parse("fun main()\n  println(1)\n")
        fd = prog.statements[0]
        self.assertEqual(len(fd.params), 0)

    def test_if_stmt(self):
        prog = parse("fun main()\n  if true\n    println(1)\n")
        fd = prog.statements[0]
        stmt = fd.body[0]
        self.assertIsInstance(stmt, IfStmt)
        self.assertIsNone(stmt.else_body)

    def test_if_else(self):
        code = "fun main()\n  if true\n    println(1)\n  else\n    println(2)\n"
        prog = parse(code)
        fd = prog.statements[0]
        stmt = fd.body[0]
        self.assertIsInstance(stmt, IfStmt)
        self.assertIsNotNone(stmt.else_body)

    def test_while_stmt(self):
        code = "fun main()\n  var i = 5\n  while i > 0\n    i = i - 1\n"
        prog = parse(code)
        fd = prog.statements[0]
        stmt = fd.body[1]
        self.assertIsInstance(stmt, WhileStmt)

    def test_return_stmt(self):
        prog = parse("fun main()\n  return 42\n")
        fd = prog.statements[0]
        stmt = fd.body[0]
        self.assertIsInstance(stmt, ReturnStmt)
        self.assertIsNotNone(stmt.value)

    def test_return_empty(self):
        prog = parse("fun main()\n  return\n")
        fd = prog.statements[0]
        stmt = fd.body[0]
        self.assertIsInstance(stmt, ReturnStmt)
        self.assertIsNone(stmt.value)

    def test_print_stmt(self):
        prog = parse("fun main()\n  println(42)\n")
        fd = prog.statements[0]
        stmt = fd.body[0]
        self.assertIsInstance(stmt, PrintStmt)

    def test_fun_call(self):
        prog = parse("fun main()\n  foo(x, y)\n")
        fd = prog.statements[0]
        stmt = fd.body[0]
        self.assertIsInstance(stmt, FunCall)
        self.assertEqual(stmt.name, 'foo')
        self.assertEqual(len(stmt.args), 2)

    def test_binary_op_addition(self):
        prog = parse("fun main()\n  val x = 1 + 2\n")
        fd = prog.statements[0]
        vd = fd.body[0]
        self.assertIsInstance(vd.value, BinaryOp)
        self.assertEqual(vd.value.op, '+')

    def test_binary_op_subtraction(self):
        prog = parse("fun main()\n  val x = 5 - 3\n")
        fd = prog.statements[0]
        vd = fd.body[0]
        self.assertIsInstance(vd.value, BinaryOp)
        self.assertEqual(vd.value.op, '-')

    def test_binary_op_multiplication(self):
        prog = parse("fun main()\n  val x = 3 * 4\n")
        fd = prog.statements[0]
        vd = fd.body[0]
        self.assertIsInstance(vd.value, BinaryOp)
        self.assertEqual(vd.value.op, '*')

    def test_binary_op_division(self):
        prog = parse("fun main()\n  val x = 10 / 2\n")
        fd = prog.statements[0]
        vd = fd.body[0]
        self.assertIsInstance(vd.value, BinaryOp)
        self.assertEqual(vd.value.op, '/')

    def test_unary_minus(self):
        prog = parse("fun main()\n  val x = -5\n")
        fd = prog.statements[0]
        vd = fd.body[0]
        self.assertIsInstance(vd.value, UnaryOp)
        self.assertEqual(vd.value.op, '-')

    def test_literal_int(self):
        prog = parse("fun main()\n  val x = 42\n")
        fd = prog.statements[0]
        vd = fd.body[0]
        self.assertIsInstance(vd.value, Literal)
        self.assertEqual(vd.value.type_name, 'Int')

    def test_literal_double(self):
        prog = parse("fun main()\n  val x = 3.14\n")
        fd = prog.statements[0]
        vd = fd.body[0]
        self.assertIsInstance(vd.value, Literal)
        self.assertEqual(vd.value.type_name, 'Double')

    def test_literal_string(self):
        prog = parse('fun main()\n  val x = "hello"\n')
        fd = prog.statements[0]
        vd = fd.body[0]
        self.assertIsInstance(vd.value, Literal)
        self.assertEqual(vd.value.type_name, 'String')

    def test_literal_bool_true(self):
        prog = parse("fun main()\n  val x = true\n")
        fd = prog.statements[0]
        vd = fd.body[0]
        self.assertIsInstance(vd.value, Literal)
        self.assertEqual(vd.value.type_name, 'Boolean')

    def test_literal_bool_false(self):
        prog = parse("fun main()\n  val x = false\n")
        fd = prog.statements[0]
        vd = fd.body[0]
        self.assertIsInstance(vd.value, Literal)
        self.assertEqual(vd.value.type_name, 'Boolean')

    def test_precedence_mul_before_add(self):
        prog = parse("fun main()\n  val x = 2 + 3 * 4\n")
        fd = prog.statements[0]
        vd = fd.body[0]
        self.assertIsInstance(vd.value, BinaryOp)
        self.assertEqual(vd.value.op, '+')
        self.assertIsInstance(vd.value.right, BinaryOp)
        self.assertEqual(vd.value.right.op, '*')

    def test_precedence_parens(self):
        prog = parse("fun main()\n  val x = (2 + 3) * 4\n")
        fd = prog.statements[0]
        vd = fd.body[0]
        self.assertIsInstance(vd.value, BinaryOp)
        self.assertEqual(vd.value.op, '*')
        self.assertIsInstance(vd.value.left, BinaryOp)
        self.assertEqual(vd.value.left.op, '+')

    def test_comparison_chain(self):
        prog = parse("fun main()\n  val x = a > b\n  val y = c < d\n  val z = e == f\n  val w = g != h\n")
        fd = prog.statements[0]
        for stmt in fd.body:
            self.assertIsInstance(stmt.value, BinaryOp)

    def test_and_or(self):
        prog = parse("fun main()\n  val x = a and b\n  val y = c or d\n  val z = not e\n")
        fd = prog.statements[0]
        self.assertIsInstance(fd.body[0].value, BinaryOp)
        self.assertEqual(fd.body[0].value.op, 'and')
        self.assertIsInstance(fd.body[1].value, BinaryOp)
        self.assertEqual(fd.body[1].value.op, 'or')
        self.assertIsInstance(fd.body[2].value, UnaryOp)
        self.assertEqual(fd.body[2].value.op, 'not')

    def test_identifier(self):
        prog = parse("fun main()\n  val x = nome\n")
        fd = prog.statements[0]
        vd = fd.body[0]
        self.assertIsInstance(vd.value, Identifier)
        self.assertEqual(vd.value.name, 'nome')

    def test_empty_lines_skipped(self):
        prog = parse("\n\nfun main()\n  val x = 1\n\n\n")
        self.assertEqual(len(prog.statements), 1)

    def test_syntax_error_recovery(self):
        code = "fun main()\n  val = 10\n  val y = 5\n"
        tokens = tokenize_full(code)
        parser = Parser(tokens)
        prog = parser.parse_program()
        self.assertGreater(len(prog.statements), 0)


# ============================================================
# SEMANTIC TESTS
# ============================================================

class TestSemantic(unittest.TestCase):

    def analyze(self, code):
        prog = parse(code)
        analyzer = SemanticAnalyzer()
        analyzer.analyze(prog)
        return analyzer

    def test_no_errors_valid_program(self):
        code = "fun main()\n  val x = 10\n  val y = x + 5\n"
        captured = io.StringIO()
        sys.stdout = captured
        try:
            self.analyze(code)
        finally:
            sys.stdout = sys.__stdout__
        output = captured.getvalue()
        self.assertNotIn('ERRO SEMÂNTICO', output)

    def test_undeclared_variable(self):
        code = "fun main()\n  val x = y\n"
        captured = io.StringIO()
        sys.stdout = captured
        try:
            self.analyze(code)
        finally:
            sys.stdout = sys.__stdout__
        self.assertIn('ERRO SEMÂNTICO', captured.getvalue())
        self.assertIn('y', captured.getvalue())

    def test_redeclaration(self):
        code = "fun main()\n  val x = 10\n  val x = 20\n"
        captured = io.StringIO()
        sys.stdout = captured
        try:
            self.analyze(code)
        finally:
            sys.stdout = sys.__stdout__
        self.assertIn('ERRO SEMÂNTICO', captured.getvalue())
        self.assertIn('já declarada', captured.getvalue())

    def test_assign_to_val(self):
        code = "fun main()\n  val x = 10\n  x = 20\n"
        captured = io.StringIO()
        sys.stdout = captured
        try:
            self.analyze(code)
        finally:
            sys.stdout = sys.__stdout__
        self.assertIn('ERRO SEMÂNTICO', captured.getvalue())
        self.assertIn('imutável', captured.getvalue())

    def test_assign_to_var(self):
        code = "fun main()\n  var x = 10\n  x = 20\n"
        captured = io.StringIO()
        sys.stdout = captured
        try:
            self.analyze(code)
        finally:
            sys.stdout = sys.__stdout__
        self.assertNotIn('ERRO SEMÂNTICO', captured.getvalue())

    def test_variable_in_different_scope(self):
        code = "fun main()\n  val x = 10\n  if true\n    val x = 20\n"
        captured = io.StringIO()
        sys.stdout = captured
        try:
            self.analyze(code)
        finally:
            sys.stdout = sys.__stdout__
        self.assertNotIn('ERRO SEMÂNTICO', captured.getvalue())

    def test_function_redeclaration(self):
        code = "fun foo()\n  val x = 1\nfun foo()\n  val y = 2\n"
        captured = io.StringIO()
        sys.stdout = captured
        try:
            self.analyze(code)
        finally:
            sys.stdout = sys.__stdout__
        self.assertIn('ERRO SEMÂNTICO', captured.getvalue())

    def test_undeclared_variable_in_expression(self):
        code = "fun main()\n  val x = a + b\n"
        captured = io.StringIO()
        sys.stdout = captured
        try:
            self.analyze(code)
        finally:
            sys.stdout = sys.__stdout__
        output = captured.getvalue()
        self.assertIn('a', output)
        self.assertIn('b', output)


# ============================================================
# INTEGRATION TESTS
# ============================================================

class TestIntegration(unittest.TestCase):

    def test_complete_example(self):
        code = """fun calcular(x: Int, y: Int)
  var resultado = x + y
  while resultado > 0
    println(resultado)
    resultado = resultado - 1
  return resultado

fun main()
  val a = 15.0
  val b = 5.0
  println(calcular(a, b))
"""
        prog = parse(code)
        self.assertEqual(len(prog.statements), 2)
        self.assertIsInstance(prog.statements[0], FunDecl)
        self.assertIsInstance(prog.statements[1], FunDecl)

    def test_all_exemplo_files(self):
        import os
        exemplos_dir = os.path.join(os.path.dirname(__file__), 'exemplos')
        ok_files = [
            'mathematica.kt', 'controle.kt', 'laco.kt',
            'logica.kt', 'precedencia.kt', 'fatorial.kt',
            'strings.kt', 'completo.kt',
        ]
        error_files = ['erro_semantico.kt', 'erro_sintatico.kt']

        for fname in ok_files:
            path = os.path.join(exemplos_dir, fname)
            with self.subTest(file=fname):
                with open(path, 'r') as f:
                    code = f.read()
                tokens = tokenize_full(code)
                parser = Parser(tokens)
                prog = parser.parse_program()
                self.assertGreater(len(prog.statements), 0, f"{fname} should produce statements")
                analyzer = SemanticAnalyzer()
                captured = io.StringIO()
                sys.stdout = captured
                try:
                    analyzer.analyze(prog)
                finally:
                    sys.stdout = sys.__stdout__
                output = captured.getvalue()
                self.assertNotIn('ERRO', output, f"{fname} should have no errors")

        for fname in error_files:
            path = os.path.join(exemplos_dir, fname)
            with self.subTest(file=fname):
                with open(path, 'r') as f:
                    code = f.read()
                captured = io.StringIO()
                sys.stdout = captured
                try:
                    tokens = tokenize_full(code)
                    parser = Parser(tokens)
                    prog = parser.parse_program()
                    analyzer = SemanticAnalyzer()
                    analyzer.analyze(prog)
                finally:
                    sys.stdout = sys.__stdout__
                output = captured.getvalue()
                self.assertIn('ERRO', output, f"{fname} should have at least one error")


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    unittest.main()
