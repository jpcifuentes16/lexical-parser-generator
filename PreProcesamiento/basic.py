from error import *
from tokenObj import *
from character import Character

#######################################
# CONSTANTES
#######################################

DIGITOS = list(map(chr, range(ord('0'), ord('9')+1))) + \
    ['.'] + list(map(chr, range(ord('a'), ord('z')+1)))


#######################################
# TOKENS
#######################################
# Constantes tokens tipos
TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_OR = 'OR'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_CONCAT = 'CONCAT'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_LBRACKET = 'LBRACKET'
TT_RBRACKET = 'RBRACKET'
TT_LBRACES = 'LBRACES'
TT_RBRACES = 'RBRACES'
TT_EOF = 'EOF'

# equivalente de cada token pero en simbolos
diccionario = {
    'PLUS': '+',
    'MINUS': '-',
    'MUL': '*',
    'DIV': '/',
    'OR': '|',
    'CONCAT': '.'
}


#######################################
# LEXER
#######################################

class Lexer:
    '''
    Encargado de asignar tokens a cada conjunto
    de caracteres identificado, caso contrario
    error
    '''

    def __init__(self, textoPlano):
        self.textoPlano = textoPlano
        self.pos = -1
        self.charActual = None
        self.avanzar()

    def avanzar(self):
        '''
        Avanza una posicion en el textoPlano si no ha llegado al
        final del texto, caso contrario None
        '''
        self.pos += 1
        if self.pos < len(self.textoPlano):
            self.charActual = self.textoPlano[self.pos]
        else:
            self.charActual = None

    def explorar(self):
        '''
        retorna el siguiente token si no ha llegado al final
        '''

        if self.pos + 1 < len(self.textoPlano):
            return self.textoPlano[self.pos + 1]
        else:
            return None

    def crearTokens(self):
        '''
        Crea una lista de tokens
        '''
        tokens = []

        # Mientras no haya llegado al final
        while self.charActual != None:
            if (isinstance(self.charActual, Character) and isinstance(self.explorar(), Character)):
                tokens.append(Token(TT_INT, self.charActual))
                tokens.append(Token(TT_CONCAT))
                tokens.append(Token(TT_INT, self.explorar()))
                self.avanzar()
                self.avanzar()
            elif isinstance(self.charActual, Character):
                tokens.append(Token(TT_INT, self.charActual))
                self.avanzar()
            # si es un espacio o tab solo avanza
            elif self.charActual in ' \t':
                self.avanzar()

                '''
				sino intenta reconocer el token y lo
				agrega a la lista tokens
				'''
            elif self.charActual in DIGITOS:
                tokens.append(self.crearNumero())
            elif self.charActual == '+':
                tokens.append(Token(TT_PLUS))
                self.avanzar()
            elif self.charActual == '-':
                tokens.append(Token(TT_MINUS))
                self.avanzar()
            elif self.charActual == '|':
                tokens.append(Token(TT_OR))
                self.avanzar()
            elif self.charActual == '*':
                tokens.append(Token(TT_MUL))
                self.avanzar()
            elif self.charActual == '/':
                tokens.append(Token(TT_DIV))
                self.avanzar()
            elif self.charActual == '(':
                tokens.append(Token(TT_LPAREN))
                self.avanzar()
            elif self.charActual == ')':
                tokens.append(Token(TT_RPAREN))
                self.avanzar()
            elif self.charActual == '[':
                tokens.append(Token(TT_LBRACKET))
                self.avanzar()
            elif self.charActual == ']':
                tokens.append(Token(TT_RBRACKET))
                self.avanzar()
            elif self.charActual == '{':
                tokens.append(Token(TT_LBRACES))
                self.avanzar()
            elif self.charActual == '}':
                tokens.append(Token(TT_RBRACES))
                self.avanzar()
            else:
                # Retorna error si no reconoce el caracter
                char = self.charActual
                self.avanzar()
                return [], IllegalCharError(f"'{char}'")

        # al final agrega el token de final
        tokens.append(Token(TT_EOF))
        return tokens, None

    def crearNumero(self):
        numContact = ''
        contadorPuntos = 0

        '''
		Mientras no haya llegado al final del texto plano
		y el char actual sea numero o punto
		'''
        while self.charActual != None and self.charActual in DIGITOS:

            # Cuenta los puntos
            if self.charActual == '.':
                # Si ya hay un punto para
                if contadorPuntos == 1:
                    break
                contadorPuntos += 1
                numContact += '.'
            else:
                numContact += self.charActual
            self.avanzar()

        # decide si es un numero int o float
        if contadorPuntos == 0:
            return Token(TT_INT, int(numContact))
        else:
            return Token(TT_FLOAT, float(numContact))

