import os
import re

TOKEN_SPEC = [
    ('FUN',      r'^fun\b'),
    ('VAL',      r'^val\b'),
    ('VAR',      r'^var\b'),
    ('IF',       r'^if\b'),
    ('ELSE',     r'^else\b'),
    ('WHILE',    r'^while\b'),
    ('FOR',      r'^for\b'),
    ('RETURN',   r'^return\b'),
    ('PRINTLN',  r'^println\b'),
    ('AND',      r'^and\b'),
    ('OR',       r'^or\b'),
    ('NOT',      r'^not\b'),
    ('TRUE',     r'^true\b'),
    ('FALSE',    r'^false\b'),
    ('TYPE',     r'^Int\b|^Double\b|^String\b|^Boolean\b|^Unit\b'),
    ('NUMBER',   r'^\d+(\.\d*)?'),
    ('STRING',   r'^"[^"]*"'),
    ('EQ',       r'^=='),
    ('NEQ',      r'^!='),
    ('GE',       r'^>='),
    ('LE',       r'^<='),
    ('ASSIGN',   r'^='),
    ('GT',       r'^>'),
    ('LT',       r'^<'),
    ('PLUS',     r'^\+'),
    ('MINUS',    r'^-'),
    ('STAR',     r'^\*'),
    ('COMMENT',  r'^//[^\n]*'),
    ('SLASH',    r'^/'),
    ('LPAREN',   r'^\('),
    ('RPAREN',   r'^\)'),
    ('COLON',    r'^:'),
    ('COMMA',    r'^,'),
    ('DOT',      r'^\.'),
    ('ID',       r'^[a-zA-Z_]\w*'),
    ('NEWLINE',  r'^\n'),
    ('SKIP',     r'^[ \t]+'),
    ('MISMATCH', r'.'),
]


def tokenize(codigo_fonte):
    tokens = []
    linha = 1
    coluna = 1

    indent_stack = [0]
    line_start = True

    i = 0
    while i < len(codigo_fonte):
        rest = codigo_fonte[i:]

        if line_start:
            spaces = 0
            j = i
            while j < len(codigo_fonte) and codigo_fonte[j] == ' ':
                spaces += 1
                j += 1
            if j < len(codigo_fonte) and codigo_fonte[j] != '\n':
                current_indent = indent_stack[-1]
                if spaces > current_indent:
                    indent_stack.append(spaces)
                    tokens.append(('INDENT', '', linha, coluna))
                elif spaces < current_indent:
                    while indent_stack and indent_stack[-1] > spaces:
                        indent_stack.pop()
                        tokens.append(('DEDENT', '', linha, coluna))
                    if indent_stack and indent_stack[-1] != spaces:
                        print(f"\n[ERRO LÉXICO] Linha {linha}, Coluna {coluna}: Indentação inconsistente ({spaces} espaços não correspondem a nenhum nível anterior)")
                        return tokens
            line_start = False

        matched = False
        for tok_type, pattern in TOKEN_SPEC:
            m = re.match(pattern, rest)
            if m:
                value = m.group(0)
                tok_len = len(value)

                if tok_type == 'NEWLINE':
                    coluna_newline = coluna
                    linha += 1
                    coluna = 1
                    line_start = True
                    tokens.append(('NEWLINE', value, linha - 1, coluna_newline))
                elif tok_type == 'COMMENT':
                    coluna += tok_len
                elif tok_type == 'SKIP':
                    coluna += tok_len
                elif tok_type == 'MISMATCH':
                    print(f"\n[ERRO LÉXICO] Linha {linha}, Coluna {coluna}: Caractere não reconhecido -> '{value}'")
                    return tokens
                else:
                    tokens.append((tok_type, value, linha, coluna))
                    coluna += tok_len

                i += tok_len
                matched = True
                break

        if not matched:
            print(f"\n[ERRO LÉXICO] Linha {linha}, Coluna {coluna}: Trecho não reconhecido -> '{rest[0]}'")
            break

    while len(indent_stack) > 1:
        indent_stack.pop()
        tokens.append(('DEDENT', '', linha, coluna))

    return tokens


def ler_arquivo_texto(nome_arquivo):
    print(f"Lendo o arquivo: '{nome_arquivo}'\n")
    print("-" * 50)

    if not os.path.exists(nome_arquivo):
        print(f"O arquivo '{nome_arquivo}' não foi encontrado. Criando um de exemplo...")
        with open(nome_arquivo, "w", encoding="utf-8") as f:
            f.write('fun main()\n  val x = 10\n  println(x)\n')

    with open(nome_arquivo, 'r', encoding='utf-8') as arquivo:
        codigo = arquivo.read()

    return codigo


if __name__ == '__main__':
    arquivo_alvo = "main.kt"
    codigo_do_arquivo = ler_arquivo_texto(arquivo_alvo)
    print(f"CÓDIGO LIDO:\n{codigo_do_arquivo}\n")
    print("-" * 50)
    meus_tokens = tokenize(codigo_do_arquivo)
    if meus_tokens:
        for token in meus_tokens:
            tipo, valor, linha, coluna = token
            print(f"[{tipo:^10}] '{valor}' (Linha: {linha}, Col: {coluna})")
