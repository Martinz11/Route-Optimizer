from BuscaNP import buscaNP
import F_auxiliares as fa
from os import system

while(True):
    """system("cls")
    print("**** TIPO DE EXECUÇÃO ****\n")
    print("1. GRAFO")
    print("2. GRID")
    input("Sua opção: ")"""
    

    #---------------- Executa Grafo -----------------------------
    arquivo = "Romenia_Sem_Pesos.txt"
    nos, grafo = fa.Gera_Problema_Grafo(arquivo)
    #print("======== Lista de nós ========\n",nos)
    print("\n======== Lista de Adjacência ========\n",grafo)
    origem  = input("\nOrigem......: ").upper()
    destino = input("Destino.....: ").upper()
    flag_origem  = origem in nos
    flag_destino = destino in nos
    flag = flag_origem and flag_destino
    flag_grafo = True
        #------------------------------------------------------------

    if flag:
        sol = buscaNP()
        caminho = []
        # AMPLITUDE
        if flag_grafo:
            caminho = sol.amplitude_grafo(origem,destino,nos,grafo)

        if caminho!=None:
            fa.imprimeCaminho("AMPLITUDE", caminho, len(caminho))
        else:
            print("AMPLITUDE/nCAMINHO NÃO ENCONTRADO")
        
        # PROFUNDIDADE
        caminho = []
        if flag_grafo:
            caminho = sol.profundidade_grafo(origem,destino,nos,grafo)

        print("\n*****PROFUNDIDADE*****")
        if caminho!=None:
            fa.imprimeCaminho("PROFUNIDADE", caminho, len(caminho))
        else:
            print("PROFUNDIDADE/nCAMINHO NÃO ENCONTRADO")    
    else:
        print("Estados inválidos!")
    op2 = input("\nDeseja continuar (S/N)?").upper()
    if op2=='N':
        break
    system("cls") 
