"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║                    ██╗     ██╗   ██╗███████╗██╗████████╗ █████╗ ███╗   ██╗ ██████╗ ║
║                    ██║     ██║   ██║██╔════╝██║╚══██╔══╝██╔══██╗████╗  ██║██╔═══██╗║
║                    ██║     ██║   ██║███████╗██║   ██║   ███████║██╔██╗ ██║██║   ██║║
║                    ██║     ██║   ██║╚════██║██║   ██║   ██╔══██║██║╚██╗██║██║   ██║║
║                    ███████╗╚██████╔╝███████║██║   ██║   ██║  ██║██║ ╚████║╚██████╔╝║
║                    ╚══════╝ ╚═════╝ ╚══════╝╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝ ║
║                                                                               ║
║                    Uma Linguagem de Programação em Português                  ║
║                                                                               ║
║  ┌─────────────────────────────────────────────────────────────────────────┐  ║
║  │  Código Fonte (.lus)  →  Scanner  →  Parser  →  Semântico  →  Python   │  ║
║  └─────────────────────────────────────────────────────────────────────────┘  ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Desenvolvido para apresentação acadêmica de Compiladores
"""

import sys
import json
from typing import Optional
from lexer import Scanner, ErroLexico, Token
from parser import Parser, VisualizadorAST, Programa, NoAST, VisitanteAST
from parser import (
    ExpressaoLiteral, ExpressaoVariavel, ExpressaoBinaria, ExpressaoUnaria,
    ExpressaoAgrupamento, ExpressaoAtribuicao, ExpressaoLogica,
    ExpressaoChamadaFuncao, ExpressaoAcessoArray, DeclaracaoExpressao,
    DeclaracaoVariavel, DeclaracaoBloco, DeclaracaoSe, DeclaracaoEnquanto,
    DeclaracaoPara, DeclaracaoFuncao, DeclaracaoRetorna, DeclaracaoEscreva,
    DeclaracaoLeia
)
from semantico import AnalisadorSemantico, ErroSemantico



# GERADOR DE CÓDIGO PYTHON (TRANSPILADOR)
# ═══════════════════════════════════════════════════════════════════════════════

class GeradorPython(VisitanteAST):
    """
    Gera código Python a partir da AST.
    
    Este é um transpilador que converte código Lusitano para Python,
    permitindo executar o programa diretamente.
    """
    
    def __init__(self):
        self.indent_level = 0
        self.codigo = []
        self.em_expressao = False
    
    def _indent(self) -> str:
        return "    " * self.indent_level
    
    def _adicionar(self, linha: str):
        self.codigo.append(self._indent() + linha)
    
    def gerar(self, programa: Programa) -> str:
        """Gera código Python a partir do programa."""
        print("╔═══════════════════════════════════════════════════════════════╗")
        print("║           GERANDO CÓDIGO PYTHON (TRANSPILADOR)                ║")
        print("╚═══════════════════════════════════════════════════════════════╝")
        
        # Header do código gerado
        self.codigo = [
            "# -*- coding: utf-8 -*-",
            '"""',
            "Código gerado automaticamente pelo Compilador Lusitano",
            "Linguagem fonte: Lusitano (Português)",
            '"""',
            "",
            "# Funções auxiliares",
            "def leia(mensagem=''):",
            "    return input(mensagem)",
            "",
            "def paraInteiro(valor):",
            "    return int(valor)",
            "",
            "def paraReal(valor):",
            "    return float(valor)",
            "",
            "def paraTexto(valor):",
            "    return str(valor)",
            "",
            "def raiz(x):",
            "    return x ** 0.5",
            "",
            "def absoluto(x):",
            "    return abs(x)",
            "",
            "def arredonda(x):",
            "    return round(x)",
            "",
            "def tamanho(texto):",
            "    return len(texto)",
            "",
            "# ═══════════════════════════════════════",
            "# Código do programa Lusitano",
            "# ═══════════════════════════════════════",
            ""
        ]
        
        programa.aceitar(self)
        
        # Chamar função principal se existir
        self.codigo.append("")
        self.codigo.append("# Ponto de entrada")
        self.codigo.append("if __name__ == '__main__':")
        self.codigo.append("    try:")
        self.codigo.append("        principal()")
        self.codigo.append("    except NameError:")
        self.codigo.append("        pass  # Função principal não definida")
        
        codigo_final = "\n".join(self.codigo)
        print(f"✓ Código Python gerado ({len(self.codigo)} linhas)\n")
        return codigo_final
    
    
    # VISITORS
    # ─────────────────────────────────────────────────────────────────────────
    
    def visitar_programa(self, no: Programa) -> str:
        for decl in no.declaracoes:
            decl.aceitar(self)
        return ""
    
    def visitar_literal(self, no: ExpressaoLiteral) -> str:
        if no.tipo == "texto":
            return repr(no.valor)
        elif no.tipo == "logico":
            return "True" if no.valor else "False"
        return str(no.valor)
    
    def visitar_variavel(self, no: ExpressaoVariavel) -> str:
        return no.nome
    
    def visitar_binaria(self, no: ExpressaoBinaria) -> str:
        esq = no.esquerda.aceitar(self)
        dir = no.direita.aceitar(self)
        op = no.operador.lexema
        
        # Mapear operadores
        mapa_ops = {
            '==': '==',
            '!=': '!=',
            '<': '<',
            '<=': '<=',
            '>': '>',
            '>=': '>=',
            '+': '+',
            '-': '-',
            '*': '*',
            '/': '/',
            '%': '%',
            '**': '**',
        }
        
        op_python = mapa_ops.get(op, op)
        return f"({esq} {op_python} {dir})"
    
    def visitar_unaria(self, no: ExpressaoUnaria) -> str:
        operando = no.operando.aceitar(self)
        op = no.operador.lexema
        
        if op == 'nao':
            return f"(not {operando})"
        return f"({op}{operando})"
    
    def visitar_agrupamento(self, no: ExpressaoAgrupamento) -> str:
        return f"({no.expressao.aceitar(self)})"
    
    def visitar_atribuicao(self, no: ExpressaoAtribuicao) -> str:
        valor = no.valor.aceitar(self)
        if self.em_expressao:
            return f"({no.nome} := {valor})"
        return f"{no.nome} = {valor}"
    
    def visitar_logica(self, no: ExpressaoLogica) -> str:
        esq = no.esquerda.aceitar(self)
        dir = no.direita.aceitar(self)
        op = "and" if no.operador.lexema == "e" else "or"
        return f"({esq} {op} {dir})"
    
    def visitar_chamada_funcao(self, no: ExpressaoChamadaFuncao) -> str:
        args = ", ".join([arg.aceitar(self) for arg in no.argumentos])
        return f"{no.nome}({args})"
    
    def visitar_acesso_array(self, no: ExpressaoAcessoArray) -> str:
        obj = no.objeto.aceitar(self)
        idx = no.indice.aceitar(self)
        return f"{obj}[{idx}]"
    
    def visitar_declaracao_expressao(self, no: DeclaracaoExpressao) -> str:
        self.em_expressao = False
        expr = no.expressao.aceitar(self)
        self._adicionar(expr)
        return ""
    
    def visitar_declaracao_variavel(self, no: DeclaracaoVariavel) -> str:
        if no.inicializador:
            valor = no.inicializador.aceitar(self)
            self._adicionar(f"{no.nome} = {valor}")
        else:
            # Valores padrão por tipo
            valores_padrao = {
                'inteiro': '0',
                'real': '0.0',
                'texto': '""',
                'logico': 'False'
            }
            valor = valores_padrao.get(no.tipo_dado, 'None')
            self._adicionar(f"{no.nome} = {valor}")
        return ""
    
    def visitar_bloco(self, no: DeclaracaoBloco) -> str:
        for decl in no.declaracoes:
            decl.aceitar(self)
        return ""
    
    def visitar_se(self, no: DeclaracaoSe) -> str:
        cond = no.condicao.aceitar(self)
        self._adicionar(f"if {cond}:")
        
        self.indent_level += 1
        no.bloco_verdadeiro.aceitar(self)
        if not no.bloco_verdadeiro.declaracoes if hasattr(no.bloco_verdadeiro, 'declaracoes') else True:
            self._adicionar("pass")
        self.indent_level -= 1
        
        if no.bloco_falso:
            # Verifica se é um senaose (else if)
            if isinstance(no.bloco_falso, DeclaracaoSe):
                cond_elif = no.bloco_falso.condicao.aceitar(self)
                self._adicionar(f"elif {cond_elif}:")
                self.indent_level += 1
                no.bloco_falso.bloco_verdadeiro.aceitar(self)
                self.indent_level -= 1
                if no.bloco_falso.bloco_falso:
                    self._adicionar("else:")
                    self.indent_level += 1
                    no.bloco_falso.bloco_falso.aceitar(self)
                    self.indent_level -= 1
            else:
                self._adicionar("else:")
                self.indent_level += 1
                no.bloco_falso.aceitar(self)
                self.indent_level -= 1
        
        return ""
    
    def visitar_enquanto(self, no: DeclaracaoEnquanto) -> str:
        cond = no.condicao.aceitar(self)
        self._adicionar(f"while {cond}:")
        
        self.indent_level += 1
        no.corpo.aceitar(self)
        self.indent_level -= 1
        
        return ""
    
    def visitar_para(self, no: DeclaracaoPara) -> str:
        inicio = no.inicio.aceitar(self)
        fim = no.fim.aceitar(self)
        
        if no.passo:
            passo = no.passo.aceitar(self)
            self._adicionar(f"for {no.variavel} in range({inicio}, {fim} + 1, {passo}):")
        else:
            self._adicionar(f"for {no.variavel} in range({inicio}, {fim} + 1):")
        
        self.indent_level += 1
        no.corpo.aceitar(self)
        self.indent_level -= 1
        
        return ""
    
    def visitar_funcao(self, no: DeclaracaoFuncao) -> str:
        params = ", ".join([p[0] for p in no.parametros])
        self._adicionar(f"def {no.nome}({params}):")
        
        self.indent_level += 1
        no.corpo.aceitar(self)
        
        # Adiciona pass se o corpo estiver vazio
        if not no.corpo.declaracoes:
            self._adicionar("pass")
        
        self.indent_level -= 1
        self._adicionar("")  # Linha em branco após função
        
        return ""
    
    def visitar_retorna(self, no: DeclaracaoRetorna) -> str:
        if no.valor:
            valor = no.valor.aceitar(self)
            self._adicionar(f"return {valor}")
        else:
            self._adicionar("return")
        return ""
    
    def visitar_escreva(self, no: DeclaracaoEscreva) -> str:
        args = ", ".join([e.aceitar(self) for e in no.expressoes])
        self._adicionar(f"print({args}, sep='')")
        return ""
    
    def visitar_leia(self, no: DeclaracaoLeia) -> str:
        if no.mensagem:
            msg = no.mensagem.aceitar(self)
            self._adicionar(f"{no.variavel} = input({msg})")
        else:
            self._adicionar(f"{no.variavel} = input()")
        return ""



