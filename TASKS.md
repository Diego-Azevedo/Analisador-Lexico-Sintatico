# Plano de implementacao - LCC-2026-1

Este documento separa a implementacao do analisador lexico e do analisador sintatico em etapas. Ele foi montado a partir do enunciado do EP de INE5622 e deve guiar o desenvolvimento incremental do projeto em Python 3.11+.

Entrega oficial: 26 de junho de 2026, ate 23:55 via Moodle.

## Requisitos obrigatorios do enunciado

- Implementar um analisador lexico que leia a entrada caracter por caracter.
- Basear o analisador lexico em diagramas de transicao.
- Implementar uma tabela de simbolos com uma entrada por identificador.
- Registrar, para cada identificador, uma lista de ocorrencias com linha e coluna.
- Implementar um analisador sintatico para uma gramatica LL(1).
- Construir a tabela de reconhecimento sintatico uma unica vez.
- Usar a tabela LL(1) para aceitar ou rejeitar a entrada.
- Entregar tres programas `.lcc` com pelo menos 100 linhas cada, sem erros lexicos e sem erros sintaticos.
- Entregar `Makefile` funcional.
- Entregar `README.md` com instrucoes de execucao.
- A execucao deve receber como entrada um unico caminho para arquivo `.lcc`.

## Estrutura proposta

```text
lcc-compiler/
├── src/
│   ├── lexer.py          # Analisador lexico: automato, leitura char a char
│   ├── symbol_table.py   # Tabela de simbolos
│   ├── parser.py         # Analisador sintatico LL(1)
│   ├── grammar.py        # Gramatica, FIRST, FOLLOW e tabela LL(1)
│   └── main.py           # Entry point: recebe caminho do .lcc
├── examples/
│   ├── prog1.lcc
│   ├── prog2.lcc
│   └── prog3.lcc
├── tests/
│   ├── test_lexer.py
│   └── test_parser.py
├── Makefile
├── README.md
└── .gitignore
```

## Fase 0 - Projeto e estrutura

### Task 0.1 - Criar estrutura de diretorios

Tipo: infra

Criar a base do projeto com `src/`, `tests/`, `examples/`, `Makefile`, `README.md` e `.gitignore`.

Criterios de aceite:

- A estrutura existe no repositorio.
- O codigo-fonte fica isolado em `src/`.
- Os exemplos `.lcc` ficam em `examples/`.
- Os testes ficam em `tests/`.

### Task 0.2 - Definir Makefile

Tipo: infra

Criar `Makefile` compativel com Python 3.11+, com comandos simples para execucao, testes e limpeza.

Targets sugeridos:

- `make run FILE=examples/prog1.lcc`
- `make test`
- `make clean`

Criterios de aceite:

- `make run FILE=<arquivo.lcc>` executa o analisador.
- `make test` roda os testes automatizados.
- `make clean` remove caches e arquivos temporarios.
- O `Makefile` documenta a versao de Python usada.

### Task 0.3 - Escrever README inicial

Tipo: doc

Criar `README.md` com informacoes minimas para uso e avaliacao.

Conteudo minimo:

- Nome do projeto.
- Integrantes do grupo.
- Versao de Python.
- Como executar o analisador.
- Como executar os testes.
- Exemplos de comandos.
- Observacoes sobre eventuais modificacoes na linguagem, se houver.

Criterios de aceite:

- Uma pessoa externa consegue executar o projeto seguindo o README.
- O README deixa claro qual arquivo `.lcc` deve ser passado como entrada.

## Fase 1 - Gramatica e tokens

### Task 1.1 - Levantar todos os tokens da gramatica

Tipo: grammar

Mapear todos os terminais da gramatica CC-2026-1.

Tokens reservados e literais identificados no enunciado:

- Palavras reservadas: `def`, `int`, `float`, `string`, `print`, `read`, `return`, `if`, `else`, `for`, `break`, `new`, `null`.
- Operadores: `=`, `+`, `-`, `*`, `/`, `%`, `<`, `>`, `<=`, `>=`, `==`, `!=`.
- Delimitadores: `(`, `)`, `{`, `}`, `[`, `]`, `,`, `;`.
- Tokens nao triviais: `ident`, `int_constant`, `float_constant`, `string_constant`.
- Token especial interno: `EOF`.

