# Arquitetura do Mini-Compilador Kotlin

## Estrutura do Projeto

```
kotlin-compiler/
│
├── main.py                  # Orquestrador — coordena todas as fases
├── lexer_kt.py              # Analisador Léxico (Scanner)
├── parser_kt.py             # Analisador Sintático (Parser)
├── ast_kt.py                # AST — nós da árvore + pretty-printer
├── semantic_kt.py           # Analisador Semântico + Tabela de Símbolos
├── generate_tokens_kt.py    # Arquivo original do professor (não modificado)
│
├── main.kt                  # Exemplo de código Mini-Kotlin
├── arquitetura.txt          # Diagrama ASCII da arquitetura
└── arquitetura.md           # Este arquivo
```

---

### Descrição dos Arquivos

| Arquivo | Função |
|---|---|
| `main.py` | **Orquestrador.** Lê o arquivo `.kt`, chama o lexer, o parser, exibe a AST e o analisador semântico em sequência. |
| `lexer_kt.py` | **Scanner.** Percorre o código-fonte caractere por caractere, aplica regex para reconhecer 30+ tipos de token (keywords, operadores, literais, etc.) e gerencia a pilha de indentação para emitir `INDENT`/`DEDENT`. |
| `parser_kt.py` | **Parser descendente recursivo.** Consome o fluxo de tokens e constrói a AST seguindo a gramática livre de contexto. Valida a ordem lógica das instruções e a precedência matemática. |
| `ast_kt.py` | **AST.** Define as classes de nós (`Program`, `FunDecl`, `VarDecl`, `IfStmt`, `WhileStmt`, `BinaryOp`, etc.) e a função `print_ast()` que exibe a árvore indentada no terminal. |
| `semantic_kt.py` | **Analisador Semântico.** Percorre a AST com uma pilha de escopos, mantém uma tabela de símbolos (hash map) e verifica: variável declarada antes do uso, sem redeclaração no mesmo escopo. |
| `generate_tokens_kt.py` | Arquivo original fornecido pelo professor (`gerar_tokens`). Mantido intacto como referência. |
| `main.kt` | Código de exemplo na linguagem Mini-Kotlin (indentação no lugar de chaves, sem ponto e vírgula). |

---

## Diagrama da Arquitetura

```
                    ┌─────────────────────┐
                    │   CÓDIGO FONTE      │
                    │   (main.kt)         │
                    └────────┬────────────┘
                             │
                             ▼
               ┌─────────────────────────┐
               │   FASE 1: LÉXICO        │
               │   lexer_kt.py           │
               │                         │
               │   "Escaneia" o código   │
               │   e divide em tokens    │
               │   (palavras-chave,      │
               │    operadores, números, │
               │    identação → INDENT/  │
               │    DEDENT, etc.)        │
               │                         │
               │   Erro léxico:          │
               │   caractere inválido    │
               └────────┬────────────────┘
                        │ fluxo de tokens
                        ▼
               ┌─────────────────────────┐
               │   FASE 2: SINTÁTICO     │
               │   parser_kt.py          │
               │                         │
               │   Consome os tokens e   │
               │   verifica a gramática  │
               │   (descida recursiva)   │
               │                         │
               │   Reconhece: fun, if,   │
               │   while, expr math,    │
               │   precedência, etc.     │
               │                         │
               │   Erro sintático:       │
               │   token inesperado      │
               └────────┬────────────────┘
                        │ Árvore Sintática Abstrata (AST)
                        ▼
               ┌─────────────────────────┐
               │   FASE 3: AST           │
               │   ast_kt.py             │
               │                         │
               │   Nós: Program,         │
               │   FunDecl, VarDecl,     │
               │   IfStmt, WhileStmt,    │
               │   BinaryOp, Literal,    │
               │   FunCall, etc.         │
               │                         │
               │   print_ast(): exibe    │
               │   a árvore indentada    │
               └────────┬────────────────┘
                        │ AST
                        ▼
               ┌─────────────────────────┐
               │   FASE 4: SEMÂNTICO     │
               │   semantic_kt.py        │
               │                         │
               │   Percorre a AST e      │
               │   valida significados:  │
               │   • Variável declarada  │
               │     antes do uso?       │
               │   • Redeclaração no     │
               │     mesmo escopo?       │
               │                         │
               │   Erro semântico:       │
               │   variável não existe   │
               └────────┬────────────────┘
                        │
                        ▼
               ┌─────────────────────────┐
               │   ORQUESTRADOR          │
               │   main.py               │
               │                         │
               │   1. Lê o arquivo .kt   │
               │   2. Chama lexer_kt     │
               │   3. Chama parser_kt    │
               │   4. Exibe a AST        │
               │   5. Chama semantic_kt  │
               └─────────────────────────┘
```

---

## Fluxo de Execução

```
python3 main.py main.kt
       │
       ├── ler_arquivo_texto("main.kt")
       │       ↓
       │   "fun calcular(...)\n  var resultado = ..."
       │
       ├── tokenize(codigo)
       │       ↓
       │   [FUN], [ID], [LPAREN], [TYPE], ..., [INDENT], ...
       │
       ├── Parser(tokens).parse_program()
       │       ↓
       │   Program(FunDecl, VarDecl, WhileStmt, ...)
       │
       ├── print_ast(program)
       │       ↓
       │   AST exibida na tela
       │
       └── SemanticAnalyzer().analyze(program)
               ↓
           Erros semânticos (se houver)
```

---

## Exemplo de Funcionamento (Rastreamento)

```
Entrada:  val x = 10

Léxico → [VAL]   'val' (L:1 C:1)
         [ID]    'x'   (L:1 C:5)
         [ASSIGN] '='  (L:1 C:7)
         [NUMBER] '10' (L:1 C:9)

Sintático → VarDecl(kind='val', name='x', value=Literal(10, Int))

Semântico → "x" declarado no escopo atual. OK.
```

---

## Requisitos do Projeto Atendidos

| Requisito | Status |
|---|---|
| Atribuição: `val`/`var x = expr` | ✔ |
| Matemática: `+`, `-`, `*`, `/` com precedência e `()` | ✔ |
| Controle: `if`/`else`, `while` (por indentação) | ✔ |
| Relacionais: `>`, `<`, `==`, `!=` | ✔ |
| Lógicos: `and`, `or`, `not` (proibido `&&`, `\|\|`, `!`) | ✔ |
| Funções: `fun nome(params)` | ✔ |
| Indentação: `INDENT`/`DEDENT` ao invés de `{}` | ✔ |
| Tipos inferidos: `Int`, `Double`, `String`, `Boolean` | ✔ |
| Erro léxico: caractere inválido → linha/coluna | ✔ |
| Erro sintático: token inesperado | ✔ |
| Erro semântico: variável não declarada / redeclarada | ✔ |
| AST exibida na tela | ✔ |
