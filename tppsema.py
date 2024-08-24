import sys
import os

from sys import argv, exit

import logging

showKey = False 
haveTPP = False
arrError = []

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

from mytree import MyNode
from anytree.exporter import DotExporter, UniqueDotExporter
from anytree import RenderTree, AsciiStyle
from tppparser import generate_syntax_tree

from myerror import MyError

error_handler = MyError('SemaErrors')

#root = None

def find_function(node, function_name):
    # Verifica se o nó atual é None
    if node is None:
        print("Node is None.")
        return None

    # Verifica se o nó atual tem filhos
    if not hasattr(node, 'children'):
        print(f"Node '{node}' does not have children attribute.")
        return None

    # Verifica se o nó atual representa uma função com o nome 'principal'
    if hasattr(node, 'name') and node.name == function_name:
        return node
    
    # Percorre os filhos do nó atual
    for child in node.children:
        result = find_function(child, function_name)
        if result:
            return result
    
    return None


def findingSemanticErrors(tree):
    global haveTPP
    global showKey
    global arrError

    if(find_function(tree, 'principal') == None):
        arrError.append(error_handler.newError(showKey,'ERR-SEM-MAIN-NOT-DECL'))
    
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

            findingSemanticErrors(tree)
            

            

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