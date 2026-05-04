import numpy as np  
import random as rd
#-----------------------------------------------------------------------------
# IMPORTA O GRAFO DE ARQUIVO TEXTO
#-----------------------------------------------------------------------------
def Gera_Problema_Grafo(arquivo):
    f = open(arquivo,"r",encoding="utf-8")
    
    nos = []
    grafo = []
    for str1 in f:
        str1 = str1.strip("\n")
        str1 = str1.split(",")
        nos.append(str1[0])
        grafo.append(str1[1:])
    
    return nos, grafo
#-----------------------------------------------------------------------------
# IMPORTA O GRAFO DE ARQUIVO TEXTO
#-----------------------------------------------------------------------------
def Gera_Problema_Grafo_Ale(n,m):
    
    grafo = []
    nos = []
    for i in range(n):
        nos.append(i)
        tam = rd.randint(5,m)
        linha = []
        for j in range(tam):
            x = rd.randrange(n)
            if x not in linha:
                linha.append(x)
        grafo.append(linha)
    return nos, grafo

#-----------------------------------------------------------------------------

def imprimeCaminho(texto,caminho,custo):
    print("\n",texto)
    print("Caminho: ",caminho)
    print("Custo..: ",len(caminho)-1)
