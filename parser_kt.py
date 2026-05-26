from ast_kt import (
    Program, FunDecl, Param, VarDecl, Assignment,
    IfStmt, WhileStmt, ReturnStmt, PrintStmt,
    BinaryOp, UnaryOp, Literal, Identifier, FunCall
)


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self, offset=0):
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return ('EOF', '', -1, -1)

    def advance(self):
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def expect(self, expected_type):
        tok = self.peek()
        if tok[0] == expected_type:
            return self.advance()
        print(f"[ERRO SINTÁTICO] Linha {tok[2]}: Esperado '{expected_type}', encontrado '{tok[0]}' ({repr(tok[1])})")
        return None

    def consume_newline(self):
        if self.peek()[0] == 'NEWLINE':
            self.advance()

    def parse_program(self):
        stmts = []
        while self.pos < len(self.tokens):
            tok = self.peek()
            if tok[0] == 'EOF':
                break
            stmt = self.parse_statement()
            if stmt is not None:
                stmts.append(stmt)
        return Program(stmts)

    def parse_statement(self):
        tok = self.peek()
        t = tok[0]

        while t == 'NEWLINE':
            self.advance()
            tok = self.peek()
            t = tok[0]

        if t == 'EOF' or t == 'DEDENT':
            return None

        if t == 'FUN':
            return self.parse_fun_decl()
        elif t in ('VAL', 'VAR'):
            stmt = self.parse_var_decl()
            self.consume_newline()
            return stmt
        elif t == 'IF':
            return self.parse_if_stmt()
        elif t == 'WHILE':
            return self.parse_while_stmt()
        elif t == 'RETURN':
            stmt = self.parse_return_stmt()
            self.consume_newline()
            return stmt
        elif t == 'ID' and self.peek(1)[0] == 'ASSIGN':
            stmt = self.parse_assignment()
            self.consume_newline()
            return stmt
        else:
            stmt = self.parse_expression()
            self.consume_newline()
            return stmt

    def parse_block(self):
        self.expect('INDENT')
        stmts = []
        while self.pos < len(self.tokens):
            tok = self.peek()
            if tok[0] == 'DEDENT':
                self.advance()
                break
            if tok[0] == 'EOF':
                break
            stmt = self.parse_statement()
            if stmt is not None:
                stmts.append(stmt)
        return stmts

    def parse_fun_decl(self):
        self.expect('FUN')
        name_tok = self.expect('ID')
        name = name_tok[1] if name_tok else '?'
        self.expect('LPAREN')
        params = []
        if self.peek()[0] != 'RPAREN':
            params = self.parse_param_list()
        self.expect('RPAREN')
        self.expect('NEWLINE')
        body = self.parse_block()
        return FunDecl(name, params, body)

    def parse_param_list(self):
        params = []
        params.append(self.parse_param())
        while self.peek()[0] == 'COMMA':
            self.advance()
            params.append(self.parse_param())
        return params

    def parse_param(self):
        name_tok = self.expect('ID')
        name = name_tok[1] if name_tok else '?'
        self.expect('COLON')
        type_tok = self.expect('TYPE')
        type_name = type_tok[1] if type_tok else '?'
        return Param(name, type_name)

    def parse_var_decl(self):
        kind = self.advance()[0]
        name_tok = self.expect('ID')
        name = name_tok[1] if name_tok else '?'
        self.expect('ASSIGN')
        value = self.parse_expression()
        return VarDecl(kind.lower(), name, value)

    def parse_assignment(self):
        name_tok = self.expect('ID')
        name = name_tok[1] if name_tok else '?'
        self.expect('ASSIGN')
        value = self.parse_expression()
        return Assignment(name, value)

    def parse_if_stmt(self):
        self.expect('IF')
        condition = self.parse_expression()
        self.expect('NEWLINE')
        then_body = self.parse_block()
        else_body = None
        if self.peek()[0] == 'ELSE':
            self.advance()
            self.expect('NEWLINE')
            else_body = self.parse_block()
        return IfStmt(condition, then_body, else_body)

    def parse_while_stmt(self):
        self.expect('WHILE')
        condition = self.parse_expression()
        self.expect('NEWLINE')
        body = self.parse_block()
        return WhileStmt(condition, body)

    def parse_argument_list(self):
        args = []
        args.append(self.parse_expression())
        while self.peek()[0] == 'COMMA':
            self.advance()
            args.append(self.parse_expression())
        return args

    def parse_return_stmt(self):
        self.expect('RETURN')
        value = None
        if self.peek()[0] not in ('NEWLINE', 'DEDENT', 'EOF'):
            value = self.parse_expression()
        return ReturnStmt(value)

    def parse_expression(self):
        return self.parse_or_expr()

    def parse_or_expr(self):
        left = self.parse_and_expr()
        while self.peek()[0] == 'OR':
            self.advance()
            right = self.parse_and_expr()
            left = BinaryOp('or', left, right)
        return left

    def parse_and_expr(self):
        left = self.parse_not_expr()
        while self.peek()[0] == 'AND':
            self.advance()
            right = self.parse_not_expr()
            left = BinaryOp('and', left, right)
        return left

    def parse_not_expr(self):
        if self.peek()[0] == 'NOT':
            self.advance()
            operand = self.parse_comparison_expr()
            return UnaryOp('not', operand)
        return self.parse_comparison_expr()

    def parse_comparison_expr(self):
        left = self.parse_additive_expr()
        tok = self.peek()
        if tok[0] in ('GT', 'LT', 'GE', 'LE', 'EQ', 'NEQ'):
            self.advance()
            op_map = {'GT': '>', 'LT': '<', 'GE': '>=', 'LE': '<=', 'EQ': '==', 'NEQ': '!='}
            right = self.parse_additive_expr()
            return BinaryOp(op_map[tok[0]], left, right)
        return left

    def parse_additive_expr(self):
        left = self.parse_multiplicative_expr()
        while self.peek()[0] in ('PLUS', 'MINUS'):
            op = self.advance()[0]
            op_map = {'PLUS': '+', 'MINUS': '-'}
            right = self.parse_multiplicative_expr()
            left = BinaryOp(op_map[op], left, right)
        return left

    def parse_multiplicative_expr(self):
        left = self.parse_unary_expr()
        while self.peek()[0] in ('STAR', 'SLASH'):
            op = self.advance()[0]
            op_map = {'STAR': '*', 'SLASH': '/'}
            right = self.parse_unary_expr()
            left = BinaryOp(op_map[op], left, right)
        return left

    def parse_unary_expr(self):
        if self.peek()[0] == 'MINUS':
            self.advance()
            operand = self.parse_atom()
            return UnaryOp('-', operand)
        return self.parse_atom()

    def parse_atom(self):
        tok = self.peek()
        t = tok[0]

        if t == 'NUMBER':
            self.advance()
            val = tok[1]
            if '.' in val:
                return Literal(val, 'Double')
            return Literal(val, 'Int')
        elif t == 'STRING':
            self.advance()
            return Literal(tok[1], 'String')
        elif t == 'TRUE':
            self.advance()
            return Literal('true', 'Boolean')
        elif t == 'FALSE':
            self.advance()
            return Literal('false', 'Boolean')
        elif t == 'ID':
            self.advance()
            if self.peek()[0] == 'LPAREN':
                self.advance()
                args = []
                if self.peek()[0] != 'RPAREN':
                    args = self.parse_argument_list()
                self.expect('RPAREN')
                return FunCall(tok[1], args)
            return Identifier(tok[1])
        elif t == 'PRINTLN':
            self.advance()
            self.expect('LPAREN')
            value = self.parse_expression()
            self.expect('RPAREN')
            return PrintStmt(value)
        elif t == 'LPAREN':
            self.advance()
            expr = self.parse_expression()
            self.expect('RPAREN')
            return expr
        else:
            print(f"[ERRO SINTÁTICO] Linha {tok[2]}: Expressão esperada, encontrado '{t}' ({repr(tok[1])})")
            return Literal('0', 'Int')
