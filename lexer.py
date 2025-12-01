"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    COMPILADOR LUSITANO - ANALISADOR LÉXICO                    ║
╚═══════════════════════════════════════════════════════════════════════════════╝

O Scanner (Analisador Léxico) é responsável por:
- Ler o código fonte caractere por caractere
- Agrupar caracteres em tokens (unidades léxicas)
- Identificar palavras-chave, identificadores, números, operadores
- Reportar erros léxicos (caracteres inválidos, strings não fechadas, etc.)
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional, Any
import re



# DEFINIÇÃO DOS TIPOS DE TOKENS


class TipoToken(Enum):
    """Enumeração de todos os tipos de tokens da linguagem Lusitano."""
    
    
    # LITERAIS
    # ─────────────────────────────────────────────────────────────────────────
    NUMERO_INTEIRO = auto()    # 42, -10, 0
    NUMERO_REAL = auto()       # 3.14, -0.5
    TEXTO = auto()             # "Olá, mundo!"
    VERDADEIRO = auto()        # verdadeiro
    FALSO = auto()             # falso
    
    
    # IDENTIFICADORES E PALAVRAS-CHAVE
    # ─────────────────────────────────────────────────────────────────────────
    IDENTIFICADOR = auto()     # nome_variavel, minhaFuncao
    
    # Tipos de dados
    TIPO_INTEIRO = auto()      # inteiro
    TIPO_REAL = auto()         # real
    TIPO_TEXTO = auto()        # texto
    TIPO_LOGICO = auto()       # logico
    TIPO_VAZIO = auto()        # vazio (void)
    
    # Estruturas de controle
    SE = auto()                # se
    SENAO = auto()             # senao
    SENAOSE = auto()           # senaose (else if)
    ENQUANTO = auto()          # enquanto
    PARA = auto()              # para
    DE = auto()                # de (usado em 'para')
    ATE = auto()               # ate (usado em 'para')
    PASSO = auto()             # passo (step em for)
    FACA = auto()              # faca (do)
    REPITA = auto()            # repita (repeat)
    
    # Funções
    FUNCAO = auto()            # funcao
    RETORNA = auto()           # retorna
    
    # Entrada/Saída
    ESCREVA = auto()           # escreva (print)
    LEIA = auto()              # leia (input)
    
    # Operadores lógicos (palavras)
    E = auto()                 # e (and)
    OU = auto()                # ou (or)
    NAO = auto()               # nao (not)
    
    # Declaração
    VAR = auto()               # var (declaração de variável)
    CONST = auto()             # const (constante)
    
    
    # OPERADORES ARITMÉTICOS
    # ─────────────────────────────────────────────────────────────────────────
    MAIS = auto()              # +
    MENOS = auto()             # -
    MULTIPLICA = auto()        # *
    DIVIDE = auto()            # /
    MODULO = auto()            # %
    POTENCIA = auto()          # **
    
    
    # OPERADORES RELACIONAIS
    # ─────────────────────────────────────────────────────────────────────────
    IGUAL = auto()             # ==
    DIFERENTE = auto()         # !=
    MENOR = auto()             # <
    MENOR_IGUAL = auto()       # <=
    MAIOR = auto()             # >
    MAIOR_IGUAL = auto()       # >=
    
    
    # OPERADORES DE ATRIBUIÇÃO
    # ─────────────────────────────────────────────────────────────────────────
    ATRIBUICAO = auto()        # =
    MAIS_IGUAL = auto()        # +=
    MENOS_IGUAL = auto()       # -=
    MULT_IGUAL = auto()        # *=
    DIV_IGUAL = auto()         # /=
    
    
    # DELIMITADORES
    # ─────────────────────────────────────────────────────────────────────────
    ABRE_PAREN = auto()        # (
    FECHA_PAREN = auto()       # )
    ABRE_CHAVE = auto()        # {
    FECHA_CHAVE = auto()       # }
    ABRE_COLCHETE = auto()     # [
    FECHA_COLCHETE = auto()    # ]
    VIRGULA = auto()           # ,
    PONTO_VIRGULA = auto()     # ;
    DOIS_PONTOS = auto()       # :
    PONTO = auto()             # .
    SETA = auto()              # ->
    
    # ─────────────────────────────────────────────────────────────────────────
    # ESPECIAIS
    # ─────────────────────────────────────────────────────────────────────────
    FIM_ARQUIVO = auto()       # EOF
    NOVA_LINHA = auto()        # \n (opcional, para linguagens sensíveis)
    COMENTARIO = auto()        # // ou /* */