Criterios de aceite:

- Existe uma tabela token -> descricao.
- Palavras reservadas sao diferenciadas de identificadores.
- Todos os terminais usados pela gramatica possuem representacao no lexer.

### Task 1.2 - Definir expressoes regulares por token

Tipo: grammar

Criar uma tabela de reconhecimento para tokens nao triviais e documentar o comportamento esperado.

Definicoes iniciais sugeridas:

- `ident`: letra ou `_`, seguida de letras, digitos ou `_`.
- `int_constant`: sequencia de digitos.
- `float_constant`: digitos, ponto, digitos.
- `string_constant`: texto entre aspas duplas.
- Espacos, tabs e quebras de linha devem ser ignorados, mas atualizar linha e coluna.

Criterios de aceite:

- Regexes documentadas em `grammar.py` ou em documento auxiliar.
- Casos ambiguos definidos, como `123.`, `.5`, string sem fechamento e caractere invalido.
- A ordem de reconhecimento evita classificar palavra reservada como `ident`.

### Task 1.3 - Desenhar o automato lexico

Tipo: grammar

Definir os estados do analisador lexico baseado em diagramas de transicao.

Estados sugeridos:

- `START`
- `IDENT_OR_KEYWORD`
- `INTEGER`
- `FLOAT_AFTER_DOT`
- `STRING`
- `STRING_ESCAPE`, se escapes forem aceitos
- `OPERATOR`
- `DELIMITER`
- `ERROR`

Criterios de aceite:

- O automato esta documentado.
- A implementacao em `lexer.py` segue os estados definidos.
- O lexer le caracter por caracter, sem depender apenas de regex global.

### Task 1.4 - Converter BNF para gramatica convencional

Tipo: grammar

Converter a gramatica do enunciado para regras no formato `P -> alpha`, removendo notacoes BNF como `?`, `*`, `+` e alternativas embutidas.

Gramatica original resumida:

```text
PROGRAM -> (STATEMENT | FUNCLIST)?
FUNCLIST -> FUNCDEF FUNCLIST | FUNCDEF
FUNCDEF -> def ident ( PARAMLIST ) { STATELIST }
PARAMLIST -> ((int | float | string) ident , PARAMLIST | (int | float | string) ident)?
STATEMENT -> VARDECL ; | ATRIBSTAT ; | PRINTSTAT ; | READSTAT ; | RETURNSTAT ; | IFSTAT | FORSTAT | { STATELIST } | break ; | ;
VARDECL -> (int | float | string) ident ([int_constant])*
ATRIBSTAT -> LVALUE = (EXPRESSION | ALLOCEXPRESSION | FUNCCALL)
FUNCCALL -> ident ( PARAMLISTCALL )
PARAMLISTCALL -> (ident , PARAMLISTCALL | ident)?
PRINTSTAT -> print EXPRESSION
READSTAT -> read LVALUE
RETURNSTAT -> return
IFSTAT -> if ( EXPRESSION ) STATEMENT (else STATEMENT)?
FORSTAT -> for ( ATRIBSTAT ; EXPRESSION ; ATRIBSTAT ) STATEMENT
STATELIST -> STATEMENT (STATELIST)?
ALLOCEXPRESSION -> new (int | float | string) ([ NUMEXPRESSION ])+
EXPRESSION -> NUMEXPRESSION ((< | > | <= | >= | == | !=) NUMEXPRESSION)?
NUMEXPRESSION -> TERM ((+ | -) TERM)*
TERM -> UNARYEXPR ((* | / | %) UNARYEXPR)*
UNARYEXPR -> (+ | -)? FACTOR
FACTOR -> int_constant | float_constant | string_constant | null | LVALUE | ( NUMEXPRESSION )
LVALUE -> ident ([ NUMEXPRESSION ])*
```

Criterios de aceite:

- Cada regra possui apenas um nao-terminal no lado esquerdo.
- Cada producao esta explicitamente separada.
- Epsilon e representado de forma consistente, por exemplo `EPSILON`.

### Task 1.5 - Remover recursao a esquerda

Tipo: grammar

Verificar e eliminar recursao a esquerda direta e indireta.

Criterios de aceite:

- Existe uma versao da gramatica sem recursao a esquerda.
- Regras auxiliares sao nomeadas de forma clara, por exemplo `NUMEXPRESSION_PRIME`.
- A linguagem aceita permanece equivalente sempre que possivel.

