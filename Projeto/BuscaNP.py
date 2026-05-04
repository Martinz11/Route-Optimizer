from collections import deque
from Node import Node


class buscaNP(object):
    def sucessores_grafo(self, ind, grafo, ordem):
        return grafo[ind][::ordem]

    def exibirCaminho(self, node):
        caminho = []
        while node is not None:
            caminho.append(node.estado)
            node = node.pai
        caminho.reverse()
        return caminho

    def exibirCaminho_bid(self, encontro, visitado1, visitado2):
        encontro1 = visitado1[encontro]
        encontro2 = visitado2[encontro]
        caminho1 = self.exibirCaminho(encontro1)
        caminho2 = self.exibirCaminho(encontro2)
        return caminho1 + list(reversed(caminho2[:-1]))

    def amplitude_grafo(self, inicio, fim, nos, grafo):
        if inicio == fim: return [inicio]
        fila = deque([Node(None, inicio, 0)])
        visitado = {inicio: fila[0]}

        while fila:
            atual = fila.popleft()
            ind = nos.index(atual.estado)
            for novo in self.sucessores_grafo(ind, grafo, 1):
                if novo not in visitado:
                    filho = Node(atual, novo, atual.v1 + 1)
                    fila.append(filho)
                    visitado[novo] = filho
                    if novo == fim: return self.exibirCaminho(filho)
        return None

    def profundidade_grafo(self, inicio, fim, nos, grafo):
        if inicio == fim: return [inicio]
        pilha = deque([Node(None, inicio, 0)])
        visitado = {inicio: pilha[0]}

        while pilha:
            atual = pilha.pop()
            ind = nos.index(atual.estado)
            for novo in self.sucessores_grafo(ind, grafo, -1):
                if novo not in visitado:
                    filho = Node(atual, novo, atual.v1 + 1)
                    pilha.append(filho)
                    visitado[novo] = filho
                    if novo == fim: return self.exibirCaminho(filho)
        return None

    def prof_limitada_grafo(self, inicio, fim, nos, grafo, lim):
        if inicio == fim: return [inicio]
        pilha = deque([Node(None, inicio, 0)])
        visitado = {inicio: pilha[0]}

        while pilha:
            atual = pilha.pop()
            if atual.v1 < lim:
                ind = nos.index(atual.estado)
                for novo in self.sucessores_grafo(ind, grafo, -1):
                    if novo not in visitado:
                        filho = Node(atual, novo, atual.v1 + 1)
                        pilha.append(filho)
                        visitado[novo] = filho
                        if novo == fim: return self.exibirCaminho(filho)
        return None

    def aprof_iterativo_grafo(self, inicio, fim, nos, grafo, lim_max):
        for lim in range(1, lim_max):
            res = self.prof_limitada_grafo(inicio, fim, nos, grafo, lim)
            if res: return res
        return None

    def bidirecional_grafo(self, inicio, fim, nos, grafo):
        if inicio == fim: return [inicio]
        f1, f2 = deque([Node(None, inicio, 0)]), deque([Node(None, fim, 0)])
        v1, v2 = {inicio: f1[0]}, {fim: f2[0]}

        while f1 and f2:
            # Expansão Fronteira 1
            for _ in range(len(f1)):
                atual = f1.popleft()
                ind = nos.index(atual.estado)
                for novo in self.sucessores_grafo(ind, grafo, 1):
                    if novo not in v1:
                        filho = Node(atual, novo, atual.v1 + 1)
                        v1[novo] = filho
                        f1.append(filho)
                        if novo in v2: return self.exibirCaminho_bid(novo, v1, v2)
            # Expansão Fronteira 2
            for _ in range(len(f2)):
                atual = f2.popleft()
                ind = nos.index(atual.estado)
                for novo in self.sucessores_grafo(ind, grafo, 1):
                    if novo not in v2:
                        filho = Node(atual, novo, atual.v1 + 1)
                        v2[novo] = filho
                        f2.append(filho)
                        if novo in v1: return self.exibirCaminho_bid(novo, v1, v2)
        return None