# MAPEAMENTO DE PALAVRAS-CHAVE
# ═══════════════════════════════════════════════════════════════════════════════

PALAVRAS_CHAVE = {
    # Tipos
    "inteiro": TipoToken.TIPO_INTEIRO,
    "real": TipoToken.TIPO_REAL,
    "texto": TipoToken.TIPO_TEXTO,
    "logico": TipoToken.TIPO_LOGICO,
    "vazio": TipoToken.TIPO_VAZIO,
    
    # Valores booleanos
    "verdadeiro": TipoToken.VERDADEIRO,
    "falso": TipoToken.FALSO,
    
    # Controle de fluxo
    "se": TipoToken.SE,
    "senao": TipoToken.SENAO,
    "senaose": TipoToken.SENAOSE,
    "enquanto": TipoToken.ENQUANTO,
    "para": TipoToken.PARA,
    "de": TipoToken.DE,
    "ate": TipoToken.ATE,
    "passo": TipoToken.PASSO,
    "faca": TipoToken.FACA,
    "repita": TipoToken.REPITA,
    
    # Funções
    "funcao": TipoToken.FUNCAO,
    "retorna": TipoToken.RETORNA,
    
    # I/O
    "escreva": TipoToken.ESCREVA,
    "leia": TipoToken.LEIA,
    
    # Operadores lógicos
    "e": TipoToken.E,
    "ou": TipoToken.OU,
    "nao": TipoToken.NAO,
    
    # Declarações
    "var": TipoToken.VAR,
    "const": TipoToken.CONST,
}



# ESTRUTURA DO TOKEN
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Token:
    """
    Representa uma unidade léxica (token) do código fonte.
    
    Attributes:
        tipo: O tipo do token (palavra-chave, operador, etc.)
        lexema: O texto original do código fonte
        valor: O valor processado (ex: número convertido para int/float)
        linha: Número da linha onde o token aparece
        coluna: Posição na linha onde o token começa
    """
    tipo: TipoToken
    lexema: str
    valor: Any
    linha: int
    coluna: int
    
    def __repr__(self):
        if self.valor is not None and self.valor != self.lexema:
            return f"Token({self.tipo.name}, '{self.lexema}', valor={self.valor}, L{self.linha}:C{self.coluna})"
        return f"Token({self.tipo.name}, '{self.lexema}', L{self.linha}:C{self.coluna})"
    
    def para_dict(self):
        """Converte o token para dicionário (útil para visualização)."""
        return {
            "tipo": self.tipo.name,
            "lexema": self.lexema,
            "valor": self.valor,
            "posicao": f"L{self.linha}:C{self.coluna}"
        }



# ERROS LÉXICOS
# ═══════════════════════════════════════════════════════════════════════════════

class ErroLexico(Exception):
    """Exceção para erros encontrados durante a análise léxica."""
    
    def __init__(self, mensagem: str, linha: int, coluna: int, contexto: str = ""):
        self.mensagem = mensagem
        self.linha = linha
        self.coluna = coluna
        self.contexto = contexto
        super().__init__(self.formatar_erro())
    
    def formatar_erro(self) -> str:
        erro = f"\n╔══════════════════════════════════════════════════════════════╗\n"
        erro += f"║  ERRO LÉXICO na linha {self.linha}, coluna {self.coluna}\n"
        erro += f"╠══════════════════════════════════════════════════════════════╣\n"
        erro += f"║  {self.mensagem}\n"
        if self.contexto:
            erro += f"╠══════════════════════════════════════════════════════════════╣\n"
            erro += f"║  Contexto: {self.contexto}\n"
            erro += f"║  {' ' * (10 + self.coluna)}^\n"
        erro += f"╚══════════════════════════════════════════════════════════════╝"
        return erro



# ANALISADOR LÉXICO (SCANNER)
# ═══════════════════════════════════════════════════════════════════════════════

