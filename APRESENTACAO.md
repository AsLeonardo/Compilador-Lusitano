# 🇵🇹 🇧🇷 Compilador Lusitano
## Uma Linguagem de Programação em Português

*Leonardo Alves Silva - 10723113466*	|	*Teoria da computação e compiladores*

---

# Por que é um Compilador?

Um **compilador** é um programa que traduz código escrito em uma linguagem de programação (linguagem fonte) para outra linguagem (linguagem alvo).

## Lusitano: Transpilador

O Compilador Lusitano é tecnicamente um **transpilador** (source-to-source compiler):

```
┌─────────────────┐     ┌─────────────┐     ┌─────────────┐
│  Código Fonte   │ ──► │  Compilador │ ──► │   Python    │
│   (Lusitano)    │     │  Lusitano   │     │   (Target)  │
└─────────────────┘     └─────────────┘     └─────────────┘
```

### Por que ainda é um compilador?

1. **Mesmas fases clássicas**: Scanner, Parser, Análise Semântica
2. **Transforma linguagem A em B**: Lusitano → Python
3. **Análise completa**: Verifica erros léxicos, sintáticos e semânticos
4. **Gera código executável**: O Python gerado pode ser executado diretamente

---

# Unicidade do Projeto

## O que torna Lusitano especial?

### 1. Sintaxe 100% em Português
```lusitano
funcao principal() {
    var nome: texto = "Mundo"
    se (idade >= 18) {
        escreva("Maior de idade")
    } senao {
        escreva("Menor de idade")
    }
}
```

### 2. Palavras-chave Nativas
| Lusitano | Equivalente |
|----------|-------------|
| `funcao` | function |
| `se/senao` | if/else |
| `enquanto` | while |
| `para...de...ate` | for |
| `retorna` | return |
| `escreva` | print |
| `leia` | input |
| `verdadeiro/falso` | true/false |
| `inteiro/real/texto/logico` | int/float/str/bool |

### 3. Raridade
- Poucas linguagens de programação têm sintaxe em português
- Ainda menos são compiladores completos com análise semântica
- Valor didático imenso para lusófonos

---

# Arquitetura do Compilador

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONT END                                 │
│  ┌───────────┐   ┌───────────┐   ┌────────────────┐             │
│  │  Scanner  │──►│  Parser   │──►│   Semântico    │             │
│  │  (Léxico) │   │ (Sintaxe) │   │ (Verificação)  │             │
│  └───────────┘   └───────────┘   └────────────────┘             │
│       │               │                  │                       │
│       ▼               ▼                  ▼                       │
│   [Tokens]          [AST]        [Tabela Símbolos]              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        BACK END                                  │
│  ┌────────────────┐   ┌────────────────┐                        │
│  │   Gerador de   │──►│  Código Python │                        │
│  │     Código     │   │   Executável   │                        │
│  └────────────────┘   └────────────────┘                        │
└─────────────────────────────────────────────────────────────────┘
```

---

# FASE 1: Scanner (Análise Léxica)

## O que faz?
Transforma o código fonte (texto) em uma sequência de **tokens** (unidades léxicas).

## Analogia
Como dividir uma frase em palavras e pontuação:
- "O gato dormiu." → ["O", "gato", "dormiu", "."]

## Exemplo Lusitano

**Entrada:**
```lusitano
var idade: inteiro = 25
```

**Saída (Tokens):**
```
┌─────────┬─────────────────┬─────────┐
│ Tipo    │ Lexema          │ Valor   │
├─────────┼─────────────────┼─────────┤
│ VAR     │ "var"           │ -       │
│ IDENT   │ "idade"         │ -       │
│ DOIS_PT │ ":"             │ -       │
│ INTEIRO │ "inteiro"       │ -       │
│ ATRIB   │ "="             │ -       │
│ NUMERO  │ "25"            │ 25      │
└─────────┴─────────────────┴─────────┘
```

## Responsabilidades
- ✓ Identificar palavras-chave (se, enquanto, funcao...)
- ✓ Reconhecer identificadores (nomes de variáveis)
- ✓ Processar literais (números, strings)
- ✓ Detectar operadores e delimitadores
- ✓ Ignorar comentários e espaços
- ✓ Reportar erros léxicos (caracteres inválidos)

---

# FASE 2: Parser (Análise Sintática)

## O que faz?
Verifica se a sequência de tokens segue a **gramática** da linguagem e constrói a **AST** (Abstract Syntax Tree).

## Técnica Utilizada
**Descida Recursiva (Recursive Descent)** - cada regra gramatical vira uma função.

## Gramática Simplificada
```
programa     → declaracao*
declaracao   → funcao | var | statement
funcao       → "funcao" IDENT "(" params? ")" bloco
statement    → se | enquanto | para | escreva | expressao
expressao    → atribuicao | comparacao | termo | fator
```

## Exemplo: AST

**Código:**
```lusitano
se (x > 10) {
    escreva("Grande")
}
```

**Árvore Sintática:**
```
📄 Programa
└── 🔀 Se
    ├── Condição: ➕ Binária (>)
    │   ├── 🔤 Variável: x
    │   └── 📌 Literal: 10
    └── Então: 📁 Bloco
        └── 🖨️ Escreva: "Grande"
