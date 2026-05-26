# Mini-Compilador Kotlin

Projeto A3 — UC Teoria da Computação e Compiladores (2026.1)

**Autores:** Bruno Melo, Daniel Menezes, Fernando Mota

Mini-compilador para a linguagem **Mini-Kotlin**, uma linguagem baseada em Kotlin
com blocos definidos por **indentação** (sem chaves), inferência de tipos, e
operadores lógicos textuais (`and`, `or`, `not`).

---

## Requisitos

- **Python 3.10+**
- Nenhuma biblioteca externa necessária (apenas `os` e `re` da stdlib)

---

## Como Executar

```bash
# Compilar o arquivo padrão (main.kt)
python3 main.py

# Compilar um arquivo específico
python3 main.py exemplos/completo.kt

# Lista de exemplos disponíveis
python3 main.py exemplos/mathematica.kt
python3 main.py exemplos/laco.kt
python3 main.py exemplos/controle.kt
python3 main.py exemplos/logica.kt
python3 main.py exemplos/precedencia.kt
python3 main.py exemplos/fatorial.kt
python3 main.py exemplos/strings.kt

# Exemplos com erro (teste de detecção)
python3 main.py exemplos/erro_semantico.kt
python3 main.py exemplos/erro_sintatico.kt
```

---

## Visão Geral da Arquitetura

O compilador é dividido em 4 fases sequenciais, orquestradas por `main.py`:

```
┌─────────────┐
│  Código Fonte │  main.kt (texto)
└──────┬──────┘
       ▼
┌──────────────────────┐
│  FASE 1 — LÉXICO    │  lexer_kt.py
│                     │
│  Escaneia o código  │
│  e produz tokens    │
│  (FUN, VAL, ID,     │
│   NUMBER, INDENT,   │
│   DEDENT, etc.)     │
│                     │
│  Erro léxico:       │
│  caractere inválido │
└──────┬───────────────┘
       ▼ fluxo de tokens
┌──────────────────────┐
│  FASE 2 — SINTÁTICO │  parser_kt.py
│                     │
│  Consome os tokens  │
│  e constrói a AST   │
│  (descida recursiva)│
│                     │
│  Erro sintático:    │
│  token inesperado   │
└──────┬───────────────┘
       ▼ AST
┌──────────────────────┐
│  FASE 3 — AST       │  ast_kt.py
│                     │
│  Exibe a árvore     │
│  indentada no       │
│  terminal           │
└──────┬───────────────┘
       ▼ AST
┌──────────────────────┐
│  FASE 4 — SEMÂNTICO │  semantic_kt.py
│                     │
│  Percorre a AST,    │
│  valida declarações │
│  e usos de variáveis│
│                     │
│  Erro semântico:    │
│  var não declarada  │
│  ou redeclarada     │
└──────────────────────┘
```

---

## Linguagem Mini-Kotlin

### Regras

| Característica | Regra |
|---|---|
| Declaração de variáveis | `val x = 10` ou `var x = 10` (inferência de tipo) |
| Mutabilidade | `val` = imutável, `var` = mutável |
| Operadores lógicos | `and`, `or`, `not` (proibido `&&`, `\|\|`, `!`) |
| Delimitadores | Quebra de linha (`\n`) — sem ponto e vírgula |
| Blocos de escopo | Indentação — sem chaves `{}` |
| Funções | `fun nome(param: Tipo) \n  corpo` |
| Comentários | `//` até o fim da linha |

### Exemplo

```kotlin
fun calcular(x: Int, y: Int)
  var resultado = x + y
  while resultado > 0
    println(resultado)
    resultado = resultado - 1
  return resultado

fun main()
  val a = 15.0
  val b = 5.0
  println(calcular(a, b))
```

### Operadores Suportados

- **Aritméticos:** `+`, `-`, `*`, `/`
- **Relacionais:** `>`, `<`, `>=`, `<=`, `==`, `!=`
- **Lógicos:** `and`, `or`, `not`
- **Atribuição:** `=`
- **Agrupamento:** `(`, `)`

### Tipos (inferidos)

- `Int` (números sem ponto)
- `Double` (números com ponto)
- `String` (`"texto"`)
- `Boolean` (`true` / `false`)
- `Unit` (retorno de `println`)

---

## Estrutura do Projeto

```
kotlin-compiler/
│
├── main.py                    # Orquestrador principal
├── lexer_kt.py                # Analisador léxico (scanner)
├── parser_kt.py               # Analisador sintático (parser descendente recursivo)
├── ast_kt.py                  # Nós da AST + pretty-printer
├── semantic_kt.py             # Analisador semântico + tabela de símbolos
├── generate_tokens_kt.py      # Arquivo original do professor (não modificado)
│
├── main.kt                    # Exemplo padrão (Mini-Kotlin)
│
├── exemplos/
│   ├── mathematica.kt         # Soma e chamada de função
│   ├── controle.kt            # if / else com >=
│   ├── laco.kt                # while loop com string
│   ├── logica.kt              # and / or / not
│   ├── precedencia.kt         # Precedência matemática
│   ├── fatorial.kt            # Fatorial com while + return
│   ├── strings.kt             # Literais de string
│   ├── completo.kt            # Todos os recursos combinados
│   ├── erro_semantico.kt      # Exemplo com erro semântico
│   └── erro_sintatico.kt      # Exemplo com erro sintático
│
├── arquitetura.md             # Diagrama da arquitetura em Markdown
├── arquitetura.txt            # Diagrama da arquitetura em ASCII
└── README.md                  # Este arquivo
```

---

## Fases do Projeto (conforme o enunciado)

| Fase | Entregável | Arquivo | Peso |
|---|---|---|---|
| 1 | Modelagem (tabela de tokens + GLC) | `lexer_kt.py` + este README | 15% |
| 2 | Analisador Léxico | `lexer_kt.py` | 15% |
| 3 | Analisador Sintático + Erros | `parser_kt.py` | 25% |
| 4 | AST | `ast_kt.py` | 15% |
| 5 | Tabela de Símbolos + Semântica | `semantic_kt.py` | 20% |
| — | Apresentação | — | 10% |

---

## Detecção de Erros

### Erro Léxico

```
[ERRO LÉXICO] Linha 3, Coluna 11: Caractere não reconhecido -> '@'
```

### Erro Sintático

```
[ERRO SINTÁTICO] Linha 3: Esperado 'ID', encontrado 'ASSIGN' ('=')
```

### Erro Semântico

```
[ERRO SEMÂNTICO] Variável 'z' não declarada antes do uso
```