### Task 1.6 - Fatorar a esquerda

Tipo: grammar

Fatorar producoes com prefixos comuns, especialmente onde a decisao LL(1) ficaria ambigua.

Pontos de atencao:

- `PROGRAM`, por causa de `STATEMENT` e `FUNCLIST`.
- `PARAMLIST`.
- `PARAMLISTCALL`.
- `FACTOR`, pois `LVALUE` comeca com `ident`.
- `ATRIBSTAT`, pois alternativas podem comecar com tokens parecidos apos `=`.

Criterios de aceite:

- Producoes de um mesmo nao-terminal nao possuem prefixos conflitantes.
- A gramatica fatorada pode ser usada para calcular FIRST/FOLLOW.

### Task 1.7 - Provar que a gramatica e LL(1)

Tipo: grammar

Calcular FIRST e FOLLOW para todos os nao-terminais e verificar as condicoes LL(1).

Criterios de aceite:

- `FIRST` calculado para todos os nao-terminais.
- `FOLLOW` calculado para todos os nao-terminais.
- Para cada nao-terminal, alternativas possuem conjuntos FIRST disjuntos.
- Para alternativas com `EPSILON`, `FIRST` e `FOLLOW` nao entram em conflito.
- Conflitos encontrados sao registrados e resolvidos antes da implementacao do parser.

## Fase 2 - Analisador lexico - T1

### Task 2.1 - Implementar modelo de token

Tipo: py

Criar uma estrutura para representar tokens.

Campos sugeridos:

- `type`
- `lexeme`
- `line`
- `column`

Criterios de aceite:

- Todos os tokens produzidos carregam linha e coluna inicial.
- O token `EOF` e emitido ao fim da entrada.

### Task 2.2 - Implementar tabela de simbolos

Tipo: py

Implementar `symbol_table.py`.

Comportamento esperado:

- Uma entrada por lexema identificado como `ident`.
- Cada entrada mantem lista de ocorrencias `(linha, coluna)`.
- Palavras reservadas nao entram na tabela de simbolos.

Criterios de aceite:

- Identificadores repetidos compartilham a mesma entrada.
- Todas as ocorrencias sao preservadas.
- A tabela pode ser impressa em formato claro.

### Task 2.3 - Implementar lexer char a char

Tipo: py

Implementar `lexer.py` usando estados de automato.

Responsabilidades:

- Ler o arquivo caracter por caracter.
- Ignorar whitespace atualizando linha e coluna.
- Reconhecer palavras reservadas.
- Reconhecer identificadores.
- Reconhecer constantes inteiras, reais e strings.
- Reconhecer operadores de um ou dois caracteres.
- Reconhecer delimitadores.
- Atualizar a tabela de simbolos ao encontrar `ident`.

Criterios de aceite:

- O lexer gera a lista de tokens na ordem de ocorrencia.
- A tabela de simbolos e preenchida corretamente.
- O lexer nao usa um unico regex global para varrer a entrada.

### Task 2.4 - Reportar erros lexicos

Tipo: py

Capturar caracteres invalidos e tokens malformados.

Erros minimos:

- Caractere desconhecido.
- String sem fechamento.
- Float incompleto, se a linguagem nao aceitar esse formato.
- Sequencia invalida de operador.

Criterios de aceite:

- A mensagem informa linha e coluna.
- Ao encontrar erro lexico, a execucao informa erro de forma simples e clara.
- O parser nao e executado quando ha erro lexico.

### Task 2.5 - Formatar saida do analisador lexico

Tipo: py

Definir saida conforme o enunciado.

Saida sem erro lexico:

- Lista de tokens em ordem.
- Tabela de simbolos.

Saida com erro lexico:

- Mensagem simples de erro lexico com linha e coluna.

Criterios de aceite:

- A lista de tokens e similar ao exemplo do enunciado.
- A tabela de simbolos e legivel.
- A saida nao mistura diagnosticos internos desnecessarios.

## Fase 3 - Analisador sintatico - T2

### Task 3.1 - Representar a gramatica LL(1)

Tipo: py

Implementar `grammar.py` com a gramatica final apos conversao, remocao de recursao a esquerda e fatoracao.

Criterios de aceite:

