import sys
import os

from sys import argv, exit

import logging

showKey = False 
haveTPP = False
arrError = []
semTable = []

logging.basicConfig(
     level = logging.DEBUG,
     filename = "sema.log",
     filemode = "w",
     format = "%(filename)10s:%(lineno)4d:%(message)s"
)
log = logging.getLogger()


import ply.yacc as yacc

# Get the token map from the lexer.  This is required.
from tpplex import tokens

#from anytree.exporter import DotExporter, UniqueDotExporter
from mytree import MyNode
from anytree import RenderTree, AsciiStyle, PreOrderIter

from tppparser import generate_syntax_tree

from myerror import MyError
from enum import Enum

error_handler = MyError('SemaErrors')

#root = None

class PalavrasChaves(Enum):
    declaracao_funcao = "declaracao_funcao"
    declaracao_variaveis = "declaracao_variaveis"
    atribuicao = "atribuicao"
    chamada_funcao = "chamada_funcao"
    fim = "FIM"
    retorna = "retorna"
    fator = "fator"

def find_ID_and_factor(node):
    """
    Função recursiva para encontrar todos os nós com o nome especificado.

    :param node: O nó inicial a partir do qual a busca começa.
    :param name: O nome do nó que estamos buscando.
    :return: Uma lista de nós que correspondem ao nome fornecido.
    """
    found_nodes = []
    nodeAux = None

    #print(node.name)
    
    # Verifica se o nome do nó atual corresponde ao nome buscado
    if node.name == PalavrasChaves.fator.value:
        nodeAux = node.children[0]
        nodeAux = nodeAux.children[0]
        if(nodeAux.name == 'ID'):
            nodeAux = nodeAux.children[0]
            found_nodes.append(nodeAux.name)    
        else: 
            found_nodes.append(nodeAux.name)
    
    # Busca recursivamente nos filhos do nó atual
    for child in node.children:
        found_nodes.extend(find_ID_and_factor(child))
    
    return found_nodes

def creatingSemanticTable(tree):
    global haveTPP
    global showKey
    global arrError

    nodeAux = None
    type = None
    name = None
    scope = None
    data = []

    # Explora a árvore nó por nó
    for node in PreOrderIter(tree):

        # Tabela palavre chaves
        # Declaração de Variavel
        if hasattr(node, 'name') and node.name == PalavrasChaves.declaracao_variaveis.value:
            
            nodeAux = node.children[0] 
            nodeAux = nodeAux.children[0] 
            type = nodeAux.name

            nodeAux = node.children[2] 
            nodeAux = nodeAux.children[0]
            nodeAux = nodeAux.children[0]
            nodeAux = nodeAux.children[0]
            name = nodeAux.name

            semTable.append({"declaration": node.name, "type": type, "id": name, "scope": scope})

        if hasattr(node, 'name') and node.name == PalavrasChaves.fim.value:
            scope = None

        # Declaração de Função
        if hasattr(node, 'name') and node.name == PalavrasChaves.declaracao_funcao.value:
            
            nodeAux = node.children[0] 
            nodeAux = nodeAux.children[0] 
            type = nodeAux.name

            nodeAux = node.children[1] 
            nodeAux = nodeAux.children[0]
            nodeAux = nodeAux.children[0]
            name = nodeAux.name

            
            #print(f"nodeAux = {nodeAux.name}")
            #TODO: Verificar quantos parametros ela tem
            semTable.append({"declaration": node.name, "type": type, "id": name, "scope": scope})
            scope = name

        # Atribuição
        if hasattr(node, 'name') and node.name == PalavrasChaves.atribuicao.value:
            
            nodeAux = node.children[0] 
            nodeAux = nodeAux.children[0] 
            nodeAux = nodeAux.children[0] 
            name = nodeAux.name

            #print(f"nodeAux = {nodeAux.name}")
            #TODO: provavelmente verificar se vai ter mais IDS na atribuição
            #TODO: Se for um valor, verificar o tipo dele
            semTable.append({"declaration": node.name, "type": '-', "id": name, "scope": scope}) 
        
        # Chamada de Função
        if hasattr(node, 'name') and node.name == PalavrasChaves.chamada_funcao.value:
            
            nodeAux = node.children[0] 
            nodeAux = nodeAux.children[0] 
            name = nodeAux.name

            nodeAux = node.children[2] 
            data = find_ID_and_factor(nodeAux)
            
            #print(f"nodeAux = {nodeAux.name}")
            semTable.append({"declaration": node.name, "type": '-', "id": name, "scope": scope, "data": data}) 

        if hasattr(node, 'name') and node.name == PalavrasChaves.retorna.value:

            if len(node.children) > 2:
                nodeAux = node.children[2]
                data = find_ID_and_factor(nodeAux)

                semTable.append({"declaration": node.name, "type": '-', "id": name, "scope": scope, "data": data}) 

    print(semTable)
    if len(arrError) > 0:
        raise IOError(arrError)

        
    

def semanticMain(args):
    global haveTPP
    global showKey
    global arrError

    for i in range(len(args)):
        aux = args[i].split('.')
        if aux[-1] == 'tpp':
            haveTPP = True
            locationTTP = i 
        if(args[i] == '-k'):
            showKey = True

    try:
        if(len(args) < 3 and showKey == True):
            arrError.append(error_handler.newError(showKey,'ERR-SEM-USE'))
            raise IOError(arrError)
        if haveTPP == False:
            arrError.append(error_handler.newError(showKey,'ERR-SEM-NOT-TPP'))
            raise IOError(arrError)
        elif not os.path.exists(args[locationTTP]):
            arrError.append(error_handler.newError(showKey,'ERR-SEM-FILE-NOT-EXISTS'))
            raise IOError(arrError)
        else:
            tree = generate_syntax_tree(args)         

            #print(tree)        
            #print(RenderTree(tree, style=AsciiStyle()).by_attr())
            #for pre, fill, node in RenderTree(root):
            #    print("%s%s" % (pre, node.name))

            creatingSemanticTable(tree)
            

            

    except Exception as e:
        if(showKey):
            for i in range(len(e.args[0])):
                print(e.args[0][i])
        else:
            for i in range(len(e.args[0])):
                print(e.args[0][i])

# Programa Principal.
if __name__ == "__main__":
    semanticMain(sys.argv)