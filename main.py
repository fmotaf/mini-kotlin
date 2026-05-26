import sys
from lexer_kt import tokenize, ler_arquivo_texto
from parser_kt import Parser
from ast_kt import print_ast
from semantic_kt import SemanticAnalyzer


def main():
    arquivo_alvo = sys.argv[1] if len(sys.argv) > 1 else "main.kt"

    print("=" * 60)
    print("MINI-KOTLIN COMPILADOR")
    print("=" * 60)

    codigo = ler_arquivo_texto(arquivo_alvo)
    print(f"\nCÓDIGO FONTE:\n{codigo}")
    print("=" * 60)

    print("\n>>> FASE 1: ANÁLISE LÉXICA (SCANNER)")

    tokens = tokenize(codigo)

    if not tokens:
        print("Nenhum token gerado. Abortando.")
        return

    for tok in tokens:
        print(f"  [{tok[0]:^8}] '{tok[1]}' (L:{tok[2]} C:{tok[3]})")

    print(f"\nTotal de tokens: {len(tokens)}")
    print("=" * 60)

    print("\n>>> FASE 2: ANÁLISE SINTÁTICA (PARSER)")

    parser = Parser(tokens)
    program = parser.parse_program()

    if not program.statements:
        print("Nenhuma instrução encontrada. Abortando.")
        return

    print("\n>>> FASE 3: ÁRVORE SINTÁTICA ABSTRATA (AST)")
    print_ast(program)
    print("=" * 60)

    print("\n>>> FASE 4: ANÁLISE SEMÂNTICA")

    analyzer = SemanticAnalyzer()
    analyzer.analyze(program)

    print("\nAnálise semântica concluída.")
    print("=" * 60)
    print("COMPILAÇÃO FINALIZADA")


if __name__ == '__main__':
    main()