```

## Responsabilidades
- ✓ Verificar estrutura gramatical
- ✓ Construir árvore sintática abstrata
- ✓ Reportar erros de sintaxe
- ✓ Suportar precedência de operadores

---

# FASE 3: Análise Semântica

## O que faz?
Verifica a **correção lógica** do programa que a sintaxe não consegue garantir.

## Verificações Realizadas

### 1. Declaração de Variáveis
```lusitano
// ❌ ERRO: variável não declarada
escreva(x)

// ✓ CORRETO
var x: inteiro = 10
escreva(x)
```

### 2. Compatibilidade de Tipos
```lusitano
// ❌ ERRO: não pode somar texto com inteiro
var resultado: inteiro = "olá" + 5

// ✓ CORRETO
var resultado: inteiro = 10 + 5
```

### 3. Escopo de Variáveis
```lusitano
funcao teste() {
    var local: inteiro = 1
}
// ❌ ERRO: 'local' não existe fora da função
escreva(local)
```

### 4. Tipos de Retorno
```lusitano
// ❌ ERRO: deveria retornar inteiro
funcao soma(a: inteiro, b: inteiro): inteiro {
    retorna "texto"
}
```

### 5. Atribuição a Constantes
```lusitano
const PI: real = 3.14159
// ❌ ERRO: não pode alterar constante
PI = 3.14
```

## Tabela de Símbolos
```
┌──────────────┬──────────┬────────────┬────────┐
│ Nome         │ Tipo     │ Categoria  │ Escopo │
├──────────────┼──────────┼────────────┼────────┤
│ fatorial     │ funcao   │ funcao     │ 0      │
│ n            │ inteiro  │ parametro  │ 1      │
│ principal    │ funcao   │ funcao     │ 0      │
│ nome         │ texto    │ variavel   │ 1      │
│ PI           │ real     │ constante  │ 1      │
└──────────────┴──────────┴────────────┴────────┘
```

---

# FASE 4: Geração de Código

## O que faz?
Percorre a AST e gera código Python equivalente.

## Padrão Visitor
Cada tipo de nó da AST tem um método de visita que gera o código correspondente.

## Exemplo de Transpilação

**Entrada (Lusitano):**
```lusitano
funcao fatorial(n: inteiro): inteiro {
    se (n <= 1) {
        retorna 1
    }
    retorna n * fatorial(n - 1)
}

funcao principal() {
    para i de 1 ate 5 {
        escreva(i, "! = ", fatorial(i))
    }
}
```

**Saída (Python):**
```python
def fatorial(n):
    if (n <= 1):
        return 1
    return (n * fatorial((n - 1)))

def principal():
    for i in range(1, 5 + 1):
        print(i, '! = ', fatorial(i), sep='')

if __name__ == '__main__':
    principal()
```

## Mapeamentos
| Lusitano | Python |
|----------|--------|
| `se/senao` | `if/else` |
| `enquanto` | `while` |
| `para i de X ate Y` | `for i in range(X, Y+1)` |
| `e` / `ou` / `nao` | `and` / `or` / `not` |
| `verdadeiro/falso` | `True/False` |

---

# Fluxo Completo de Compilação

```
┌────────────────────────────────────────────────────────────────────┐
│                     CÓDIGO FONTE LUSITANO                          │
│  funcao principal() {                                              │
│      var x: inteiro = 10                                           │
│      escreva("Valor: ", x)                                         │
│  }                                                                  │
└────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────┐
│                    1. ANÁLISE LÉXICA (Scanner)                     │
│  [FUNCAO][IDENT:principal][ABRE_PAREN][FECHA_PAREN][ABRE_CHAVE]   │
│  [VAR][IDENT:x][DOIS_PONTOS][TIPO_INTEIRO][ATRIB][NUM:10]...      │
└────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────┐
│                    2. ANÁLISE SINTÁTICA (Parser)                   │
│  Programa                                                          │
│  └── Funcao: principal                                             │
│      └── Bloco                                                     │
│          ├── DeclVar: x = 10 (inteiro)                            │
│          └── Escreva: ["Valor: ", x]                              │
└────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────┐
│                    3. ANÁLISE SEMÂNTICA                            │
│  ✓ Função 'principal' declarada                                    │
│  ✓ Variável 'x' declarada como inteiro                            │
│  ✓ Tipos compatíveis na atribuição                                │
│  ✓ Tabela de símbolos construída                                  │
└────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────┐
│                    4. GERAÇÃO DE CÓDIGO                            │
│  def principal():                                                  │
│      x = 10                                                        │
│      print('Valor: ', x, sep='')                                  │
│                                                                    │
│  if __name__ == '__main__':                                       │
│      principal()                                                   │
└────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌────────────────────────────────────────────────────────────────────┐
│                        EXECUÇÃO                                     │
│  $ python programa.py                                              │
│  Valor: 10                                                         │
└────────────────────────────────────────────────────────────────────┘
```

---

# Demonstração Prática

## Programa de Exemplo
```lusitano
// Programa de demonstração
funcao fatorial(n: inteiro): inteiro {
    se (n <= 1) {
        retorna 1
    }
    retorna n * fatorial(n - 1)
}

