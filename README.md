# LCC-2026-1 Compiler Front-end

Analisador lexico e analisador sintatico LL(1) para a linguagem LCC-2026-1, implementados em Python 3.11.

## Integrante

- Diego Becker de Azevedo.

## Requisitos

- Python 3.11+
- Ambiente Linux/Unix
- `make`

## Como executar

```sh
make run FILE=examples/prog1.lcc
```

Tambem e possivel executar diretamente:

```sh
python3.11 -m src.main examples/prog1.lcc
```

## Como testar

```sh
make test
```

## Saida esperada

Sem erros lexicos, o programa imprime a lista de tokens e a tabela de simbolos. Em seguida, executa a analise sintatica e informa se a entrada pertence a linguagem.

Com erro lexico, a execucao informa linha e coluna do erro e nao executa o parser.

Com erro sintatico, a execucao informa a entrada vazia da tabela LL(1), o nao-terminal analisado e o token atual.

## Observacoes sobre a linguagem

A implementacao segue a gramatica LCC-2026-1 do enunciado. O analisador lexico reconhece comentarios de linha iniciados por `//` como extensao pratica para permitir cabecalhos nos programas de exemplo.