class Scanner:
    """
    Analisador Léxico para a linguagem Lusitano.
    
    Converte o código fonte em uma sequência de tokens, identificando:
    - Palavras-chave e identificadores
    - Números (inteiros e reais)
    - Strings
    - Operadores e delimitadores
    - Comentários (que são ignorados)
    """
    
    def __init__(self, codigo_fonte: str):
        self.fonte = codigo_fonte
        self.tokens: List[Token] = []
        
        # Posição atual no código
        self.inicio = 0      # Início do token atual
        self.atual = 0       # Posição atual de leitura
        self.linha = 1       # Linha atual
        self.coluna = 1      # Coluna atual
        self.coluna_inicio = 1  # Coluna do início do token
    
    
    # MÉTODOS AUXILIARES
    # ─────────────────────────────────────────────────────────────────────────
    
    def fim_codigo(self) -> bool:
        """Verifica se chegamos ao fim do código fonte."""
        return self.atual >= len(self.fonte)
    
    def avancar(self) -> str:
        """Avança um caractere e retorna o caractere atual."""
        char = self.fonte[self.atual]
        self.atual += 1
        if char == '\n':
            self.linha += 1
            self.coluna = 1
        else:
            self.coluna += 1
        return char
    
    def espiar(self) -> str:
        """Retorna o caractere atual sem avançar."""
        if self.fim_codigo():
            return '\0'
        return self.fonte[self.atual]
    
    def espiar_proximo(self) -> str:
        """Retorna o próximo caractere sem avançar."""
        if self.atual + 1 >= len(self.fonte):
            return '\0'
        return self.fonte[self.atual + 1]
    
    def combinar(self, esperado: str) -> bool:
        """Avança se o caractere atual for o esperado."""
        if self.fim_codigo() or self.fonte[self.atual] != esperado:
            return False
        self.atual += 1
        self.coluna += 1
        return True
    
    def lexema_atual(self) -> str:
        """Retorna o texto do token atual."""
        return self.fonte[self.inicio:self.atual]
    
    def adicionar_token(self, tipo: TipoToken, valor: Any = None):
        """Adiciona um token à lista."""
        lexema = self.lexema_atual()
        if valor is None:
            valor = lexema
        self.tokens.append(Token(tipo, lexema, valor, self.linha, self.coluna_inicio))
    
    def linha_atual_contexto(self) -> str:
        """Retorna a linha atual para contexto de erro."""
        inicio_linha = self.fonte.rfind('\n', 0, self.inicio) + 1
        fim_linha = self.fonte.find('\n', self.atual)
        if fim_linha == -1:
            fim_linha = len(self.fonte)
        return self.fonte[inicio_linha:fim_linha]
    
    
    # ANÁLISE DE TOKENS ESPECÍFICOS
    # ─────────────────────────────────────────────────────────────────────────
    
    def analisar_string(self):
        """Analisa uma string delimitada por aspas."""
        aspas = self.fonte[self.atual - 1]  # " ou '
        valor = ""
        
        while not self.fim_codigo() and self.espiar() != aspas:
            char = self.espiar()
            
            # Verifica fim de linha sem fechar string
            if char == '\n':
                raise ErroLexico(
                    "String não terminada - encontrado fim de linha",
                    self.linha, self.coluna_inicio,
                    self.linha_atual_contexto()
                )
            
            # Processa caracteres de escape
            if char == '\\':
                self.avancar()
                if self.fim_codigo():
                    raise ErroLexico(
                        "String não terminada após caractere de escape",
                        self.linha, self.coluna_inicio
                    )
                
                escape = self.avancar()
                escapes = {
                    'n': '\n', 't': '\t', 'r': '\r',
                    '\\': '\\', '"': '"', "'": "'"
                }
                valor += escapes.get(escape, f'\\{escape}')
            else:
                valor += self.avancar()
        
        if self.fim_codigo():
            raise ErroLexico(
                "String não terminada - fim de arquivo inesperado",
                self.linha, self.coluna_inicio,
                self.linha_atual_contexto()
            )
        
        # Consome a aspa de fechamento
        self.avancar()
        self.adicionar_token(TipoToken.TEXTO, valor)
    
    def analisar_numero(self):
        """Analisa um número (inteiro ou real)."""
        # Consome todos os dígitos da parte inteira
        while self.espiar().isdigit():
            self.avancar()
        
        # Verifica se há parte decimal
        is_real = False
        if self.espiar() == '.' and self.espiar_proximo().isdigit():
            is_real = True
            self.avancar()  # Consome o ponto
            
            while self.espiar().isdigit():
                self.avancar()
        
        # Verifica notação científica (1e10, 2.5e-3)
        if self.espiar().lower() == 'e':
            is_real = True
            self.avancar()
            
            if self.espiar() in ('+', '-'):
                self.avancar()
            
            if not self.espiar().isdigit():
                raise ErroLexico(
                    "Número em notação científica inválido - esperado dígito após 'e'",
                    self.linha, self.coluna,
                    self.linha_atual_contexto()
                )
            
            while self.espiar().isdigit():
                self.avancar()
        
        lexema = self.lexema_atual()
        if is_real:
            self.adicionar_token(TipoToken.NUMERO_REAL, float(lexema))
        else:
            self.adicionar_token(TipoToken.NUMERO_INTEIRO, int(lexema))
    
    def analisar_identificador(self):
        """Analisa um identificador ou palavra-chave."""
        while self.espiar().isalnum() or self.espiar() == '_':
            self.avancar()
        
        lexema = self.lexema_atual()
        
        # Verifica se é palavra-chave
        tipo = PALAVRAS_CHAVE.get(lexema.lower())
        if tipo is None:
            tipo = TipoToken.IDENTIFICADOR
        
        self.adicionar_token(tipo)
    
    def analisar_comentario_linha(self):
        """Ignora comentário de linha (//)."""
        while not self.fim_codigo() and self.espiar() != '\n':
            self.avancar()
    
    def analisar_comentario_bloco(self):
        """Ignora comentário de bloco (/* */)."""
        linha_inicio = self.linha
        
        while not self.fim_codigo():
            if self.espiar() == '*' and self.espiar_proximo() == '/':
                self.avancar()  # *
                self.avancar()  # /
                return
            self.avancar()
        
        raise ErroLexico(
            f"Comentário de bloco não fechado (iniciado na linha {linha_inicio})",
            self.linha, self.coluna
        )
    
    
    # SCANNER PRINCIPAL
    # ─────────────────────────────────────────────────────────────────────────
    
    def escanear_token(self):
        """Escaneia e classifica o próximo token."""
        char = self.avancar()
        
        # Ignora espaços em branco
        if char in ' \t\r\n':
            return
        
        # ─── Strings ───
        if char in '"\'':
            self.analisar_string()
            return
        
        # ─── Números ───
        if char.isdigit():
            self.analisar_numero()
            return
        
        # ─── Identificadores e palavras-chave ───
        if char.isalpha() or char == '_':
            self.analisar_identificador()
            return
        
        # ─── Operadores e delimitadores ───
        match char:
            # Parênteses e chaves
            case '(': self.adicionar_token(TipoToken.ABRE_PAREN)
            case ')': self.adicionar_token(TipoToken.FECHA_PAREN)
            case '{': self.adicionar_token(TipoToken.ABRE_CHAVE)
            case '}': self.adicionar_token(TipoToken.FECHA_CHAVE)
            case '[': self.adicionar_token(TipoToken.ABRE_COLCHETE)
            case ']': self.adicionar_token(TipoToken.FECHA_COLCHETE)
            
            # Pontuação
            case ',': self.adicionar_token(TipoToken.VIRGULA)
            case ';': self.adicionar_token(TipoToken.PONTO_VIRGULA)
            case ':': self.adicionar_token(TipoToken.DOIS_PONTOS)
            case '.': self.adicionar_token(TipoToken.PONTO)
            
            # Operadores aritméticos
            case '+':
                if self.combinar('='):
                    self.adicionar_token(TipoToken.MAIS_IGUAL)
                else:
                    self.adicionar_token(TipoToken.MAIS)
            
            case '-':
                if self.combinar('='):
                    self.adicionar_token(TipoToken.MENOS_IGUAL)
                elif self.combinar('>'):
                    self.adicionar_token(TipoToken.SETA)
                else:
                    self.adicionar_token(TipoToken.MENOS)
            
            case '*':
                if self.combinar('*'):
                    self.adicionar_token(TipoToken.POTENCIA)
                elif self.combinar('='):
                    self.adicionar_token(TipoToken.MULT_IGUAL)
                else:
                    self.adicionar_token(TipoToken.MULTIPLICA)
            
            case '/':
                if self.combinar('/'):
                    self.analisar_comentario_linha()
                elif self.combinar('*'):
                    self.analisar_comentario_bloco()
                elif self.combinar('='):
                    self.adicionar_token(TipoToken.DIV_IGUAL)
                else:
                    self.adicionar_token(TipoToken.DIVIDE)
            
            case '%': self.adicionar_token(TipoToken.MODULO)
            
            # Operadores relacionais e atribuição
            case '=':
                if self.combinar('='):
                    self.adicionar_token(TipoToken.IGUAL)
                else:
                    self.adicionar_token(TipoToken.ATRIBUICAO)
            
            case '!':
                if self.combinar('='):
                    self.adicionar_token(TipoToken.DIFERENTE)
                else:
                    raise ErroLexico(
                        f"Caractere inesperado: '{char}'. Você quis dizer 'nao' ou '!='?",
                        self.linha, self.coluna_inicio,
                        self.linha_atual_contexto()
                    )
            
            case '<':
                if self.combinar('='):
                    self.adicionar_token(TipoToken.MENOR_IGUAL)
                else:
                    self.adicionar_token(TipoToken.MENOR)
            
            case '>':
                if self.combinar('='):
                    self.adicionar_token(TipoToken.MAIOR_IGUAL)
                else:
                    self.adicionar_token(TipoToken.MAIOR)
            
            # Caractere não reconhecido
            case _:
                raise ErroLexico(
                    f"Caractere não reconhecido: '{char}' (código: {ord(char)})",
                    self.linha, self.coluna_inicio,
                    self.linha_atual_contexto()
                )
    
    def escanear(self) -> List[Token]:
        """
        Executa a análise léxica completa do código fonte.
        
        Returns:
            Lista de tokens encontrados, terminando com FIM_ARQUIVO.
        """
        print("╔═══════════════════════════════════════════════════════════════╗")
        print("║            INICIANDO ANÁLISE LÉXICA (SCANNER)                 ║")
        print("╚═══════════════════════════════════════════════════════════════╝")
        
        while not self.fim_codigo():
            self.inicio = self.atual
            self.coluna_inicio = self.coluna
            self.escanear_token()
        
        # Adiciona token de fim de arquivo
        self.tokens.append(Token(
            TipoToken.FIM_ARQUIVO, 
            "", 
            None, 
            self.linha, 
            self.coluna
        ))
        
        print(f"✓ Análise léxica concluída: {len(self.tokens)} tokens encontrados\n")
        return self.tokens
    
    def imprimir_tokens(self):
        """Imprime os tokens de forma formatada para visualização."""
        print("\n┌─────────────────────────────────────────────────────────────────┐")
        print("│                      TABELA DE TOKENS                            │")
        print("├────────┬─────────────────────┬───────────────────┬───────────────┤")
        print("│ Linha  │ Tipo                │ Lexema            │ Valor         │")
        print("├────────┼─────────────────────┼───────────────────┼───────────────┤")
        
        for token in self.tokens:
            linha = f"L{token.linha}:C{token.coluna}"
            tipo = token.tipo.name[:19]
            lexema = repr(token.lexema)[:17]
            valor = repr(token.valor)[:13] if token.valor != token.lexema else "-"
            
            print(f"│ {linha:<6} │ {tipo:<19} │ {lexema:<17} │ {valor:<13} │")
        
        print("└────────┴─────────────────────┴───────────────────┴───────────────┘")



# TESTE DO SCANNER
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    codigo_teste = '''
// Programa de exemplo em Lusitano
funcao principal() {
    var nome: texto = "Mundo"
    var idade: inteiro = 25
    var pi: real = 3.14159
    var ativo: logico = verdadeiro
    
    escreva("Olá, " + nome + "!")
    
    se (idade >= 18) {
        escreva("Maior de idade")
    } senao {
        escreva("Menor de idade")
    }
    
    var soma: inteiro = 0
    para i de 1 ate 10 {
        soma = soma + i
    }
    
    enquanto (soma > 0) {
        soma = soma - 1
    }
    
    retorna 0
}
'''
    
    try:
        scanner = Scanner(codigo_teste)
        tokens = scanner.escanear()
        scanner.imprimir_tokens()
    except ErroLexico as e:
        print(e)
