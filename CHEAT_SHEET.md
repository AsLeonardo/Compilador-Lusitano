# Cheat Sheet: Comandos do Compilador Lusitano

*Leonardo Alves Silva - 10723113466*	|	*Teoria da computação e compiladores*

## Especifique o Arquivo

```bash
python lusitano.py fibonacci.lus        # CORRETO
python lusitano.py                      # Apenas executa o exemplo
```

---

## Comando Mais Rápido

```bash
python lusitano.py fibonacci.lus -o fibonacci.py --run
```

**Este:**

1. Lê `fibonacci.lus`
2. Passa por todas as fases (léxica → sintática → semântica)
3. Gera `fibonacci.py`
4. Executa o programa imediatamente

---

## Todos os Comandos Disponíveis

### 1. Compilar e Executar

```bash
python lusitano.py fibonacci.lus --run
```

- Compila
- Executa
- Não salva arquivo

---

### 2. Compilar e Salvar

```bash
python lusitano.py fibonacci.lus -o fibonacci.py
```

- Compila
- Salva em `fibonacci.py`
- Não executa

Depois execute com:
```bash
python fibonacci.py
```

---

### 3. Compilar, Salvar E Executar

```bash
python lusitano.py fibonacci.lus -o fibonacci.py --run
```

- Compila
- Salva em `fibonacci.py`
- Executa

---

### 4. Apenas Compilar (Ver Resultado)

```bash
python lusitano.py fibonacci.lus
```

- Compila
- Mostra todas as fases
- Não salva
- Não executa

---

### 5. Salvar com Nome Customizado

```bash
python lusitano.py fibonacci.lus -o meu_programa.py
```

Gera `meu_programa.py` em vez de `fibonacci.py`

---

- `-o` = `--output`
- `-r` = `--run`

---

## Fluxos Comuns

### 1: "Quero ver funcionando"

```bash
python lusitano.py fibonacci.lus --run
```

### 2: "Quero revisar o código Python antes de rodar"

```bash
python lusitano.py fibonacci.lus -o fibonacci.py
# Abra fibonacci.py
python fibonacci.py  # Depois execute
```

### 3: "Quero compilar e salvar"

```bash
python lusitano.py fibonacci.lus -o fibonacci.py
```

---

## Estrutura de Diretórios

Para que tudo funcione, organize assim:

```
meu_projeto/
│
├── lexer.py              ← Arquivo do compilador
├── parser.py             ← Arquivo do compilador
├── semantico.py          ← Arquivo do compilador
├── lusitano.py           ← Arquivo do compilador
│
├── fibonacci.lus         ← SEU código Lusitano
├── outro_programa.lus    ← Outro código Lusitano
│
├── fibonacci.py          ← Gerado automaticamente
└── outro_programa.py     ← Gerado automaticamente
```

---

## Salvar Múltiplas Versões

```bash
# Versão 1
python lusitano.py fibonacci.lus -o fibonacci_v1.py

# Versão 2 (após editar fibonacci.lus)
python lusitano.py fibonacci.lus -o fibonacci_v2.py

# Versão final
python lusitano.py fibonacci.lus -o fibonacci.py --run
```

---

## Entender a Saída

Quando você roda:
```bash
python lusitano.py fibonacci.lus
```

Você vê:

```
╔════════════════════════════════════════════════╗
║         COMPILADOR LUSITANO                   ║
╚════════════════════════════════════════════════╝

[FASE 1: ANÁLISE LÉXICA]
✓ 126 tokens identificados

[FASE 2: ANÁLISE SINTÁTICA]
✓ AST construída
✓ 4 funções encontradas

[FASE 3: ANÁLISE SEMÂNTICA]
✓ Tipos verificados
✓ 0 erros

[GERAÇÃO DE CÓDIGO]
✓ Python gerado
```

## Compilador Lusitano

*Uma linguagem de programação em português*

-

***Leonardo Alves Silva - 10723113466***
***Teoria da computação e compiladores***
