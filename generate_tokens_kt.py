import os  # Biblioteca para interagir com o sistema operacional (ex: checar arquivos)
import re  # Biblioteca para usar Expressões Regulares (Regex)


def gerar_tokens(codigo_fonte):
    """
    Função principal do Analisador Léxico (Scanner).
    Recebe o código-fonte como uma string completa e o divide em uma lista de tokens.
    """
    # Lista de regras. Cada regra é uma tupla ('NOME_DO_TOKEN', 'Expressão Regular')
    # ATENÇÃO: O símbolo '^' no início de cada regex é fundamental.
    # Ele força a busca a acontecer APENAS no começo da string atual.
    token_specification = [
        ('TYPE',     r'^Byte\b|^Short\b|^Int\b|^Long\b|^Float\b|^Double\b|^Char\b|^String\b|^Boolean\b'),#tipos de dados
        ('NUMBER',   r'\d+(\.\d*)?'),  # Número inteiro ou decimal
        ('ASSIGN',   r'='),           # Operador de atribuição
        ('END',      r';'),            # Fiinalizador de instrução
        ('ID',       r'[A-Z|a-z]+'),    # Identificadores
        ('OP',       r'[+\-*/]'),      # Operadores aritméticos
        ('NEWLINE',  r'\n'),           # Finais de linha
        ('SKIP',     r'[ \t]+'),       # Pula espaços e tabulações
        ('MISMATCH', r'.'),            # Qualquer outro caracter
    ]

    tokens = [] # Lista que vai armazenar os tokens válidos encontrados

    # Variáveis para rastrear a posição no código (excelente para criar mensagens de erro precisas)
    linha_atual = 1
    coluna_atual = 1

    # O laço continua rodando enquanto houver caracteres na string do código-fonte
    while codigo_fonte:
        padrao_encontrado = False

        # Testa cada regra léxica definida na lista `token_specification`
        for tipo, padrao in token_specification:
            
            # Tenta casar a regra (regex) com o início do código-fonte atual
            match = re.match(padrao, codigo_fonte)

            if match: # Se encontrou um padrão válido...
                valor = match.group(0) # Extrai o texto exato que atendeu à regra
                tamanho_valor = len(valor)

                # Se for uma quebra de linha, pulamos de linha e zeramos a coluna
                if tipo == 'NEWLINE':
                    linha_atual += 1
                    coluna_atual = 1
                else:
                    # Se não for espaço/tabulação (SKIP), empacotamos e guardamos o token!
                    if tipo != 'SKIP':
                        novo_token = (tipo, valor, linha_atual, coluna_atual)
                        tokens.append(novo_token)

                # Atualiza a coluna atual (fazemos isso até para os espaços em branco que ignoramos)
                coluna_atual += tamanho_valor

                # PASSO CRUCIAL: "Fatia" a string, removendo o pedaço que acabamos de ler.
                # Isso permite que, na próxima volta do 'while', o `re.match` analise a próxima palavra do código.
                codigo_fonte = codigo_fonte[tamanho_valor:]
                padrao_encontrado = True
                break # Sai do laço 'for' pois já identificou o token deste pedaço

        # Se o programa testou todas as regras e nenhuma serviu para o início da string, temos um caractere inválido!
        if not padrao_encontrado:
            print(f"\n[ERRO LÉXICO] Linha {linha_atual}, Coluna {coluna_atual}: Trecho não reconhecido -> '{codigo_fonte[0]}'")
            break # Interrompe a análise em caso de erro

    return tokens


def ler_arquivo_texto(nome_arquivo):
    """
    Função auxiliar para ler o arquivo que contém o código a ser analisado.
    """
    print(f"Lendo o arquivo : '{nome_arquivo}'\n")
    print("-" * 50)

    # Trecho facilitador: Se o arquivo não existir, cria um código de teste automaticamente para os alunos.
    if not os.path.exists(nome_arquivo):
        print(f"O arquivo '{nome_arquivo}' não foi encontrado. Criando um de exemplo...")
        with open(nome_arquivo, "w", encoding="utf-8") as f:
            f.write("int peso = 85;\nfloat nota = 7.2;\nchar letra = 'a';")

    # Abre e lê todo o conteúdo do arquivo
    with open(nome_arquivo, 'r', encoding='utf-8') as arquivo:
        codigo = arquivo.read()

    return codigo


# ==========================================
# EXECUÇÃO PRINCIPAL DO PROGRAMA
# ==========================================

arquivo_alvo = "main.kt"

# 1. Lê o código-fonte do arquivo .txt
codigo_do_arquivo = ler_arquivo_texto(arquivo_alvo)

print(f"CÓDIGO LIDO:\n{codigo_do_arquivo}\n")
print("-" * 50)

# 2. Passa o texto para o nosso Analisador Léxico processar
meus_tokens = gerar_tokens(codigo_do_arquivo)

# 3. Imprime os tokens encontrados de forma legível e organizada
if meus_tokens:
    for token in meus_tokens:
        tipo, valor, linha, coluna = token
        # Dica de Python: '{tipo:^10}' centraliza a palavra usando 10 espaços, alinhando a visualização no terminal.
        print(f"[{tipo:^10}] '{valor}' (Linha: {linha}, Col: {coluna})")