- Nao-terminais, terminais e producoes estao representados em estruturas de dados simples.
- `EPSILON` e `EOF` sao tratados explicitamente.
- A gramatica implementada corresponde a versao provada como LL(1).

### Task 3.2 - Calcular FIRST

Tipo: py

Implementar calculo de FIRST para terminais, nao-terminais e sequencias de simbolos.

Criterios de aceite:

- FIRST converge para ponto fixo.
- FIRST lida corretamente com `EPSILON`.
- Existem testes unitarios para casos com alternativas e epsilon.

### Task 3.3 - Calcular FOLLOW

Tipo: py

Implementar calculo de FOLLOW para todos os nao-terminais.

Criterios de aceite:

- FOLLOW do simbolo inicial contem `EOF`.
- FOLLOW converge para ponto fixo.
- Existem testes unitarios para propagacao de FOLLOW entre producoes.

### Task 3.4 - Construir tabela LL(1)

Tipo: py

Construir a tabela de reconhecimento sintatico uma unica vez a partir da gramatica, FIRST e FOLLOW.

Criterios de aceite:

- A tabela mapeia `(nao_terminal, terminal)` para uma producao.
- Conflitos na tabela sao detectados e reportados.
- A tabela e criada antes do parse e reutilizada durante a analise.

### Task 3.5 - Implementar parser preditivo LL(1)

Tipo: py

Implementar `parser.py` usando pilha e tabela LL(1).

Fluxo esperado:

- Receber a lista de tokens do lexer.
- Inicializar pilha com `EOF` e simbolo inicial.
- Comparar topo da pilha com token corrente.
- Expandir nao-terminal usando a tabela.
- Aceitar quando pilha e entrada chegam a `EOF`.

Criterios de aceite:

- Entradas validas geram mensagem de sucesso.
- Entradas invalidas geram erro sintatico.
- O parser nao recalcula a tabela a cada passo.

### Task 3.6 - Reportar erros sintaticos com contexto

Tipo: py

Implementar diagnostico exigido no enunciado quando uma entrada da tabela esta vazia.

A mensagem deve indicar:

- Forma sentencial `alpha`.
- Nao-terminal mais a esquerda de `alpha`.
- Token atual da entrada.
- Linha e coluna do token atual, como informacao adicional util.

Criterios de aceite:

- Erros sintaticos sao diferentes de erros lexicos.
- A mensagem deixa claro qual entrada da tabela LL(1) esta vazia.
- A saida nao contem stack trace em uso normal.

### Task 3.7 - Integrar lexer, parser e main

Tipo: py

Implementar `main.py` como ponto unico de execucao.

Comportamento esperado:

- Receber um caminho de arquivo `.lcc`.
- Executar lexer.
- Se nao houver erro lexico, imprimir tokens e tabela de simbolos.
- Executar parser.
- Imprimir sucesso ou erro sintatico.

Criterios de aceite:

- `python3.11 -m src.main examples/prog1.lcc` funciona.
- `make run FILE=examples/prog1.lcc` funciona.
- Falta de argumento ou arquivo inexistente gera erro claro.

## Fase 4 - Programas de exemplo `.lcc`

### Task 4.1 - Escrever programa 1 com pelo menos 100 linhas

Tipo: doc

Criar `examples/prog1.lcc`.

Sugestao:

- Programa com declaracoes, atribuicoes, arrays, `if`, `for`, `print` e `read`.
- Tema: ordenacao ou manipulacao de arrays.

Criterios de aceite:

- Tem pelo menos 100 linhas.
- Nao possui erro lexico.
- Nao possui erro sintatico.
- Usa uma boa variedade da linguagem.

### Task 4.2 - Escrever programa 2 com pelo menos 100 linhas

Tipo: doc

Criar `examples/prog2.lcc`.

Sugestao:

- Programa com operacoes matematicas e chamadas de funcoes.
- Tema: calculos numericos, acumuladores ou simulacao de recursao por repeticao.

Criterios de aceite:

- Tem pelo menos 100 linhas.
- Nao possui erro lexico.
- Nao possui erro sintatico.
- Exercita funcoes, parametros e retorno.

### Task 4.3 - Escrever programa 3 com pelo menos 100 linhas

Tipo: doc

Criar `examples/prog3.lcc`.

Sugestao:

