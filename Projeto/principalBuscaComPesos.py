from BuscaP import busca


# --------------------------------------------------------------------------
# IMPORTA DADOS DO ARQUIVO
# --------------------------------------------------------------------------
def Gerar_Problema_Grafo(arq):
    grafo = []
    nos = []
    with open(arq, "r") as f:
        for dados in f:
            dados = dados.strip()
            dados = dados.split(",")
            nos.append(dados[0])
            aux1 = []
            for i in range(1, len(dados), 2):
                aux = []
                aux.append(dados[i])
                aux.append(int(dados[i + 1]))
                aux1.append(aux)
            grafo.append(aux1)

    return nos, grafo


# --------------------------------------------------------------------------
# MÓDULO PRINCIPAL
# --------------------------------------------------------------------------

# Execução - Grafo
nos, grafo = Gerar_Problema_Grafo("Romenia_Com_Pesos.txt")
inicio = "arad"
# Alterado 'iasa' para 'iasi' para corresponder ao arquivo txt
final = ["bucareste", "sibiu", "mehadia", "urziceni", "hirsova", "iasi", "dobreta"]
inicio = inicio.upper()
for i in range(len(final)):
    final[i] = final[i].upper()

# Executa buscas
sol = busca()

# Adicionado laço para testar cada destino da lista individualmente
for destino in final:
    print(f"\n\n*** ROTAS PARA: {destino} ***")

    caminho, custo = sol.custo_uniforme(inicio, destino, nos, grafo)
    print("\n===> Custo Uniforme")
    if caminho != None:
        print("Caminho: ", caminho)
        print("Custo: ", custo)
    else:
        print("Caminho não encontrado")

    caminho, custo = sol.a_estrela(inicio, destino, nos, grafo)
    print("\n===> A Estrela")
    if caminho != None:
        print("Caminho: ", caminho[::-1])
        print("Custo: ", custo)
    else:
        print("Caminho não encontrado")