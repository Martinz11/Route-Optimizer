# ---------------------------------------------------------------------------
# BuscaP.py
# Algoritmos de busca com custo (grafo ponderado).
# Métodos originais do professor + greedy, aia_estrela,
# menor_tempo e menos_semaforos adicionados para o trabalho de trânsito.
# ---------------------------------------------------------------------------

from collections import deque
from NodeP import NodeP


# Heurística: distâncias aéreas (km) até Bucareste
HEURISTICA = {
    "ARAD": 366,        "BUCARESTE": 0,      "CRAIOVA": 160,
    "DOBRETA": 242,     "EFORIE": 161,       "FAGARAS": 176,
    "GIURGIU": 77,      "HIRSOVA": 151,      "IASI": 226,
    "LUGOJ": 244,       "MEHADIA": 241,      "NEAMT": 234,
    "ORADEA": 380,      "PITESTI": 100,      "RIMINCUVILCEA": 193,
    "SIBIU": 253,       "TIMISOARA": 329,    "URZICENI": 80,
    "VASLUI": 199,      "ZERIND": 374,
    "BRASOV": 149,      "ALBA_IULIA": 222,   "TARGU_MURES": 201,
    "SATU_MARE": 407,   "BAIA_MARE": 381,    "BISTRITA": 320,
    "CONSTANTA": 245,   "GALATI": 120,       "BRAILA": 101,
    "TULCEA": 185,
}