#######################################
# NODES
#######################################


class NodoNumero:
    '''
    Nodo que solo contiene un numero
    '''

    def __init__(self, token):
        self.token = token

    def __repr__(self):
        return f'{self.token.valor}'


class NodoBinario:
    '''
    Nodo que contiene <nodo izquierdo> <operador> <nodo derecho>
    '''

    def __init__(self, nodoIzquierdo, tokenOperacion, nodoDerecho, agrupacion=None):
        self.nodoIzquierdo = nodoIzquierdo
        self.tokenOperacion = tokenOperacion
        self.nodoDerecho = nodoDerecho
        self.agrupacion = agrupacion
        self.listaTokens = []
        self.crearAgrupacion()

    def crearAgrupacion(self):
        try:
            tipo = self.agrupacion.tipo
        except:
            tipo = None

        if (tipo in [TT_LPAREN, None]):
            self.listaTokens = [Token(
                TT_LPAREN), self.nodoIzquierdo, self.tokenOperacion, self.nodoDerecho, Token(TT_RPAREN)]

        elif (tipo == TT_LBRACKET):
            self.listaTokens = [Token(TT_LBRACKET), self.nodoIzquierdo,
                                self.tokenOperacion, self.nodoDerecho, Token(TT_RBRACKET)]

        elif (tipo == TT_LBRACES):
            self.listaTokens = [Token(TT_LBRACES), self.nodoIzquierdo,
                                self.tokenOperacion, self.nodoDerecho, Token(TT_RBRACES)]

    def __repr__(self):
        try:
            tipo = self.agrupacion.tipo
        except:
            tipo = None

        if (tipo in [TT_LPAREN, None]):
            return f"({self.nodoIzquierdo}{diccionario[self.tokenOperacion.tipo]}{self.nodoDerecho})"

        elif (tipo == TT_LBRACKET):
            return f"[{self.nodoIzquierdo}{diccionario[self.tokenOperacion.tipo]}{self.nodoDerecho}]"

        elif (tipo == TT_LBRACES):
            return f"{chr(123)}{self.nodoIzquierdo}{diccionario[self.tokenOperacion.tipo]}{self.nodoDerecho}{chr(125)}"


#######################################
# PARSER DE RESULTADOS
#######################################


class ParseResultados:
    '''
    Lleva el control de errores o avances del parser
    '''

    def __init__(self):
        self.error = None
        self.nodo = None

    def registrar(self, res):
        '''
        Registra una operacion nueva del parser,
        actualiza errores de ser necesario
        '''
        if isinstance(res, ParseResultados):
            if res.error:
                self.error = res.error
            return res.nodo
        return res

    def success(self, nodo):
        '''
        Marca como exitoso una operacion del parser
        '''
        self.nodo = nodo
        return self

    def failure(self, error):
        '''
        Marca como fallida una operacion del parser
        '''
        self.error = error
        return self

#######################################
# PARSER
#######################################