- Programa com entrada/saida, strings e estruturas simples.
- Tema: cadastro simples, processamento de dados ou menu textual.

Criterios de aceite:

- Tem pelo menos 100 linhas.
- Nao possui erro lexico.
- Nao possui erro sintatico.
- Exercita strings, leitura, impressao e blocos condicionais.

## Fase 5 - Testes e ajustes finais

### Task 5.1 - Testar tokens validos

Tipo: test

Criar testes para cada classe de token.

Criterios de aceite:

- Palavras reservadas sao reconhecidas corretamente.
- Identificadores sao reconhecidos e adicionados na tabela de simbolos.
- Numeros inteiros, floats e strings sao reconhecidos.
- Operadores e delimitadores sao reconhecidos.

### Task 5.2 - Testar erros lexicos

Tipo: test

Criar entradas propositalmente invalidas.

Casos minimos:

- Caractere invalido.
- String sem fechamento.
- Float malformado.
- Operador invalido.

Criterios de aceite:

- Cada erro informa linha e coluna.
- O parser nao e chamado apos erro lexico.

### Task 5.3 - Testar parser com programas validos

Tipo: test

Usar programas pequenos e os tres exemplos grandes.

Criterios de aceite:

- Programas validos sao aceitos.
- A mensagem final indica sucesso sintatico.
- Nao ha excecoes nao tratadas.

### Task 5.4 - Testar erros sintaticos

Tipo: test

Criar entradas com erros sintaticos intencionais.

Casos minimos:

- Ponto e virgula ausente.
- Parenteses ausente.
- Chave ausente.
- Expressao incompleta.
- Token inesperado em comando.

Criterios de aceite:

- Cada erro informa a entrada vazia da tabela LL(1).
- A mensagem inclui forma sentencial, nao-terminal mais a esquerda e token atual.

### Task 5.5 - Medir desempenho

Tipo: test

O enunciado atribui T3 ao tempo medio de compilacao dos programas validos. Medir tempo de execucao do lexer e parser nos tres exemplos.

Criterios de aceite:

- Existe uma forma simples de medir tempo, manual ou via target do Makefile.
- Os exemplos grandes executam sem lentidao evidente.
- A tabela LL(1) nao e reconstruida desnecessariamente durante o parse.

### Task 5.6 - Revisao final de entrega

Tipo: release

Checklist antes de enviar ao Moodle:

- `Makefile` existe.
- `README.md` existe.
- Tres arquivos `.lcc` existem em `examples/`.
- Cada `.lcc` tem pelo menos 100 linhas.
- `make run FILE=examples/prog1.lcc` funciona.
- `make run FILE=examples/prog2.lcc` funciona.
- `make run FILE=examples/prog3.lcc` funciona.
- `make test` funciona.
- Cabecalho com integrantes foi adicionado aos arquivos principais.
- Qualquer modificacao na linguagem foi documentada nos analisadores e no README.
- Nao ha warnings, stack traces ou saidas confusas em execucao normal.

## Ordem recomendada de implementacao

1. Criar estrutura, `Makefile` e `README.md`.
2. Documentar tokens, regexes e automato lexico.
3. Converter e ajustar a gramatica ate ficar LL(1).
4. Implementar `Token`, `SymbolTable` e `Lexer`.
5. Testar lexer e erros lexicos.
6. Implementar FIRST, FOLLOW e tabela LL(1).
7. Implementar parser preditivo.
8. Testar parser e erros sintaticos.
9. Criar os tres programas `.lcc`.
10. Rodar checklist final e medir desempenho.

## Saidas esperadas

### Sem erro lexico

```text
TOKENS:
[def, ident, (, int, ident, ,, int, ident, ), {, ...]

SYMBOL TABLE:
SM -> [(3, 5), (4, 1), (5, 1)]
C  -> [(8, 5), (11, 1), ...]
```

### Com erro lexico

```text
Erro lexico na linha 4, coluna 12: caractere invalido '@'
```

### Sem erro sintatico

```text
Analise sintatica concluida com sucesso.
```

### Com erro sintatico

```text
Erro sintatico na linha 10, coluna 7.
Entrada vazia na tabela M[STATEMENT, else].
Forma sentencial: alpha
Nao-terminal mais a esquerda: STATEMENT
Token atual: else
```

