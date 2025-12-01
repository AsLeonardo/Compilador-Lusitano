"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    COMPILADOR LUSITANO - ANALISADOR SEMÂNTICO                 ║
║                                                                               ║
║  Verifica a correção semântica do programa:                                   ║
║  - Declaração de variáveis antes do uso                                       ║
║  - Compatibilidade de tipos                                                   ║
║  - Escopo de variáveis                                                        ║
║  - Retorno de funções                                                         ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum, auto
from parser import (
    NoAST, VisitanteAST, Programa, DeclaracaoFuncao, DeclaracaoVariavel,
    DeclaracaoBloco, DeclaracaoSe, DeclaracaoEnquanto, DeclaracaoPara,
    DeclaracaoRetorna, DeclaracaoEscreva, DeclaracaoLeia, DeclaracaoExpressao,
    ExpressaoLiteral, ExpressaoVariavel, ExpressaoBinaria, ExpressaoUnaria,
    ExpressaoAgrupamento, ExpressaoAtribuicao, ExpressaoLogica,
    ExpressaoChamadaFuncao, ExpressaoAcessoArray, Token
)
from lexer import TipoToken, Scanner



# SISTEMA DE TIPOS
# ═══════════════════════════════════════════════════════════════════════════════

class Tipo(Enum):
    """Tipos de dados da linguagem Lusitano."""
    INTEIRO = auto()
    REAL = auto()
    TEXTO = auto()
    LOGICO = auto()
    VAZIO = auto()
    FUNCAO = auto()
    DESCONHECIDO = auto()
    ERRO = auto()
    
    def __str__(self):
        nomes = {
            Tipo.INTEIRO: "inteiro",
            Tipo.REAL: "real",
            Tipo.TEXTO: "texto",
            Tipo.LOGICO: "logico",
            Tipo.VAZIO: "vazio",
            Tipo.FUNCAO: "funcao",
            Tipo.DESCONHECIDO: "desconhecido",
            Tipo.ERRO: "erro"
        }
        return nomes.get(self, self.name)

# Mapeamento de string para Tipo
MAPA_TIPOS = {
    "inteiro": Tipo.INTEIRO,
    "real": Tipo.REAL,
    "texto": Tipo.TEXTO,
    "logico": Tipo.LOGICO,
    "vazio": Tipo.VAZIO,
}



# TABELA DE SÍMBOLOS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Simbolo:
    """Representa um símbolo na tabela de símbolos."""
    nome: str
    tipo: Tipo
    categoria: str  # 'variavel', 'funcao', 'parametro', 'constante'
    escopo: int
    linha: int
    coluna: int
    constante: bool = False
    parametros: List[tuple] = field(default_factory=list)  # Para funções
    tipo_retorno: Optional[Tipo] = None  # Para funções
    inicializado: bool = False
    
    def __repr__(self):
        return f"Simbolo({self.nome}: {self.tipo}, {self.categoria}, escopo={self.escopo})"


class TabelaSimbolos:
    """
    Tabela de símbolos com suporte a escopos aninhados.
    
    Usa uma lista de dicionários onde cada dicionário representa um escopo.
    O escopo 0 é o global.
    """
    
    def __init__(self):
        self.escopos: List[Dict[str, Simbolo]] = [{}]  # Começa com escopo global
        self.escopo_atual = 0
        self.todos_simbolos: List[Simbolo] = []
    
    def entrar_escopo(self):
        """Entra em um novo escopo."""
        self.escopos.append({})
        self.escopo_atual += 1
    
    def sair_escopo(self):
        """Sai do escopo atual."""
        if self.escopo_atual > 0:
            self.escopos.pop()
            self.escopo_atual -= 1
    
    def declarar(self, simbolo: Simbolo) -> bool:
        """
        Declara um símbolo no escopo atual.
        Retorna False se já existe no escopo atual.
        """
        if simbolo.nome in self.escopos[self.escopo_atual]:
            return False
        
        simbolo.escopo = self.escopo_atual
        self.escopos[self.escopo_atual][simbolo.nome] = simbolo
        self.todos_simbolos.append(simbolo)
        return True
    
    def buscar(self, nome: str) -> Optional[Simbolo]:
        """
        Busca um símbolo em todos os escopos, do mais interno para o mais externo.
        """
        for escopo in reversed(self.escopos):
            if nome in escopo:
                return escopo[nome]
        return None
    
    def buscar_local(self, nome: str) -> Optional[Simbolo]:
        """Busca um símbolo apenas no escopo atual."""
        return self.escopos[self.escopo_atual].get(nome)
    
    def imprimir(self):
        """Imprime a tabela de símbolos formatada."""
        print("\n┌─────────────────────────────────────────────────────────────────────────┐")
        print("│                         TABELA DE SÍMBOLOS                              │")
        print("├──────────────────┬────────────┬────────────┬────────┬───────────────────┤")
        print("│ Nome             │ Tipo       │ Categoria  │ Escopo │ Posição           │")
        print("├──────────────────┼────────────┼────────────┼────────┼───────────────────┤")
        
        for simbolo in self.todos_simbolos:
            nome = simbolo.nome[:16]
            tipo = str(simbolo.tipo)[:10]
            cat = simbolo.categoria[:10]
            esc = str(simbolo.escopo)
            pos = f"L{simbolo.linha}:C{simbolo.coluna}"
            
            print(f"│ {nome:<16} │ {tipo:<10} │ {cat:<10} │ {esc:<6} │ {pos:<17} │")
        
        print("└──────────────────┴────────────┴────────────┴────────┴───────────────────┘")