class Parser:
    '''
    Convierte una secuencia de tokens en una estructura
    de datos, crea parentesis donde sea necesario y retorna
    una cadena con los parentesis apropiados para armar el arbol
    '''

    def __init__(self, tokens):
        self.tokens = tokens
        self.tokenId = -1
        self.tokenGrupo = None
        self.avanzar()

    def avanzar(self):
        '''
        Pasamo a la siguiente posicion si no hemos
        llegado al final
        '''
        self.tokenId += 1
        if self.tokenId < len(self.tokens):
            self.tokenActual = self.tokens[self.tokenId]
        return self.tokenActual

    def explorar(self):
        '''
        retorna el siguiente token si no ha llegado al final
        '''
        if self.tokenId < len(self.tokens):
            return self.tokens[self.tokenId]
        return None

    def parse(self):
        res = self.expr()
        if not res.error and self.tokenActual.tipo != TT_EOF:
            if (isinstance(res.nodo, NodoBinario) and self.explorar().tipo == TT_INT):
                res.success(NodoBinario(
                    res.nodo, Token(TT_CONCAT), NodoNumero(self.explorar())))
                return res
            print(f'AQUII {res.nodo}')
            print(f'AQUII2 {self.tokenActual}')

            return res.failure(InvalidSyntaxError("Expected '+', '-', '*' or '/'"))
        return res

    def factor(self):
        '''
        factor : INT | FLOAT
        '''
        res = ParseResultados()
        token = self.tokenActual

        if token.tipo in (TT_INT, TT_FLOAT):
            res.registrar(self.avanzar())
            return res.success(NodoNumero(token))

        elif token.tipo in [TT_LPAREN, TT_LBRACKET, TT_LBRACES]:
            self.tokenGrupo = token
            res.registrar(self.avanzar())
            expr = res.registrar(self.expr())
            if res.error:
                return res
            if self.tokenActual.tipo in [TT_RPAREN, TT_RBRACKET, TT_RBRACES]:
                res.registrar(self.avanzar())
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(
                    "Expected ')'"
                ))

        return res.failure(InvalidSyntaxError(
            "Expected int or float"
        ))

    def term(self):
        '''
        term : factor ((MUL | DIV) factor)*
        '''
        return self.bin_op(self.factor, (TT_MUL, TT_DIV, TT_CONCAT))

    def expr(self):
        '''
        expr : term ((PLUS | MINUS) term)*
        '''
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS, TT_OR))

    def bin_op(self, func, ops):
        '''
        Codigo de term y expr
        Como se parecen tanto, se deja dinamico la funcion
        y los operadores que tienen que interpretar
        '''
        res = ParseResultados()
        left = res.registrar(func())

        if res.error:
            return res

        while self.tokenActual.tipo in ops:
            tokenOperacion = self.tokenActual
            res.registrar(self.avanzar())
            right = res.registrar(func())
            if res.error:
                return res
            print(f"""
			NODO BINARIO con {self.tokenGrupo}
			LEFT {left}
			RIGHT {right}""")
            left = NodoBinario(left, tokenOperacion, right, self.tokenGrupo)

        return res.success(left)

#######################################
# RUN
#######################################


def getSubListaNodes(root):
    listaSubNodos = []

    if(isinstance(root, NodoBinario)):
        for j in root.listaTokens:
            if(isinstance(j, NodoBinario)):
                listaSubNodos += getSubListaNodes(j)
            else:
                listaSubNodos.append(j)

    return listaSubNodos


def getListNodes(root):
    '''
    self.nodoIzquierdo = nodoIzquierdo
                                                                                                                                    self.tokenOperacion = tokenOperacion
                                                                                                                                    self.nodoDerecho = nodoDerecho
    '''
    listaNodos = []
    if isinstance(root, NodoBinario):
        for i in root.listaTokens:
            if(isinstance(i, NodoBinario)):
                listaNodos += getSubListaNodes(i)
            else:
                listaNodos.append(i)
    else:
        print(root)

    print(listaNodos)


def run(textoPlano):
    '''
    Metodo principal que llama al lexer y al parser
    '''

    lexer = Lexer(textoPlano)
    tokens, error = lexer.crearTokens()
    # print(f'\nTOKENS \n {tokens}\n')
    if error:
        return None, error

    parser = Parser(tokens)
    ast = parser.parse()

    getListNodes(ast.nodo)

    return ast.nodo, ast.error