# COMPILADOR PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

class CompiladorLusitano:
    """
    Compilador completo da linguagem Lusitano.
    
    Fases:
    1. Análise Léxica (Scanner)
    2. Análise Sintática (Parser)
    3. Análise Semântica
    4. Geração de Código (Transpilação para Python)
    """
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.scanner: Optional[Scanner] = None
        self.parser: Optional[Parser] = None
        self.analisador: Optional[AnalisadorSemantico] = None
        self.gerador: Optional[GeradorPython] = None
        self.ast: Optional[Programa] = None
        self.codigo_python: Optional[str] = None
    
    def banner(self):
        """Exibe o banner do compilador."""
        print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║    ██╗     ██╗   ██╗███████╗██╗████████╗ █████╗ ███╗   ██╗ ██████╗            ║
║    ██║     ██║   ██║██╔════╝██║╚══██╔══╝██╔══██╗████╗  ██║██╔═══██╗           ║
║    ██║     ██║   ██║███████╗██║   ██║   ███████║██╔██╗ ██║██║   ██║           ║
║    ██║     ██║   ██║╚════██║██║   ██║   ██╔══██║██║╚██╗██║██║   ██║           ║
║    ███████╗╚██████╔╝███████║██║   ██║   ██║  ██║██║ ╚████║╚██████╔╝           ║
║    ╚══════╝ ╚═════╝ ╚══════╝╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝            ║
║                                                                               ║
║              Uma Linguagem de Programação em Português                        ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
        """)
    
    def compilar(self, codigo_fonte: str, executar: bool = False) -> bool:
        """
        Compila o código fonte Lusitano.
        
        Args:
            codigo_fonte: Código em Lusitano
            executar: Se True, executa o código gerado
            
        Returns:
            True se a compilação foi bem-sucedida
        """
        self.banner()
        
        try:
            # ─── FASE 1: Análise Léxica ───
            self.scanner = Scanner(codigo_fonte)
            tokens = self.scanner.escanear()
            
            if self.verbose:
                self.scanner.imprimir_tokens()
            
            # ─── FASE 2: Análise Sintática ───
            self.parser = Parser(tokens)
            self.ast = self.parser.analisar()
            
            if self.verbose:
                print("\n" + "═" * 70)
                print("                    ÁRVORE SINTÁTICA ABSTRATA (AST)")
                print("═" * 70 + "\n")
                visualizador = VisualizadorAST()
                print(visualizador.visualizar(self.ast))
            
            # ─── FASE 3: Análise Semântica ───
            self.analisador = AnalisadorSemantico()
            if not self.analisador.analisar(self.ast):
                return False
            
            if self.verbose:
                self.analisador.tabela.imprimir()
            
            # ─── FASE 4: Geração de Código ───
            self.gerador = GeradorPython()
            self.codigo_python = self.gerador.gerar(self.ast)
            
            if self.verbose:
                print("\n" + "═" * 70)
                print("                    CÓDIGO PYTHON GERADO")
                print("═" * 70 + "\n")
                
                # Numerar linhas
                for i, linha in enumerate(self.codigo_python.split('\n'), 1):
                    print(f"{i:4} │ {linha}")
            
            # ─── Executar (opcional) ───
            if executar:
                print("\n" + "═" * 70)
                print("                    EXECUÇÃO DO PROGRAMA")
                print("═" * 70 + "\n")
                
                exec(self.codigo_python, {'__name__': '__main__'})
            
            print("\n" + "═" * 70)
            print("              ✅ COMPILAÇÃO CONCLUÍDA COM SUCESSO!")
            print("═" * 70 + "\n")
            
            return True
            
        except ErroLexico as e:
            print(e)
            return False
        except Exception as e:
            print(f"\n❌ Erro durante a compilação: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def salvar_python(self, caminho: str):
        """Salva o código Python gerado em um arquivo."""
        if self.codigo_python:
            with open(caminho, 'w', encoding='utf-8') as f:
                f.write(self.codigo_python)
            print(f"✓ Código salvo em: {caminho}")
    
    def exportar_ast_json(self, caminho: str):
        """Exporta a AST em formato JSON."""
        if self.ast:
            with open(caminho, 'w', encoding='utf-8') as f:
                json.dump(self.ast.para_dict(), f, indent=2, ensure_ascii=False)
            print(f"✓ AST exportada em: {caminho}")



# PROGRAMA DE EXEMPLO
# ═══════════════════════════════════════════════════════════════════════════════

PROGRAMA_EXEMPLO = '''
// ═══════════════════════════════════════════════════════════════
// Programa de demonstração da linguagem Lusitano
// ═══════════════════════════════════════════════════════════════

// Função para calcular fatorial recursivamente
funcao fatorial(n: inteiro): inteiro {
    se (n <= 1) {
        retorna 1
    }
    retorna n * fatorial(n - 1)
}

// Função para verificar se um número é par
funcao ehPar(numero: inteiro): logico {
    retorna numero % 2 == 0
}

// Função para calcular a soma de 1 até n
funcao somaAte(n: inteiro): inteiro {
    var soma: inteiro = 0
    para i de 1 ate n {
        soma = soma + i
    }
    retorna soma
}

// Função principal do programa
funcao principal(): inteiro {
    // Declaração de variáveis
    var nome: texto = "Lusitano"
    var versao: real = 1.0
    var ativo: logico = verdadeiro
    
    // Mensagem de boas-vindas
    escreva("╔═════════════════════════════════════════╗")
    escreva("║   Bem-vindo à linguagem ", nome, "!    ║")
    escreva("║   Versão: ", versao, "                         ║")
    escreva("╚═════════════════════════════════════════╝")
    escreva("")
    
    // Demonstração de fatorial
    escreva("📊 Cálculo de Fatoriais:")
    para n de 1 ate 6 {
        escreva("   ", n, "! = ", fatorial(n))
    }
    escreva("")
    
    // Demonstração de números pares
    escreva("🔢 Números de 1 a 10:")
    para i de 1 ate 10 {
        se (ehPar(i)) {
            escreva("   ", i, " é PAR")
        } senao {
            escreva("   ", i, " é ÍMPAR")
        }
    }
    escreva("")
    
    // Demonstração de soma
    var limite: inteiro = 100
    escreva("➕ Soma de 1 até ", limite, ": ", somaAte(limite))
    escreva("")
    
    // Demonstração de while
    escreva("🔄 Contagem regressiva:")
    var contador: inteiro = 5
    enquanto (contador > 0) {
        escreva("   ", contador, "...")
        contador = contador - 1
    }
    escreva("   🚀 Lançamento!")
    escreva("")
    
    // Expressões matemáticas
    var a: inteiro = 10
    var b: inteiro = 3
    escreva("🧮 Operações com a=", a, " e b=", b, ":")
    escreva("   Soma: ", a + b)
    escreva("   Subtração: ", a - b)
    escreva("   Multiplicação: ", a * b)
    escreva("   Divisão: ", a / b)
    escreva("   Módulo: ", a % b)
    escreva("   Potência: ", a ** b)
    escreva("")
    
    escreva("✅ Programa finalizado com sucesso!")
    
    retorna 0
}
'''



# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    compilador = CompiladorLusitano(verbose=True)
    
    if len(sys.argv) > 1:
        # Compilar arquivo
        arquivo = sys.argv[1]
        try:
            with open(arquivo, 'r', encoding='utf-8') as f:
                codigo = f.read()
            
            executar = '--run' in sys.argv or '-r' in sys.argv
            compilador.compilar(codigo, executar=executar)
            
            # Salvar código Python
            if '--output' in sys.argv or '-o' in sys.argv:
                idx = sys.argv.index('--output' if '--output' in sys.argv else '-o')
                if idx + 1 < len(sys.argv):
                    compilador.salvar_python(sys.argv[idx + 1])
                    
        except FileNotFoundError:
            print(f"Erro: Arquivo '{arquivo}' não encontrado.")
    else:
        # Executar exemplo
        print("Uso: python lusitano.py <arquivo.lus> [-r|--run] [-o|--output <arquivo.py>]")
        print("\nExecutando programa de demonstração...\n")
        compilador.compilar(PROGRAMA_EXEMPLO, executar=True)
