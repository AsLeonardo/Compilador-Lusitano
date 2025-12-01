"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    COMPILADOR LUSITANO - ANALISADOR SINTÁTICO                 ║
║                                                                               ║
║  Parser que constrói a Árvore Sintática Abstrata (AST)                        ║
║  Utiliza a técnica de Descida Recursiva (Recursive Descent)                   ║
╚═══════════════════════════════════════════════════════════════════════════════╝

O Parser (Analisador Sintático) é responsável por:
- Verificar se a sequência de tokens segue a gramática da linguagem
- Construir a AST (Abstract Syntax Tree)
- Reportar erros sintáticos com mensagens claras
"""

from dataclasses import dataclass, field
from typing import List, Optional, Any, Union
from abc import ABC, abstractmethod
from lexer import Token, TipoToken, Scanner, ErroLexico



# NODOS DA AST (ABSTRACT SYNTAX TREE)
# ═══════════════════════════════════════════════════════════════════════════════

class NoAST(ABC):
    """Classe base abstrata para todos os nós da AST."""
    
    @abstractmethod
    def aceitar(self, visitante: 'VisitanteAST') -> Any:
        """Método para o padrão Visitor."""
        pass
    
    @abstractmethod
    def para_dict(self) -> dict:
        """Converte o nó para dicionário (para visualização)."""
        pass



# NÓS DE EXPRESSÕES
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ExpressaoLiteral(NoAST):
    """Representa um valor literal (número, string, booleano)."""
    valor: Any
    tipo: str  # 'inteiro', 'real', 'texto', 'logico'
    token: Token
    
    def aceitar(self, visitante: 'VisitanteAST') -> Any:
        return visitante.visitar_literal(self)
    
    def para_dict(self) -> dict:
        return {"tipo": "Literal", "valor": self.valor, "tipo_dado": self.tipo}


@dataclass
class ExpressaoVariavel(NoAST):
    """Representa o acesso a uma variável."""
    nome: str
    token: Token
    
    def aceitar(self, visitante: 'VisitanteAST') -> Any:
        return visitante.visitar_variavel(self)
    
    def para_dict(self) -> dict:
        return {"tipo": "Variavel", "nome": self.nome}


@dataclass
class ExpressaoBinaria(NoAST):
    """Representa uma operação binária (a + b, x > y, etc.)."""
    esquerda: NoAST
    operador: Token
    direita: NoAST
    
    def aceitar(self, visitante: 'VisitanteAST') -> Any:
        return visitante.visitar_binaria(self)
    
    def para_dict(self) -> dict:
        return {
            "tipo": "Binaria",
            "operador": self.operador.lexema,
            "esquerda": self.esquerda.para_dict(),
            "direita": self.direita.para_dict()
        }


@dataclass
class ExpressaoUnaria(NoAST):
    """Representa uma operação unária (-x, nao condicao)."""
    operador: Token
    operando: NoAST
    
    def aceitar(self, visitante: 'VisitanteAST') -> Any:
        return visitante.visitar_unaria(self)
    
    def para_dict(self) -> dict:
        return {
            "tipo": "Unaria",
            "operador": self.operador.lexema,
            "operando": self.operando.para_dict()
        }


@dataclass
class ExpressaoAgrupamento(NoAST):
    """Representa uma expressão entre parênteses."""
    expressao: NoAST
    
    def aceitar(self, visitante: 'VisitanteAST') -> Any:
        return visitante.visitar_agrupamento(self)
    
    def para_dict(self) -> dict:
        return {"tipo": "Agrupamento", "expressao": self.expressao.para_dict()}


@dataclass
class ExpressaoAtribuicao(NoAST):
    """Representa uma atribuição (x = 10)."""
    nome: str
    token_nome: Token
    valor: NoAST
    
    def aceitar(self, visitante: 'VisitanteAST') -> Any:
        return visitante.visitar_atribuicao(self)
    
    def para_dict(self) -> dict:
        return {
            "tipo": "Atribuicao",
            "variavel": self.nome,
            "valor": self.valor.para_dict()
        }


@dataclass
class ExpressaoLogica(NoAST):
    """Representa uma operação lógica (e, ou)."""
    esquerda: NoAST
    operador: Token
    direita: NoAST
    
    def aceitar(self, visitante: 'VisitanteAST') -> Any:
        return visitante.visitar_logica(self)
    
    def para_dict(self) -> dict:
        return {
            "tipo": "Logica",
            "operador": self.operador.lexema,
            "esquerda": self.esquerda.para_dict(),
            "direita": self.direita.para_dict()
        }


@dataclass
class ExpressaoChamadaFuncao(NoAST):
    """Representa uma chamada de função."""
    nome: str
    token_nome: Token
    argumentos: List[NoAST]
    
    def aceitar(self, visitante: 'VisitanteAST') -> Any:
        return visitante.visitar_chamada_funcao(self)
    
    def para_dict(self) -> dict:
        return {
            "tipo": "ChamadaFuncao",
            "nome": self.nome,
            "argumentos": [arg.para_dict() for arg in self.argumentos]
        }


@dataclass
class ExpressaoAcessoArray(NoAST):
    """Representa acesso a elemento de array (arr[i])."""
    objeto: NoAST
    indice: NoAST
    token_colchete: Token
    
    def aceitar(self, visitante: 'VisitanteAST') -> Any:
        return visitante.visitar_acesso_array(self)
    
    def para_dict(self) -> dict:
        return {
            "tipo": "AcessoArray",
            "objeto": self.objeto.para_dict(),
            "indice": self.indice.para_dict()
        }



# NÓS DE DECLARAÇÕES/STATEMENTS
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class DeclaracaoExpressao(NoAST):
    """Uma expressão usada como declaração."""
    expressao: NoAST
    
    def aceitar(self, visitante: 'VisitanteAST') -> Any:
        return visitante.visitar_declaracao_expressao(self)
    
    def para_dict(self) -> dict:
        return {"tipo": "DeclaracaoExpressao", "expressao": self.expressao.para_dict()}


@dataclass
class DeclaracaoVariavel(NoAST):
    """Declaração de variável (var x: inteiro = 10)."""
    nome: str
    token_nome: Token
    tipo_dado: Optional[str]  # 'inteiro', 'real', 'texto', 'logico'
    inicializador: Optional[NoAST]
    constante: bool = False
    
    def aceitar(self, visitante: 'VisitanteAST') -> Any:
        return visitante.visitar_declaracao_variavel(self)
    
    def para_dict(self) -> dict:
        d = {
            "tipo": "DeclaracaoVariavel",
            "nome": self.nome,
            "tipo_dado": self.tipo_dado,
            "constante": self.constante
        }
        if self.inicializador:
            d["inicializador"] = self.inicializador.para_dict()
        return d


@dataclass
class DeclaracaoBloco(NoAST):
    """Um bloco de declarações { ... }."""
    declaracoes: List[NoAST]
    
    def aceitar(self, visitante: 'VisitanteAST') -> Any:
        return visitante.visitar_bloco(self)
    
    def para_dict(self) -> dict:
        return {
            "tipo": "Bloco",
            "declaracoes": [d.para_dict() for d in self.declaracoes]
        }


@dataclass
class DeclaracaoSe(NoAST):
    """Declaração se/senao (if/else)."""
    condicao: NoAST
    bloco_verdadeiro: NoAST
    bloco_falso: Optional[NoAST] = None
    
    def aceitar(self, visitante: 'VisitanteAST') -> Any:
        return visitante.visitar_se(self)
    
    def para_dict(self) -> dict:
        d = {
            "tipo": "Se",
            "condicao": self.condicao.para_dict(),
            "entao": self.bloco_verdadeiro.para_dict()
        }
        if self.bloco_falso:
            d["senao"] = self.bloco_falso.para_dict()
        return d


@dataclass
class DeclaracaoEnquanto(NoAST):
    """Declaração enquanto (while)."""
    condicao: NoAST
    corpo: NoAST
    
    def aceitar(self, visitante: 'VisitanteAST') -> Any:
        return visitante.visitar_enquanto(self)
    
    def para_dict(self) -> dict:
        return {
            "tipo": "Enquanto",
            "condicao": self.condicao.para_dict(),
            "corpo": self.corpo.para_dict()
        }


@dataclass
class DeclaracaoPara(NoAST):
    """Declaração para (for) - para i de 1 ate 10."""
    variavel: str
    token_variavel: Token
    inicio: NoAST
    fim: NoAST
    passo: Optional[NoAST]
    corpo: NoAST
    
    def aceitar(self, visitante: 'VisitanteAST') -> Any:
        return visitante.visitar_para(self)
    
    def para_dict(self) -> dict:
        d = {
            "tipo": "Para",
            "variavel": self.variavel,
            "de": self.inicio.para_dict(),
            "ate": self.fim.para_dict(),
            "corpo": self.corpo.para_dict()
        }
        if self.passo:
            d["passo"] = self.passo.para_dict()
        return d


@dataclass
class DeclaracaoFuncao(NoAST):
    """Declaração de função."""
    nome: str
    token_nome: Token
    parametros: List[tuple]  # [(nome, tipo), ...]
    tipo_retorno: Optional[str]
    corpo: 'DeclaracaoBloco'
    
    def aceitar(self, visitante: 'VisitanteAST') -> Any:
        return visitante.visitar_funcao(self)
    
    def para_dict(self) -> dict:
        return {
            "tipo": "Funcao",
            "nome": self.nome,
            "parametros": [{"nome": p[0], "tipo": p[1]} for p in self.parametros],
            "tipo_retorno": self.tipo_retorno,
            "corpo": self.corpo.para_dict()
        }


@dataclass
class DeclaracaoRetorna(NoAST):
    """Declaração retorna (return)."""
    token: Token
    valor: Optional[NoAST]
    
    def aceitar(self, visitante: 'VisitanteAST') -> Any:
        return visitante.visitar_retorna(self)
    
    def para_dict(self) -> dict:
        d = {"tipo": "Retorna"}
        if self.valor:
            d["valor"] = self.valor.para_dict()
        return d


@dataclass
class DeclaracaoEscreva(NoAST):
    """Declaração escreva (print)."""
    expressoes: List[NoAST]
    
    def aceitar(self, visitante: 'VisitanteAST') -> Any:
        return visitante.visitar_escreva(self)
    
    def para_dict(self) -> dict:
        return {
            "tipo": "Escreva",
            "expressoes": [e.para_dict() for e in self.expressoes]
        }


@dataclass
class DeclaracaoLeia(NoAST):
    """Declaração leia (input)."""
    variavel: str
    token_variavel: Token
    mensagem: Optional[NoAST] = None
    
    def aceitar(self, visitante: 'VisitanteAST') -> Any:
        return visitante.visitar_leia(self)
    
    def para_dict(self) -> dict:
        d = {"tipo": "Leia", "variavel": self.variavel}
        if self.mensagem:
            d["mensagem"] = self.mensagem.para_dict()
        return d


@dataclass
class Programa(NoAST):
    """Nó raiz representando o programa inteiro."""
    declaracoes: List[NoAST]
    
    def aceitar(self, visitante: 'VisitanteAST') -> Any:
        return visitante.visitar_programa(self)
    
    def para_dict(self) -> dict:
        return {
            "tipo": "Programa",
            "declaracoes": [d.para_dict() for d in self.declaracoes]
        }



# PADRÃO VISITOR PARA A AST
# ═══════════════════════════════════════════════════════════════════════════════

class VisitanteAST(ABC):
    """Interface Visitor para percorrer a AST."""
    
    @abstractmethod
    def visitar_literal(self, no: ExpressaoLiteral) -> Any: pass
    @abstractmethod
    def visitar_variavel(self, no: ExpressaoVariavel) -> Any: pass
    @abstractmethod
    def visitar_binaria(self, no: ExpressaoBinaria) -> Any: pass
    @abstractmethod
    def visitar_unaria(self, no: ExpressaoUnaria) -> Any: pass
    @abstractmethod
    def visitar_agrupamento(self, no: ExpressaoAgrupamento) -> Any: pass
    @abstractmethod
    def visitar_atribuicao(self, no: ExpressaoAtribuicao) -> Any: pass
    @abstractmethod
    def visitar_logica(self, no: ExpressaoLogica) -> Any: pass
    @abstractmethod
    def visitar_chamada_funcao(self, no: ExpressaoChamadaFuncao) -> Any: pass
    @abstractmethod
    def visitar_acesso_array(self, no: ExpressaoAcessoArray) -> Any: pass
    @abstractmethod
    def visitar_declaracao_expressao(self, no: DeclaracaoExpressao) -> Any: pass
    @abstractmethod
    def visitar_declaracao_variavel(self, no: DeclaracaoVariavel) -> Any: pass
    @abstractmethod
    def visitar_bloco(self, no: DeclaracaoBloco) -> Any: pass
    @abstractmethod
    def visitar_se(self, no: DeclaracaoSe) -> Any: pass
    @abstractmethod
    def visitar_enquanto(self, no: DeclaracaoEnquanto) -> Any: pass
    @abstractmethod
    def visitar_para(self, no: DeclaracaoPara) -> Any: pass
    @abstractmethod
    def visitar_funcao(self, no: DeclaracaoFuncao) -> Any: pass
    @abstractmethod
    def visitar_retorna(self, no: DeclaracaoRetorna) -> Any: pass
    @abstractmethod
    def visitar_escreva(self, no: DeclaracaoEscreva) -> Any: pass
    @abstractmethod
    def visitar_leia(self, no: DeclaracaoLeia) -> Any: pass
    @abstractmethod
    def visitar_programa(self, no: Programa) -> Any: pass



# ERROS SINTÁTICOS
# ═══════════════════════════════════════════════════════════════════════════════

class ErroSintatico(Exception):
    """Exceção para erros encontrados durante a análise sintática."""
    
    def __init__(self, mensagem: str, token: Token):
        self.mensagem = mensagem
        self.token = token
        super().__init__(self.formatar_erro())
    
    def formatar_erro(self) -> str:
        erro = f"\n╔══════════════════════════════════════════════════════════════╗\n"
        erro += f"║  ERRO SINTÁTICO na linha {self.token.linha}, coluna {self.token.coluna}\n"
        erro += f"╠══════════════════════════════════════════════════════════════╣\n"
        erro += f"║  {self.mensagem}\n"
        erro += f"║  Token encontrado: {self.token.tipo.name} ('{self.token.lexema}')\n"
        erro += f"╚══════════════════════════════════════════════════════════════╝"
        return erro



# ANALISADOR SINTÁTICO (PARSER)
# ═══════════════════════════════════════════════════════════════════════════════

class Parser:
    """
    Analisador Sintático usando Descida Recursiva.
    
    Implementa a gramática da linguagem Lusitano e constrói a AST.
    
    Gramática (simplificada):
    ─────────────────────────────────────────────────────────────────
    programa       → declaracao* EOF
    declaracao     → declaracao_var | declaracao_func | statement
    declaracao_var → "var" IDENTIFICADOR ":" tipo ("=" expressao)?
    declaracao_func→ "funcao" IDENTIFICADOR "(" parametros? ")" (":" tipo)? bloco
    
    statement      → escreva_stmt | leia_stmt | se_stmt | enquanto_stmt 
                   | para_stmt | retorna_stmt | bloco | expressao_stmt
    
    expressao      → atribuicao
    atribuicao     → IDENTIFICADOR "=" atribuicao | logico_ou
    logico_ou      → logico_e ("ou" logico_e)*
    logico_e       → igualdade ("e" igualdade)*
    igualdade      → comparacao (("==" | "!=") comparacao)*
    comparacao     → termo (("<" | ">" | "<=" | ">=") termo)*
    termo          → fator (("+" | "-") fator)*
    fator          → unario (("*" | "/" | "%") unario)*
    unario         → ("nao" | "-") unario | chamada
    chamada        → primario ("(" argumentos? ")" | "[" expressao "]")*
    primario       → NUMERO | TEXTO | "verdadeiro" | "falso" 
                   | IDENTIFICADOR | "(" expressao ")"
    """
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.atual = 0
    
    
    # MÉTODOS AUXILIARES
    # ─────────────────────────────────────────────────────────────────────────
    
    def token_atual(self) -> Token:
        """Retorna o token atual."""
        return self.tokens[self.atual]
    
    def token_anterior(self) -> Token:
        """Retorna o token anterior."""
        return self.tokens[self.atual - 1]
    
    def fim_tokens(self) -> bool:
        """Verifica se chegamos ao fim dos tokens."""
        return self.token_atual().tipo == TipoToken.FIM_ARQUIVO
    
    def avancar(self) -> Token:
        """Avança para o próximo token e retorna o anterior."""
        if not self.fim_tokens():
            self.atual += 1
        return self.token_anterior()
    
    def verificar(self, tipo: TipoToken) -> bool:
        """Verifica se o token atual é do tipo especificado."""
        if self.fim_tokens():
            return False
        return self.token_atual().tipo == tipo
    
    def combinar(self, *tipos: TipoToken) -> bool:
        """Verifica e consome se o token atual é um dos tipos."""
        for tipo in tipos:
            if self.verificar(tipo):
                self.avancar()
                return True
        return False
    
    def consumir(self, tipo: TipoToken, mensagem: str) -> Token:
        """Consome o token atual se for do tipo esperado, ou lança erro."""
        if self.verificar(tipo):
            return self.avancar()
        raise ErroSintatico(mensagem, self.token_atual())
    
    def sincronizar(self):
        """Recupera de erro avançando até um ponto seguro."""
        self.avancar()
        
        while not self.fim_tokens():
            if self.token_anterior().tipo == TipoToken.PONTO_VIRGULA:
                return
            
            if self.token_atual().tipo in (
                TipoToken.FUNCAO, TipoToken.VAR, TipoToken.CONST,
                TipoToken.SE, TipoToken.ENQUANTO, TipoToken.PARA,
                TipoToken.RETORNA, TipoToken.ESCREVA
            ):
                return
            
            self.avancar()
    
    
    # REGRAS DA GRAMÁTICA - DECLARAÇÕES
    # ─────────────────────────────────────────────────────────────────────────
    
    def analisar(self) -> Programa:
        """Ponto de entrada do parser - analisa o programa completo."""
        print("╔═══════════════════════════════════════════════════════════════╗")
        print("║            INICIANDO ANÁLISE SINTÁTICA (PARSER)               ║")
        print("╚═══════════════════════════════════════════════════════════════╝")
        
        declaracoes = []
        
        while not self.fim_tokens():
            try:
                decl = self.declaracao()
                if decl:
                    declaracoes.append(decl)
            except ErroSintatico as e:
                print(e)
                self.sincronizar()
        
        print(f"✓ Análise sintática concluída: {len(declaracoes)} declarações\n")
        return Programa(declaracoes)
    
    def declaracao(self) -> Optional[NoAST]:
        """Analisa uma declaração de nível superior."""
        try:
            if self.combinar(TipoToken.FUNCAO):
                return self.declaracao_funcao()
            if self.combinar(TipoToken.VAR):
                return self.declaracao_variavel(constante=False)
            if self.combinar(TipoToken.CONST):
                return self.declaracao_variavel(constante=True)
            return self.statement()
        except ErroSintatico:
            self.sincronizar()
            return None
    
    def declaracao_funcao(self) -> DeclaracaoFuncao:
        """Analisa uma declaração de função."""
        token_nome = self.consumir(TipoToken.IDENTIFICADOR, "Esperado nome da função")
        nome = token_nome.lexema
        
        self.consumir(TipoToken.ABRE_PAREN, "Esperado '(' após nome da função")
        
        parametros = []
        if not self.verificar(TipoToken.FECHA_PAREN):
            while True:
                param_nome = self.consumir(TipoToken.IDENTIFICADOR, "Esperado nome do parâmetro")
                self.consumir(TipoToken.DOIS_PONTOS, "Esperado ':' após nome do parâmetro")
                param_tipo = self.tipo_dado()
                parametros.append((param_nome.lexema, param_tipo))
                
                if not self.combinar(TipoToken.VIRGULA):
                    break
        
        self.consumir(TipoToken.FECHA_PAREN, "Esperado ')' após parâmetros")
        
        # Tipo de retorno opcional
        tipo_retorno = None
        if self.combinar(TipoToken.DOIS_PONTOS):
            tipo_retorno = self.tipo_dado()
        
        # Corpo da função
        self.consumir(TipoToken.ABRE_CHAVE, "Esperado '{' antes do corpo da função")
        corpo = self.bloco()
        
        return DeclaracaoFuncao(nome, token_nome, parametros, tipo_retorno, corpo)
    
    def declaracao_variavel(self, constante: bool = False) -> DeclaracaoVariavel:
        """Analisa uma declaração de variável."""
        token_nome = self.consumir(TipoToken.IDENTIFICADOR, "Esperado nome da variável")
        nome = token_nome.lexema
        
        # Tipo opcional
        tipo_dado = None
        if self.combinar(TipoToken.DOIS_PONTOS):
            tipo_dado = self.tipo_dado()
        
        # Inicializador opcional
        inicializador = None
        if self.combinar(TipoToken.ATRIBUICAO):
            inicializador = self.expressao()
        
        # Ponto e vírgula é opcional na nossa linguagem
        self.combinar(TipoToken.PONTO_VIRGULA)
        
        return DeclaracaoVariavel(nome, token_nome, tipo_dado, inicializador, constante)
    
    def tipo_dado(self) -> str:
        """Analisa um tipo de dado."""
        if self.combinar(TipoToken.TIPO_INTEIRO):
            return "inteiro"
        if self.combinar(TipoToken.TIPO_REAL):
            return "real"
        if self.combinar(TipoToken.TIPO_TEXTO):
            return "texto"
        if self.combinar(TipoToken.TIPO_LOGICO):
            return "logico"
        if self.combinar(TipoToken.TIPO_VAZIO):
            return "vazio"
        
        raise ErroSintatico("Esperado tipo de dado", self.token_atual())
    
    
    # REGRAS DA GRAMÁTICA - STATEMENTS
    # ─────────────────────────────────────────────────────────────────────────
    
    def statement(self) -> NoAST:
        """Analisa um statement."""
        if self.combinar(TipoToken.SE):
            return self.statement_se()
        if self.combinar(TipoToken.ENQUANTO):
            return self.statement_enquanto()
        if self.combinar(TipoToken.PARA):
            return self.statement_para()
        if self.combinar(TipoToken.ESCREVA):
            return self.statement_escreva()
        if self.combinar(TipoToken.LEIA):
            return self.statement_leia()
        if self.combinar(TipoToken.RETORNA):
            return self.statement_retorna()
        if self.combinar(TipoToken.ABRE_CHAVE):
            return self.bloco()
        
        return self.statement_expressao()
    
    def statement_se(self) -> DeclaracaoSe:
        """Analisa um statement se/senao."""
        self.consumir(TipoToken.ABRE_PAREN, "Esperado '(' após 'se'")
        condicao = self.expressao()
        self.consumir(TipoToken.FECHA_PAREN, "Esperado ')' após condição")
        
        bloco_verdadeiro = self.statement()
        
        bloco_falso = None
        if self.combinar(TipoToken.SENAO):
            bloco_falso = self.statement()
        elif self.combinar(TipoToken.SENAOSE):
            # senaose é tratado como senao + se
            bloco_falso = self.statement_se()
        
        return DeclaracaoSe(condicao, bloco_verdadeiro, bloco_falso)
    
    def statement_enquanto(self) -> DeclaracaoEnquanto:
        """Analisa um statement enquanto."""
        self.consumir(TipoToken.ABRE_PAREN, "Esperado '(' após 'enquanto'")
        condicao = self.expressao()
        self.consumir(TipoToken.FECHA_PAREN, "Esperado ')' após condição")
        
        corpo = self.statement()
        
        return DeclaracaoEnquanto(condicao, corpo)
    
    def statement_para(self) -> DeclaracaoPara:
        """Analisa um statement para (for)."""
        token_var = self.consumir(TipoToken.IDENTIFICADOR, "Esperado variável após 'para'")
        variavel = token_var.lexema
        
        self.consumir(TipoToken.DE, "Esperado 'de' após variável")
        inicio = self.expressao()
        
        self.consumir(TipoToken.ATE, "Esperado 'ate' após valor inicial")
        fim = self.expressao()
        
        passo = None
        if self.combinar(TipoToken.PASSO):
            passo = self.expressao()
        
        corpo = self.statement()
        
        return DeclaracaoPara(variavel, token_var, inicio, fim, passo, corpo)
    
    def statement_escreva(self) -> DeclaracaoEscreva:
        """Analisa um statement escreva."""
        self.consumir(TipoToken.ABRE_PAREN, "Esperado '(' após 'escreva'")
        
        expressoes = []
        if not self.verificar(TipoToken.FECHA_PAREN):
            expressoes.append(self.expressao())
            while self.combinar(TipoToken.VIRGULA):
                expressoes.append(self.expressao())
        
        self.consumir(TipoToken.FECHA_PAREN, "Esperado ')' após argumentos")
        self.combinar(TipoToken.PONTO_VIRGULA)
        
        return DeclaracaoEscreva(expressoes)
    
    def statement_leia(self) -> DeclaracaoLeia:
        """Analisa um statement leia."""
        self.consumir(TipoToken.ABRE_PAREN, "Esperado '(' após 'leia'")
        
        mensagem = None
        if self.verificar(TipoToken.TEXTO):
            mensagem = self.expressao()
            self.consumir(TipoToken.VIRGULA, "Esperado ',' após mensagem")
        
        token_var = self.consumir(TipoToken.IDENTIFICADOR, "Esperado variável para leitura")
        
        self.consumir(TipoToken.FECHA_PAREN, "Esperado ')' após variável")
        self.combinar(TipoToken.PONTO_VIRGULA)
        
        return DeclaracaoLeia(token_var.lexema, token_var, mensagem)
    
    def statement_retorna(self) -> DeclaracaoRetorna:
        """Analisa um statement retorna."""
        token = self.token_anterior()
        
        valor = None
        if not self.verificar(TipoToken.PONTO_VIRGULA) and not self.verificar(TipoToken.FECHA_CHAVE):
            valor = self.expressao()
        
        self.combinar(TipoToken.PONTO_VIRGULA)
        
        return DeclaracaoRetorna(token, valor)
    
    def bloco(self) -> DeclaracaoBloco:
        """Analisa um bloco de declarações."""
        declaracoes = []
        
        while not self.verificar(TipoToken.FECHA_CHAVE) and not self.fim_tokens():
            decl = self.declaracao()
            if decl:
                declaracoes.append(decl)
        
        self.consumir(TipoToken.FECHA_CHAVE, "Esperado '}' após bloco")
        
        return DeclaracaoBloco(declaracoes)
    
    def statement_expressao(self) -> DeclaracaoExpressao:
        """Analisa uma expressão como statement."""
        expr = self.expressao()
        self.combinar(TipoToken.PONTO_VIRGULA)
        return DeclaracaoExpressao(expr)
    
    
    # REGRAS DA GRAMÁTICA - EXPRESSÕES
    # ─────────────────────────────────────────────────────────────────────────
    
    def expressao(self) -> NoAST:
        """Analisa uma expressão."""
        return self.atribuicao()
    
    def atribuicao(self) -> NoAST:
        """Analisa uma atribuição."""
        expr = self.logico_ou()
        
        if self.combinar(TipoToken.ATRIBUICAO, TipoToken.MAIS_IGUAL, 
                         TipoToken.MENOS_IGUAL, TipoToken.MULT_IGUAL, TipoToken.DIV_IGUAL):
            operador = self.token_anterior()
            valor = self.atribuicao()
            
            if isinstance(expr, ExpressaoVariavel):
                nome = expr.nome
                
                # Para operadores compostos, criamos a expressão apropriada
                if operador.tipo != TipoToken.ATRIBUICAO:
                    # x += 5 vira x = x + 5
                    op_map = {
                        TipoToken.MAIS_IGUAL: TipoToken.MAIS,
                        TipoToken.MENOS_IGUAL: TipoToken.MENOS,
                        TipoToken.MULT_IGUAL: TipoToken.MULTIPLICA,
                        TipoToken.DIV_IGUAL: TipoToken.DIVIDE
                    }
                    op_token = Token(op_map[operador.tipo], operador.lexema[0], 
                                    None, operador.linha, operador.coluna)
                    valor = ExpressaoBinaria(expr, op_token, valor)
                
                return ExpressaoAtribuicao(nome, expr.token, valor)
            
            raise ErroSintatico("Alvo de atribuição inválido", operador)
        
        return expr
    
    def logico_ou(self) -> NoAST:
        """Analisa expressão lógica OU."""
        expr = self.logico_e()
        
        while self.combinar(TipoToken.OU):
            operador = self.token_anterior()
            direita = self.logico_e()
            expr = ExpressaoLogica(expr, operador, direita)
        
        return expr
    
    def logico_e(self) -> NoAST:
        """Analisa expressão lógica E."""
        expr = self.igualdade()
        
        while self.combinar(TipoToken.E):
            operador = self.token_anterior()
            direita = self.igualdade()
            expr = ExpressaoLogica(expr, operador, direita)
        
        return expr
    
    def igualdade(self) -> NoAST:
        """Analisa expressão de igualdade."""
        expr = self.comparacao()
        
        while self.combinar(TipoToken.IGUAL, TipoToken.DIFERENTE):
            operador = self.token_anterior()
            direita = self.comparacao()
            expr = ExpressaoBinaria(expr, operador, direita)
        
        return expr
    
    def comparacao(self) -> NoAST:
        """Analisa expressão de comparação."""
        expr = self.termo()
        
        while self.combinar(TipoToken.MENOR, TipoToken.MENOR_IGUAL, 
                            TipoToken.MAIOR, TipoToken.MAIOR_IGUAL):
            operador = self.token_anterior()
            direita = self.termo()
            expr = ExpressaoBinaria(expr, operador, direita)
        
        return expr
    
    def termo(self) -> NoAST:
        """Analisa termo (adição, subtração)."""
        expr = self.fator()
        
        while self.combinar(TipoToken.MAIS, TipoToken.MENOS):
            operador = self.token_anterior()
            direita = self.fator()
            expr = ExpressaoBinaria(expr, operador, direita)
        
        return expr
    
    def fator(self) -> NoAST:
        """Analisa fator (multiplicação, divisão)."""
        expr = self.potencia()
        
        while self.combinar(TipoToken.MULTIPLICA, TipoToken.DIVIDE, TipoToken.MODULO):
            operador = self.token_anterior()
            direita = self.potencia()
            expr = ExpressaoBinaria(expr, operador, direita)
        
        return expr
    
    def potencia(self) -> NoAST:
        """Analisa potência (associativa à direita)."""
        expr = self.unario()
        
        if self.combinar(TipoToken.POTENCIA):
            operador = self.token_anterior()
            direita = self.potencia()  # Recursão à direita
            expr = ExpressaoBinaria(expr, operador, direita)
        
        return expr
    
    def unario(self) -> NoAST:
        """Analisa expressão unária."""
        if self.combinar(TipoToken.NAO, TipoToken.MENOS):
            operador = self.token_anterior()
            operando = self.unario()
            return ExpressaoUnaria(operador, operando)
        
        return self.chamada()
    
    def chamada(self) -> NoAST:
        """Analisa chamada de função ou acesso a array."""
        expr = self.primario()
        
        while True:
            if self.combinar(TipoToken.ABRE_PAREN):
                expr = self.finalizar_chamada(expr)
            elif self.combinar(TipoToken.ABRE_COLCHETE):
                token = self.token_anterior()
                indice = self.expressao()
                self.consumir(TipoToken.FECHA_COLCHETE, "Esperado ']' após índice")
                expr = ExpressaoAcessoArray(expr, indice, token)
            else:
                break
        
        return expr
    
    def finalizar_chamada(self, chamado: NoAST) -> ExpressaoChamadaFuncao:
        """Finaliza uma chamada de função."""
        argumentos = []
        
        if not self.verificar(TipoToken.FECHA_PAREN):
            argumentos.append(self.expressao())
            while self.combinar(TipoToken.VIRGULA):
                if len(argumentos) >= 255:
                    raise ErroSintatico("Não é possível ter mais de 255 argumentos", 
                                       self.token_atual())
                argumentos.append(self.expressao())
        
        self.consumir(TipoToken.FECHA_PAREN, "Esperado ')' após argumentos")
        
        if isinstance(chamado, ExpressaoVariavel):
            return ExpressaoChamadaFuncao(chamado.nome, chamado.token, argumentos)
        
        raise ErroSintatico("Expressão não é chamável", self.token_atual())
    
    def primario(self) -> NoAST:
        """Analisa expressão primária."""
        # Literais
        if self.combinar(TipoToken.VERDADEIRO):
            return ExpressaoLiteral(True, "logico", self.token_anterior())
        
        if self.combinar(TipoToken.FALSO):
            return ExpressaoLiteral(False, "logico", self.token_anterior())
        
        if self.combinar(TipoToken.NUMERO_INTEIRO):
            token = self.token_anterior()
            return ExpressaoLiteral(token.valor, "inteiro", token)
        
        if self.combinar(TipoToken.NUMERO_REAL):
            token = self.token_anterior()
            return ExpressaoLiteral(token.valor, "real", token)
        
        if self.combinar(TipoToken.TEXTO):
            token = self.token_anterior()
            return ExpressaoLiteral(token.valor, "texto", token)
        
        # Identificador
        if self.combinar(TipoToken.IDENTIFICADOR):
            return ExpressaoVariavel(self.token_anterior().lexema, self.token_anterior())
        
        # Agrupamento
        if self.combinar(TipoToken.ABRE_PAREN):
            expr = self.expressao()
            self.consumir(TipoToken.FECHA_PAREN, "Esperado ')' após expressão")
            return ExpressaoAgrupamento(expr)
        
        raise ErroSintatico("Esperado expressão", self.token_atual())



# VISUALIZADOR DA AST
# ═══════════════════════════════════════════════════════════════════════════════

class VisualizadorAST(VisitanteAST):
    """Gera uma visualização em texto da AST."""
    
    def __init__(self):
        self.indent = 0
    
    def _indentar(self) -> str:
        return "│   " * self.indent
    
    def _prefixo(self, ultimo: bool = False) -> str:
        return self._indentar() + ("└── " if ultimo else "├── ")
    
    def visualizar(self, no: NoAST) -> str:
        """Gera visualização da AST."""
        return no.aceitar(self)
    
    # Implementação de todos os métodos do Visitor (simplificado)
    def visitar_programa(self, no: Programa) -> str:
        linhas = ["📄 Programa"]
        for i, decl in enumerate(no.declaracoes):
            ultimo = i == len(no.declaracoes) - 1
            self.indent = 0
            linhas.append(self._prefixo(ultimo) + decl.aceitar(self))
        return "\n".join(linhas)
    
    def visitar_literal(self, no: ExpressaoLiteral) -> str:
        return f"📌 Literal: {repr(no.valor)} ({no.tipo})"
    
    def visitar_variavel(self, no: ExpressaoVariavel) -> str:
        return f"🔤 Variável: {no.nome}"
    
    def visitar_binaria(self, no: ExpressaoBinaria) -> str:
        self.indent += 1
        esq = self._prefixo() + no.esquerda.aceitar(self)
        dir = self._prefixo(True) + no.direita.aceitar(self)
        self.indent -= 1
        return f"➕ Binária: '{no.operador.lexema}'\n{esq}\n{dir}"
    
    def visitar_unaria(self, no: ExpressaoUnaria) -> str:
        self.indent += 1
        operando = self._prefixo(True) + no.operando.aceitar(self)
        self.indent -= 1
        return f"➖ Unária: '{no.operador.lexema}'\n{operando}"
    
    def visitar_agrupamento(self, no: ExpressaoAgrupamento) -> str:
        return f"🔲 ({no.expressao.aceitar(self)})"
    
    def visitar_atribuicao(self, no: ExpressaoAtribuicao) -> str:
        self.indent += 1
        valor = self._prefixo(True) + no.valor.aceitar(self)
        self.indent -= 1
        return f"📝 Atribuição: {no.nome} =\n{valor}"
    
    def visitar_logica(self, no: ExpressaoLogica) -> str:
        self.indent += 1
        esq = self._prefixo() + no.esquerda.aceitar(self)
        dir = self._prefixo(True) + no.direita.aceitar(self)
        self.indent -= 1
        return f"🔀 Lógica: '{no.operador.lexema}'\n{esq}\n{dir}"
    
    def visitar_chamada_funcao(self, no: ExpressaoChamadaFuncao) -> str:
        self.indent += 1
        args = []
        for i, arg in enumerate(no.argumentos):
            ultimo = i == len(no.argumentos) - 1
            args.append(self._prefixo(ultimo) + arg.aceitar(self))
        self.indent -= 1
        args_str = "\n".join(args) if args else ""
        return f"📞 Chamada: {no.nome}()\n{args_str}"
    
    def visitar_acesso_array(self, no: ExpressaoAcessoArray) -> str:
        return f"📊 Array[{no.indice.aceitar(self)}]"
    
    def visitar_declaracao_expressao(self, no: DeclaracaoExpressao) -> str:
        return f"💭 Expressão: {no.expressao.aceitar(self)}"
    
    def visitar_declaracao_variavel(self, no: DeclaracaoVariavel) -> str:
        tipo = no.tipo_dado or "inferido"
        const = " (constante)" if no.constante else ""
        if no.inicializador:
            self.indent += 1
            init = self._prefixo(True) + no.inicializador.aceitar(self)
            self.indent -= 1
            return f"📦 Var: {no.nome}: {tipo}{const}\n{init}"
        return f"📦 Var: {no.nome}: {tipo}{const}"
    
    def visitar_bloco(self, no: DeclaracaoBloco) -> str:
        self.indent += 1
        decls = []
        for i, d in enumerate(no.declaracoes):
            ultimo = i == len(no.declaracoes) - 1
            decls.append(self._prefixo(ultimo) + d.aceitar(self))
        self.indent -= 1
        return "📁 Bloco:\n" + "\n".join(decls)
    
    def visitar_se(self, no: DeclaracaoSe) -> str:
        self.indent += 1
        cond = self._prefixo() + "Condição: " + no.condicao.aceitar(self)
        entao = self._prefixo(not no.bloco_falso) + "Então: " + no.bloco_verdadeiro.aceitar(self)
        senao = ""
        if no.bloco_falso:
            senao = "\n" + self._prefixo(True) + "Senão: " + no.bloco_falso.aceitar(self)
        self.indent -= 1
        return f"🔀 Se:\n{cond}\n{entao}{senao}"
    
    def visitar_enquanto(self, no: DeclaracaoEnquanto) -> str:
        self.indent += 1
        cond = self._prefixo() + "Condição: " + no.condicao.aceitar(self)
        corpo = self._prefixo(True) + "Corpo: " + no.corpo.aceitar(self)
        self.indent -= 1
        return f"🔄 Enquanto:\n{cond}\n{corpo}"
    
    def visitar_para(self, no: DeclaracaoPara) -> str:
        self.indent += 1
        var = self._prefixo() + f"Variável: {no.variavel}"
        inicio = self._prefixo() + "De: " + no.inicio.aceitar(self)
        fim = self._prefixo() + "Até: " + no.fim.aceitar(self)
        passo = ""
        if no.passo:
            passo = "\n" + self._prefixo() + "Passo: " + no.passo.aceitar(self)
        corpo = self._prefixo(True) + "Corpo: " + no.corpo.aceitar(self)
        self.indent -= 1
        return f"🔁 Para:\n{var}\n{inicio}\n{fim}{passo}\n{corpo}"
    
    def visitar_funcao(self, no: DeclaracaoFuncao) -> str:
        params = ", ".join([f"{p[0]}: {p[1]}" for p in no.parametros])
        retorno = f" → {no.tipo_retorno}" if no.tipo_retorno else ""
        self.indent += 1
        corpo = self._prefixo(True) + no.corpo.aceitar(self)
        self.indent -= 1
        return f"⚡ Função: {no.nome}({params}){retorno}\n{corpo}"
    
    def visitar_retorna(self, no: DeclaracaoRetorna) -> str:
        if no.valor:
            return f"↩️ Retorna: {no.valor.aceitar(self)}"
        return "↩️ Retorna"
    
    def visitar_escreva(self, no: DeclaracaoEscreva) -> str:
        exprs = ", ".join([e.aceitar(self) for e in no.expressoes])
        return f"🖨️ Escreva: {exprs}"
    
    def visitar_leia(self, no: DeclaracaoLeia) -> str:
        msg = f" ('{no.mensagem.aceitar(self)}')" if no.mensagem else ""
        return f"📥 Leia: {no.variavel}{msg}"



# TESTE DO PARSER
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    codigo_teste = '''
// Programa de exemplo em Lusitano
funcao fatorial(n: inteiro): inteiro {
    se (n <= 1) {
        retorna 1
    }
    retorna n * fatorial(n - 1)
}

funcao principal() {
    var nome: texto = "Mundo"
    var idade: inteiro = 25
    
    escreva("Olá, ", nome, "!")
    
    se (idade >= 18) {
        escreva("Maior de idade")
    } senao {
        escreva("Menor de idade")
    }
    
    var soma: inteiro = 0
    para i de 1 ate 10 {
        soma = soma + i
    }
    
    escreva("Soma: ", soma)
    escreva("Fatorial de 5: ", fatorial(5))
    
    retorna 0
}
'''
    
    try:
        # Análise Léxica
        scanner = Scanner(codigo_teste)
        tokens = scanner.escanear()
        
        # Análise Sintática
        parser = Parser(tokens)
        ast = parser.analisar()
        
        # Visualização da AST
        print("\n" + "═" * 70)
        print("                    ÁRVORE SINTÁTICA ABSTRATA (AST)")
        print("═" * 70 + "\n")
        
        visualizador = VisualizadorAST()
        print(visualizador.visualizar(ast))
        
    except (ErroLexico, ErroSintatico) as e:
        print(e)