funcao principal(): inteiro {
    escreva("Cálculo de Fatoriais:")
    para n de 1 ate 6 {
        escreva(n, "! = ", fatorial(n))
    }
    retorna 0
}
```

## Saída do Compilador
```
╔═══════════════════════════════════════╗
║   COMPILADOR LUSITANO                 ║
╚═══════════════════════════════════════╝

✓ Análise léxica: 48 tokens
✓ Análise sintática: 2 funções
✓ Análise semântica: sem erros
✓ Código Python gerado

EXECUÇÃO:
Cálculo de Fatoriais:
1! = 1
2! = 2
3! = 6
4! = 24
5! = 120
6! = 720
```

---

# Tratamento de Erros

## Erros Léxicos
```
╔══════════════════════════════════════════╗
║  ERRO LÉXICO na linha 5, coluna 12       ║
╠══════════════════════════════════════════╣
║  Caractere não reconhecido: '@'          ║
║  Contexto: var email@ = "teste"          ║
║               ^                          ║
╚══════════════════════════════════════════╝
```

## Erros Sintáticos
```
╔══════════════════════════════════════════╗
║  ERRO SINTÁTICO na linha 3, coluna 5     ║
╠══════════════════════════════════════════╣
║  Esperado ')' após condição              ║
║  Token encontrado: ABRE_CHAVE ('{')      ║
╚══════════════════════════════════════════╝
```

## Erros Semânticos
```
╔══════════════════════════════════════════╗
║  ERRO SEMÂNTICO na linha 7, coluna 10    ║
╠══════════════════════════════════════════╣
║  Variável 'contador' não foi declarada   ║
╚══════════════════════════════════════════╝
```

---

# Estrutura do Projeto

```
compilador_lusitano/
│
├── lexer.py          # Scanner - Análise Léxica
│   ├── TipoToken     # Enum com todos os tipos de tokens
│   ├── Token         # Estrutura de dados do token
│   ├── Scanner       # Analisador léxico principal
│   └── ErroLexico    # Exceções léxicas
│
├── parser.py         # Parser - Análise Sintática
│   ├── NoAST         # Classes para nós da AST
│   ├── Parser        # Analisador sintático (Descida Recursiva)
│   ├── VisitanteAST  # Interface Visitor
│   └── ErroSintatico # Exceções sintáticas
│
├── semantico.py      # Análise Semântica
│   ├── Tipo          # Sistema de tipos
│   ├── Simbolo       # Entrada da tabela de símbolos
│   ├── TabelaSimbolos# Gerenciamento de escopos
│   └── AnalisadorSemantico # Visitor para verificação
│
├── lusitano.py       # Compilador Principal
│   ├── GeradorPython # Transpilador para Python
│   └── CompiladorLusitano # Integração de todas as fases
│
└── exemplos/
    └── fibonacci.lus # Programas de exemplo
```

---

# Conclusão

## O que foi implementado

✓ **Scanner Completo**
- 40+ tipos de tokens
- Suporte a strings, números, comentários
- Mensagens de erro detalhadas

✓ **Parser Recursivo**
- Gramática completa da linguagem
- AST com 20+ tipos de nós
- Recuperação de erros

✓ **Análise Semântica**
- Tabela de símbolos com escopos
- Verificação de tipos
- Detecção de erros lógicos

✓ **Gerador de Código**
- Transpilação para Python
- Código executável diretamente

## Diferenciais

 **Sintaxe 100% Português** - Única no mercado acadêmico
 **Didático** - Código comentado e organizado
 **Extensível** - Fácil adicionar novos recursos
 **Prático** - Gera Python executável

## Compilador Lusitano
*Uma linguagem de programação em português*

-

***Leonardo Alves Silva - 10723113466***
***Teoria da computação e compiladores***