# ERROS SEMÂNTICOS
# ═══════════════════════════════════════════════════════════════════════════════

class ErroSemantico(Exception):
    """Exceção para erros semânticos."""
    
    def __init__(self, mensagem: str, linha: int, coluna: int):
        self.mensagem = mensagem
        self.linha = linha
        self.coluna = coluna
        super().__init__(self.formatar_erro())
    
    def formatar_erro(self) -> str:
        erro = f"\n╔══════════════════════════════════════════════════════════════╗\n"
        erro += f"║  ERRO SEMÂNTICO na linha {self.linha}, coluna {self.coluna}\n"
        erro += f"╠══════════════════════════════════════════════════════════════╣\n"
        erro += f"║  {self.mensagem}\n"
        erro += f"╚══════════════════════════════════════════════════════════════╝"
        return erro


@dataclass
class AvisoSemantico:
    """Representa um aviso (não fatal) durante análise semântica."""
    mensagem: str
    linha: int
    coluna: int
    
    def __str__(self):
        return f"⚠️  Aviso (L{self.linha}:C{self.coluna}): {self.mensagem}"



# ANALISADOR SEMÂNTICO
# ═══════════════════════════════════════════════════════════════════════════════

class AnalisadorSemantico(VisitanteAST):
    """
    Realiza a análise semântica do programa.
    
    Verificações realizadas:
    - Variáveis declaradas antes do uso
    - Variáveis não duplicadas no mesmo escopo
    - Compatibilidade de tipos em operações
    - Tipos de retorno de funções
    - Chamadas de funções com argumentos corretos
    - Atribuição a constantes
    """
    
    def __init__(self):
        self.tabela = TabelaSimbolos()
        self.erros: List[ErroSemantico] = []
        self.avisos: List[AvisoSemantico] = []
        self.funcao_atual: Optional[Simbolo] = None
        self.tem_retorno: bool = False
        
        # Registrar funções built-in
        self._registrar_builtins()
    
    def _registrar_builtins(self):
        """Registra funções internas da linguagem."""
        # Conversões de tipo
        for nome, tipo_ret in [("paraInteiro", Tipo.INTEIRO), 
                               ("paraReal", Tipo.REAL),
                               ("paraTexto", Tipo.TEXTO)]:
            self.tabela.declarar(Simbolo(
                nome=nome,
                tipo=Tipo.FUNCAO,
                categoria="funcao",
                escopo=0,
                linha=0,
                coluna=0,
                parametros=[("valor", Tipo.DESCONHECIDO)],
                tipo_retorno=tipo_ret
            ))
        
        # Funções matemáticas
        for nome in ["raiz", "absoluto", "arredonda"]:
            self.tabela.declarar(Simbolo(
                nome=nome,
                tipo=Tipo.FUNCAO,
                categoria="funcao",
                escopo=0,
                linha=0,
                coluna=0,
                parametros=[("x", Tipo.REAL)],
                tipo_retorno=Tipo.REAL
            ))
        
        # Funções de texto
        self.tabela.declarar(Simbolo(
            nome="tamanho",
            tipo=Tipo.FUNCAO,
            categoria="funcao",
            escopo=0,
            linha=0,
            coluna=0,
            parametros=[("texto", Tipo.TEXTO)],
            tipo_retorno=Tipo.INTEIRO
        ))
    
    def erro(self, mensagem: str, linha: int, coluna: int):
        """Registra um erro semântico."""
        self.erros.append(ErroSemantico(mensagem, linha, coluna))
    
    def aviso(self, mensagem: str, linha: int, coluna: int):
        """Registra um aviso."""
        self.avisos.append(AvisoSemantico(mensagem, linha, coluna))
    
    def analisar(self, programa: Programa) -> bool:
        """
        Executa a análise semântica do programa.
        Retorna True se não houver erros.
        """
        print("╔═══════════════════════════════════════════════════════════════╗")
        print("║          INICIANDO ANÁLISE SEMÂNTICA                          ║")
        print("╚═══════════════════════════════════════════════════════════════╝")
        
        programa.aceitar(self)
        
        # Imprimir avisos
        for aviso in self.avisos:
            print(aviso)
        
        # Verificar se há erros
        if self.erros:
            print(f"\n❌ Análise semântica encontrou {len(self.erros)} erro(s):")
            for erro in self.erros:
                print(erro)
            return False
        
        print(f"✓ Análise semântica concluída com sucesso")
        if self.avisos:
            print(f"  ({len(self.avisos)} aviso(s))")
        
        return True
    
    
    # VERIFICAÇÃO DE TIPOS
    # ─────────────────────────────────────────────────────────────────────────
    
    def tipos_compativeis(self, tipo1: Tipo, tipo2: Tipo) -> bool:
        """Verifica se dois tipos são compatíveis."""
        if tipo1 == tipo2:
            return True
        
        # Inteiro pode ser promovido para real
        if tipo1 == Tipo.INTEIRO and tipo2 == Tipo.REAL:
            return True
        if tipo1 == Tipo.REAL and tipo2 == Tipo.INTEIRO:
            return True
        
        # Tipos especiais
        if tipo1 == Tipo.DESCONHECIDO or tipo2 == Tipo.DESCONHECIDO:
            return True
        if tipo1 == Tipo.ERRO or tipo2 == Tipo.ERRO:
            return True
        
        return False
    
    def tipo_resultante(self, tipo1: Tipo, tipo2: Tipo, operador: str) -> Tipo:
        """Determina o tipo resultante de uma operação binária."""
        # Operadores aritméticos
        if operador in ['+', '-', '*', '/', '%', '**']:
            if tipo1 == Tipo.TEXTO and tipo2 == Tipo.TEXTO and operador == '+':
                return Tipo.TEXTO
            if tipo1 in [Tipo.INTEIRO, Tipo.REAL] and tipo2 in [Tipo.INTEIRO, Tipo.REAL]:
                if tipo1 == Tipo.REAL or tipo2 == Tipo.REAL or operador == '/':
                    return Tipo.REAL
                return Tipo.INTEIRO
        
        # Operadores de comparação
        if operador in ['==', '!=', '<', '<=', '>', '>=']:
            return Tipo.LOGICO
        
        # Operadores lógicos
        if operador in ['e', 'ou']:
            return Tipo.LOGICO
        
        return Tipo.ERRO
    
    
    # VISITORS PARA DECLARAÇÕES
    # ─────────────────────────────────────────────────────────────────────────
    
    def visitar_programa(self, no: Programa) -> Any:
        """Visita o nó raiz do programa."""
        for declaracao in no.declaracoes:
            declaracao.aceitar(self)
        
        # Verificar se há função principal
        principal = self.tabela.buscar("principal")
        if not principal:
            self.aviso("Programa não possui função 'principal'", 1, 1)
        
        return None
    
    def visitar_funcao(self, no: DeclaracaoFuncao) -> Any:
        """Visita declaração de função."""
        # Verificar se já existe
        existente = self.tabela.buscar_local(no.nome)
        if existente:
            self.erro(
                f"Função '{no.nome}' já foi declarada na linha {existente.linha}",
                no.token_nome.linha, no.token_nome.coluna
            )
            return None
        
        # Criar símbolo da função
        tipo_retorno = MAPA_TIPOS.get(no.tipo_retorno, Tipo.VAZIO) if no.tipo_retorno else Tipo.VAZIO
        parametros = [(p[0], MAPA_TIPOS.get(p[1], Tipo.DESCONHECIDO)) for p in no.parametros]
        
        simbolo = Simbolo(
            nome=no.nome,
            tipo=Tipo.FUNCAO,
            categoria="funcao",
            escopo=self.tabela.escopo_atual,
            linha=no.token_nome.linha,
            coluna=no.token_nome.coluna,
            parametros=parametros,
            tipo_retorno=tipo_retorno
        )
        
        self.tabela.declarar(simbolo)
        
        # Entrar no escopo da função
        self.tabela.entrar_escopo()
        funcao_anterior = self.funcao_atual
        self.funcao_atual = simbolo
        self.tem_retorno = False
        
        # Declarar parâmetros
        for nome_param, tipo_param in parametros:
            param_simbolo = Simbolo(
                nome=nome_param,
                tipo=tipo_param,
                categoria="parametro",
                escopo=self.tabela.escopo_atual,
                linha=no.token_nome.linha,
                coluna=no.token_nome.coluna,
                inicializado=True
            )
            self.tabela.declarar(param_simbolo)
        
        # Analisar corpo
        no.corpo.aceitar(self)
        
        # Verificar retorno
        if tipo_retorno != Tipo.VAZIO and not self.tem_retorno:
            self.aviso(
                f"Função '{no.nome}' deveria retornar '{tipo_retorno}' mas nem todos os caminhos têm retorno",
                no.token_nome.linha, no.token_nome.coluna
            )
        
        # Sair do escopo
        self.tabela.sair_escopo()
        self.funcao_atual = funcao_anterior
        
        return None
    
    def visitar_declaracao_variavel(self, no: DeclaracaoVariavel) -> Any:
        """Visita declaração de variável."""
        # Verificar se já existe no escopo atual
        existente = self.tabela.buscar_local(no.nome)
        if existente:
            self.erro(
                f"Variável '{no.nome}' já foi declarada neste escopo (linha {existente.linha})",
                no.token_nome.linha, no.token_nome.coluna
            )
            return None
        
        # Determinar tipo
        tipo = MAPA_TIPOS.get(no.tipo_dado, Tipo.DESCONHECIDO) if no.tipo_dado else Tipo.DESCONHECIDO
        
        # Verificar inicializador
        tipo_inicializador = None
        if no.inicializador:
            tipo_inicializador = no.inicializador.aceitar(self)
            
            if tipo == Tipo.DESCONHECIDO:
                # Inferir tipo do inicializador
                tipo = tipo_inicializador
            elif not self.tipos_compativeis(tipo, tipo_inicializador):
                self.erro(
                    f"Tipo incompatível: não é possível atribuir '{tipo_inicializador}' a '{tipo}'",
                    no.token_nome.linha, no.token_nome.coluna
                )
        
        # Verificar constante sem inicializador
        if no.constante and not no.inicializador:
            self.erro(
                f"Constante '{no.nome}' deve ser inicializada na declaração",
                no.token_nome.linha, no.token_nome.coluna
            )
        
        # Criar símbolo
        simbolo = Simbolo(
            nome=no.nome,
            tipo=tipo,
            categoria="constante" if no.constante else "variavel",
            escopo=self.tabela.escopo_atual,
            linha=no.token_nome.linha,
            coluna=no.token_nome.coluna,
            constante=no.constante,
            inicializado=no.inicializador is not None
        )
        
        self.tabela.declarar(simbolo)
        return tipo
    
    def visitar_bloco(self, no: DeclaracaoBloco) -> Any:
        """Visita um bloco de código."""
        self.tabela.entrar_escopo()
        
        for declaracao in no.declaracoes:
            declaracao.aceitar(self)
        
        self.tabela.sair_escopo()
        return None
    
    def visitar_se(self, no: DeclaracaoSe) -> Any:
        """Visita declaração se/senao."""
        tipo_cond = no.condicao.aceitar(self)
        
        if tipo_cond != Tipo.LOGICO and tipo_cond != Tipo.ERRO:
            self.erro(
                f"Condição do 'se' deve ser do tipo 'logico', mas é '{tipo_cond}'",
                no.condicao.token.linha if hasattr(no.condicao, 'token') else 0,
                no.condicao.token.coluna if hasattr(no.condicao, 'token') else 0
            )
        
        # Analisar ramos
        tem_retorno_antes = self.tem_retorno
        
        no.bloco_verdadeiro.aceitar(self)
        tem_retorno_verdadeiro = self.tem_retorno
        
        tem_retorno_falso = False
        if no.bloco_falso:
            self.tem_retorno = tem_retorno_antes
            no.bloco_falso.aceitar(self)
            tem_retorno_falso = self.tem_retorno
        
        # Só tem retorno garantido se ambos os ramos retornam
        self.tem_retorno = tem_retorno_verdadeiro and tem_retorno_falso
        
        return None
    
    def visitar_enquanto(self, no: DeclaracaoEnquanto) -> Any:
        """Visita declaração enquanto."""
        tipo_cond = no.condicao.aceitar(self)
        
        if tipo_cond != Tipo.LOGICO and tipo_cond != Tipo.ERRO:
            self.erro(
                f"Condição do 'enquanto' deve ser do tipo 'logico', mas é '{tipo_cond}'",
                0, 0
            )
        
        no.corpo.aceitar(self)
        return None
    
    def visitar_para(self, no: DeclaracaoPara) -> Any:
        """Visita declaração para (for)."""
        # Criar escopo para a variável do loop
        self.tabela.entrar_escopo()
        
        # Declarar variável do loop
        simbolo = Simbolo(
            nome=no.variavel,
            tipo=Tipo.INTEIRO,
            categoria="variavel",
            escopo=self.tabela.escopo_atual,
            linha=no.token_variavel.linha,
            coluna=no.token_variavel.coluna,
            inicializado=True
        )
        self.tabela.declarar(simbolo)
        
        # Verificar tipos de início e fim
        tipo_inicio = no.inicio.aceitar(self)
        tipo_fim = no.fim.aceitar(self)
        
        if tipo_inicio not in [Tipo.INTEIRO, Tipo.REAL]:
            self.erro(
                f"Valor inicial do 'para' deve ser numérico, mas é '{tipo_inicio}'",
                no.token_variavel.linha, no.token_variavel.coluna
            )
        
        if tipo_fim not in [Tipo.INTEIRO, Tipo.REAL]:
            self.erro(
                f"Valor final do 'para' deve ser numérico, mas é '{tipo_fim}'",
                no.token_variavel.linha, no.token_variavel.coluna
            )
        
        if no.passo:
            tipo_passo = no.passo.aceitar(self)
            if tipo_passo not in [Tipo.INTEIRO, Tipo.REAL]:
                self.erro(
                    f"Passo do 'para' deve ser numérico, mas é '{tipo_passo}'",
                    no.token_variavel.linha, no.token_variavel.coluna
                )
        
        # Analisar corpo
        no.corpo.aceitar(self)
        
        self.tabela.sair_escopo()
        return None
    
    def visitar_retorna(self, no: DeclaracaoRetorna) -> Any:
        """Visita declaração retorna."""
        self.tem_retorno = True
        
        if not self.funcao_atual:
            self.erro(
                "'retorna' fora de uma função",
                no.token.linha, no.token.coluna
            )
            return None
        
        tipo_esperado = self.funcao_atual.tipo_retorno
        
        if no.valor:
            tipo_valor = no.valor.aceitar(self)
            
            if tipo_esperado == Tipo.VAZIO:
                self.erro(
                    f"Função '{self.funcao_atual.nome}' não deveria retornar valor",
                    no.token.linha, no.token.coluna
                )
            elif not self.tipos_compativeis(tipo_esperado, tipo_valor):
                self.erro(
                    f"Tipo de retorno incompatível: esperado '{tipo_esperado}', recebido '{tipo_valor}'",
                    no.token.linha, no.token.coluna
                )
        else:
            if tipo_esperado != Tipo.VAZIO:
                self.erro(
                    f"Função '{self.funcao_atual.nome}' deveria retornar '{tipo_esperado}'",
                    no.token.linha, no.token.coluna
                )
        
        return None
    
    def visitar_escreva(self, no: DeclaracaoEscreva) -> Any:
        """Visita declaração escreva."""
        for expr in no.expressoes:
            expr.aceitar(self)
        return None
    
    def visitar_leia(self, no: DeclaracaoLeia) -> Any:
        """Visita declaração leia."""
        simbolo = self.tabela.buscar(no.variavel)
        
        if not simbolo:
            self.erro(
                f"Variável '{no.variavel}' não foi declarada",
                no.token_variavel.linha, no.token_variavel.coluna
            )
        elif simbolo.constante:
            self.erro(
                f"Não é possível ler para constante '{no.variavel}'",
                no.token_variavel.linha, no.token_variavel.coluna
            )
        else:
            simbolo.inicializado = True
        
        if no.mensagem:
            tipo_msg = no.mensagem.aceitar(self)
            if tipo_msg != Tipo.TEXTO:
                self.erro(
                    f"Mensagem do 'leia' deve ser texto, mas é '{tipo_msg}'",
                    no.token_variavel.linha, no.token_variavel.coluna
                )
        
        return None
    
    def visitar_declaracao_expressao(self, no: DeclaracaoExpressao) -> Any:
        """Visita expressão como declaração."""
        return no.expressao.aceitar(self)
    
    
    # VISITORS PARA EXPRESSÕES
    # ─────────────────────────────────────────────────────────────────────────
    
    def visitar_literal(self, no: ExpressaoLiteral) -> Tipo:
        """Visita literal."""
        return MAPA_TIPOS.get(no.tipo, Tipo.DESCONHECIDO)
    
    def visitar_variavel(self, no: ExpressaoVariavel) -> Tipo:
        """Visita acesso a variável."""
        simbolo = self.tabela.buscar(no.nome)
        
        if not simbolo:
            self.erro(
                f"Variável '{no.nome}' não foi declarada",
                no.token.linha, no.token.coluna
            )
            return Tipo.ERRO
        
        if not simbolo.inicializado and simbolo.categoria == "variavel":
            self.aviso(
                f"Variável '{no.nome}' pode não estar inicializada",
                no.token.linha, no.token.coluna
            )
        
        return simbolo.tipo
    
    def visitar_binaria(self, no: ExpressaoBinaria) -> Tipo:
        """Visita expressão binária."""
        tipo_esq = no.esquerda.aceitar(self)
        tipo_dir = no.direita.aceitar(self)
        operador = no.operador.lexema
        
        # Verificar compatibilidade
        tipo_resultado = self.tipo_resultante(tipo_esq, tipo_dir, operador)
        
        if tipo_resultado == Tipo.ERRO:
            self.erro(
                f"Operador '{operador}' não pode ser aplicado a '{tipo_esq}' e '{tipo_dir}'",
                no.operador.linha, no.operador.coluna
            )
        
        return tipo_resultado
    
    def visitar_unaria(self, no: ExpressaoUnaria) -> Tipo:
        """Visita expressão unária."""
        tipo_operando = no.operando.aceitar(self)
        operador = no.operador.lexema
        
        if operador == '-':
            if tipo_operando not in [Tipo.INTEIRO, Tipo.REAL]:
                self.erro(
                    f"Operador '-' não pode ser aplicado a '{tipo_operando}'",
                    no.operador.linha, no.operador.coluna
                )
                return Tipo.ERRO
            return tipo_operando
        
        if operador == 'nao':
            if tipo_operando != Tipo.LOGICO:
                self.erro(
                    f"Operador 'nao' só pode ser aplicado a 'logico', não a '{tipo_operando}'",
                    no.operador.linha, no.operador.coluna
                )
                return Tipo.ERRO
            return Tipo.LOGICO
        
        return tipo_operando
    
    def visitar_agrupamento(self, no: ExpressaoAgrupamento) -> Tipo:
        """Visita expressão agrupada."""
        return no.expressao.aceitar(self)
    
    def visitar_atribuicao(self, no: ExpressaoAtribuicao) -> Tipo:
        """Visita atribuição."""
        simbolo = self.tabela.buscar(no.nome)
        
        if not simbolo:
            self.erro(
                f"Variável '{no.nome}' não foi declarada",
                no.token_nome.linha, no.token_nome.coluna
            )
            return Tipo.ERRO
        
        if simbolo.constante:
            self.erro(
                f"Não é possível atribuir a constante '{no.nome}'",
                no.token_nome.linha, no.token_nome.coluna
            )
        
        tipo_valor = no.valor.aceitar(self)
        
        if not self.tipos_compativeis(simbolo.tipo, tipo_valor):
            self.erro(
                f"Tipo incompatível: não é possível atribuir '{tipo_valor}' a '{simbolo.tipo}'",
                no.token_nome.linha, no.token_nome.coluna
            )
        
        simbolo.inicializado = True
        return simbolo.tipo
    
    def visitar_logica(self, no: ExpressaoLogica) -> Tipo:
        """Visita expressão lógica."""
        tipo_esq = no.esquerda.aceitar(self)
        tipo_dir = no.direita.aceitar(self)
        
        if tipo_esq != Tipo.LOGICO:
            self.erro(
                f"Operador '{no.operador.lexema}' requer operando esquerdo 'logico', não '{tipo_esq}'",
                no.operador.linha, no.operador.coluna
            )
        
        if tipo_dir != Tipo.LOGICO:
            self.erro(
                f"Operador '{no.operador.lexema}' requer operando direito 'logico', não '{tipo_dir}'",
                no.operador.linha, no.operador.coluna
            )
        
        return Tipo.LOGICO
    
    def visitar_chamada_funcao(self, no: ExpressaoChamadaFuncao) -> Tipo:
        """Visita chamada de função."""
        simbolo = self.tabela.buscar(no.nome)
        
        if not simbolo:
            self.erro(
                f"Função '{no.nome}' não foi declarada",
                no.token_nome.linha, no.token_nome.coluna
            )
            return Tipo.ERRO
        
        if simbolo.tipo != Tipo.FUNCAO:
            self.erro(
                f"'{no.nome}' não é uma função",
                no.token_nome.linha, no.token_nome.coluna
            )
            return Tipo.ERRO
        
        # Verificar número de argumentos
        num_params = len(simbolo.parametros)
        num_args = len(no.argumentos)
        
        if num_args != num_params:
            self.erro(
                f"Função '{no.nome}' espera {num_params} argumento(s), mas recebeu {num_args}",
                no.token_nome.linha, no.token_nome.coluna
            )
        
        # Verificar tipos dos argumentos
        for i, (arg, param) in enumerate(zip(no.argumentos, simbolo.parametros)):
            tipo_arg = arg.aceitar(self)
            tipo_param = param[1]
            
            if not self.tipos_compativeis(tipo_param, tipo_arg):
                self.erro(
                    f"Argumento {i+1} de '{no.nome}': esperado '{tipo_param}', recebido '{tipo_arg}'",
                    no.token_nome.linha, no.token_nome.coluna
                )
        
        return simbolo.tipo_retorno or Tipo.VAZIO
    
    def visitar_acesso_array(self, no: ExpressaoAcessoArray) -> Tipo:
        """Visita acesso a array."""
        tipo_indice = no.indice.aceitar(self)
        
        if tipo_indice != Tipo.INTEIRO:
            self.erro(
                f"Índice de array deve ser 'inteiro', não '{tipo_indice}'",
                no.token_colchete.linha, no.token_colchete.coluna
            )
        
        # Por enquanto, retornamos DESCONHECIDO
        return Tipo.DESCONHECIDO



# TESTE DO ANALISADOR SEMÂNTICO
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    from parser import Parser
    
    codigo_teste = '''
// Teste de análise semântica
funcao somar(a: inteiro, b: inteiro): inteiro {
    retorna a + b
}

funcao principal(): inteiro {
    var x: inteiro = 10
    var y: inteiro = 20
    var resultado: inteiro
    
    resultado = somar(x, y)
    escreva("Resultado: ", resultado)
    
    // Teste de tipos
    var nome: texto = "Lusitano"
    var pi: real = 3.14159
    var ativo: logico = verdadeiro
    
    // Teste de controle de fluxo
    se (x > y) {
        escreva("x é maior")
    } senao {
        escreva("y é maior ou igual")
    }
    
    // Teste de loop
    var soma: inteiro = 0
    para i de 1 ate 10 {
        soma = soma + i
    }
    
    // Constante
    const PI: real = 3.14159
    
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
        
        # Análise Semântica
        analisador = AnalisadorSemantico()
        sucesso = analisador.analisar(ast)
        
        # Mostrar tabela de símbolos
        analisador.tabela.imprimir()
        
    except Exception as e:
        print(f"Erro: {e}")