class busca(object):

    # ── Utilitários ───────────────────────────────────────────────────────────

    def sucessores_grafo(self, ind, grafo, ordem):
        return grafo[ind][::ordem]

    def inserir_ordenado(self, lista, no):
        for i, n in enumerate(lista):
            if no.v1 < n.v1:
                lista.insert(i, no)
                break
        else:
            lista.append(no)

    def exibirCaminho(self, node):
        caminho = []
        while node is not None:
            caminho.append(node.estado)
            node = node.pai
        return caminho[::-1]

    def heuristica_grafo(self, nos, n, destino):
        """Distância aérea até Bucareste (heurística admissível)."""
        return HEURISTICA.get(n.upper(), 0)

    # ── Custo Uniforme ────────────────────────────────────────────────────────

    def custo_uniforme(self, inicio, fim, nos, grafo):
        if inicio == fim: return [inicio], 0
        lista    = deque([NodeP(None, inicio, 0, v2=0)])
        visitado = {inicio: lista[0]}
        while lista:
            atual = lista.popleft()
            if atual.estado == fim:
                return self.exibirCaminho(atual), atual.v2
            ind = nos.index(atual.estado)
            for novo, custo_aresta in self.sucessores_grafo(ind, grafo, 1):
                v2_novo = atual.v2 + int(custo_aresta)
                if novo not in visitado or v2_novo < visitado[novo].v2:
                    filho = NodeP(atual, novo, v1=v2_novo, v2=v2_novo)
                    visitado[novo] = filho
                    self.inserir_ordenado(lista, filho)
        return None, 0

    # ── A* ────────────────────────────────────────────────────────────────────

    def a_estrela(self, inicio, fim, nos, grafo):
        if inicio == fim: return [inicio], 0
        lista    = deque([NodeP(None, inicio, 0, v2=0)])
        visitado = {inicio: lista[0]}
        while lista:
            atual = lista.popleft()
            if atual.estado == fim:
                return self.exibirCaminho(atual), atual.v2
            ind = nos.index(atual.estado)
            for novo, custo_aresta in self.sucessores_grafo(ind, grafo, 1):
                v2_novo = atual.v2 + int(custo_aresta)
                v1_novo = v2_novo + self.heuristica_grafo(nos, novo, fim)
                if novo not in visitado or v2_novo < visitado[novo].v2:
                    filho = NodeP(atual, novo, v1=v1_novo, v2=v2_novo)
                    visitado[novo] = filho
                    self.inserir_ordenado(lista, filho)
        return None, 0

    # ── Greedy ────────────────────────────────────────────────────────────────

    def greedy(self, inicio, fim, nos, grafo):
        """Expande sempre o nó com menor heurística."""
        if inicio == fim: return [inicio], 0
        h0    = self.heuristica_grafo(nos, inicio, fim)
        lista = deque([NodeP(None, inicio, v1=h0, v2=0)])
        visitado = {inicio: lista[0]}
        while lista:
            atual = lista.popleft()
            if atual.estado == fim:
                return self.exibirCaminho(atual), atual.v2
            ind = nos.index(atual.estado)
            for novo, custo_aresta in self.sucessores_grafo(ind, grafo, 1):
                if novo not in visitado:
                    h     = self.heuristica_grafo(nos, novo, fim)
                    filho = NodeP(atual, novo, v1=h, v2=atual.v2 + int(custo_aresta))
                    visitado[novo] = filho
                    self.inserir_ordenado(lista, filho)
        return None, 0

    # ── AIA* ──────────────────────────────────────────────────────────────────

    def aia_estrela(self, inicio, fim, nos, grafo):
        """A* com poda de memória (beam=7)."""
        if inicio == fim: return [inicio], 0
        h0    = self.heuristica_grafo(nos, inicio, fim)
        lista = deque([NodeP(None, inicio, v1=h0, v2=0)])
        visitado = {inicio: lista[0]}
        while lista:
            atual = lista.popleft()
            if atual.estado == fim:
                return self.exibirCaminho(atual), atual.v2
            ind = nos.index(atual.estado)
            for novo, custo_aresta in self.sucessores_grafo(ind, grafo, 1):
                v2_novo = atual.v2 + int(custo_aresta)
                v1_novo = v2_novo + self.heuristica_grafo(nos, novo, fim)
                if novo not in visitado or v2_novo < visitado[novo].v2:
                    filho = NodeP(atual, novo, v1=v1_novo, v2=v2_novo)
                    visitado[novo] = filho
                    self.inserir_ordenado(lista, filho)
            if len(lista) > 7:
                lista = deque(list(lista)[:7])
        return None, 0

    # ── Menor Tempo ───────────────────────────────────────────────────────────

    def menor_tempo(self, inicio, fim, nos, grafo, semaforos):
        """
        A* com custo = distancia + espera nos semaforos vermelhos.
        semaforos: dict {nome_no: Semaforo}
        Retorna: (caminho, custo_total, qtd_semaforos_no_caminho)
        """
        if inicio == fim: return [inicio], 0, 0
        node0 = NodeP(None, inicio, v1=self.heuristica_grafo(nos, inicio, fim), v2=0)
        node0.sem_count = 0
        lista    = deque([node0])
        visitado = {inicio: node0}
        while lista:
            atual = lista.popleft()
            if atual.estado == fim:
                return self.exibirCaminho(atual), atual.v2, atual.sem_count
            ind = nos.index(atual.estado)
            for novo, custo_aresta in self.sucessores_grafo(ind, grafo, 1):
                espera  = semaforos[novo].custo_esperado() if novo in semaforos else 0
                v2_novo = atual.v2 + int(custo_aresta) + espera
                v1_novo = v2_novo + self.heuristica_grafo(nos, novo, fim)
                sc_novo = atual.sem_count + (1 if novo in semaforos else 0)
                if novo not in visitado or v2_novo < visitado[novo].v2:
                    filho = NodeP(atual, novo, v1=v1_novo, v2=v2_novo)
                    filho.sem_count = sc_novo
                    visitado[novo]  = filho
                    self.inserir_ordenado(lista, filho)
        return None, 0, 0

    # ── Menos Semáforos ───────────────────────────────────────────────────────

    def menos_semaforos(self, inicio, fim, nos, grafo, semaforos):
        """
        A* que minimiza o numero de semaforos no caminho.
        Desempate por menor distancia.
        Retorna: (caminho, distancia_total, qtd_semaforos_no_caminho)
        """
        if inicio == fim: return [inicio], 0, 0
        node0 = NodeP(None, inicio, v1=0, v2=0)
        node0.sem_count = 0
        lista    = deque([node0])
        visitado = {inicio: node0}
        while lista:
            atual = lista.popleft()
            if atual.estado == fim:
                return self.exibirCaminho(atual), atual.v2, atual.sem_count
            ind = nos.index(atual.estado)
            for novo, custo_aresta in self.sucessores_grafo(ind, grafo, 1):
                sc_novo = atual.sem_count + (1 if novo in semaforos else 0)
                v2_novo = atual.v2 + int(custo_aresta)
                v1_novo = sc_novo * 10000 + v2_novo
                if novo not in visitado or sc_novo < visitado[novo].sem_count:
                    filho = NodeP(atual, novo, v1=v1_novo, v2=v2_novo)
                    filho.sem_count = sc_novo
                    visitado[novo]  = filho
                    self.inserir_ordenado(lista, filho)
        return None, 0, 0
