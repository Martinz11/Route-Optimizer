# ---------------------------------------------------------------------------
# Semaforo.py
# Define os semáforos fixos do sistema de otimização de trânsito.
# Importado por BuscaP.py e interface.py.
# ---------------------------------------------------------------------------

# 15 nós com semáforo, espalhados por todas as regiões do mapa
SEMAFOROS_FIXOS = [
    "BAIA_MARE",        # Noroeste
    "BISTRITA",         # Centro-Norte
    "BRASOV",           # Centro
    "CONSTANTA",        # Litoral
    "CRAIOVA",          # Sul-Oeste
    "HIRSOVA",          # Leste
    "MEHADIA",          # Oeste
    "ORADEA",           # Noroeste
    "PITESTI",          # Centro-Sul
    "RIMINCUVILCEA",    # Centro-Sul
    "SIBIU",            # Centro
    "TARGU_MURES",      # Centro-Norte
    "TIMISOARA",        # Oeste
    "URZICENI",         # Leste
    "VASLUI",           # Nordeste
]

# Custo de espera ao passar por um semáforo vermelho (segundos)
ESPERA_VERMELHO = 15.0


class Semaforo:
    """
    Representa o estado fixo de um semáforo em um nó do grafo.
    Primeira metade da lista SEMAFOROS_FIXOS = verde (sem espera).
    Segunda metade = vermelho (espera de ESPERA_VERMELHO segundos).
    """

    def __init__(self, no, verde=True):
        self.no    = no
        self.verde = verde

    def custo_esperado(self):
        """Retorna o custo de espera ao chegar neste nó."""
        return 0.0 if self.verde else ESPERA_VERMELHO


def criar_semaforos():
    """
    Instancia todos os semáforos fixos.
    Primeira metade da lista = verde, segunda metade = vermelho.
    Retorna dict {nome_no: Semaforo}.
    """
    semaforos = {}
    metade = len(SEMAFOROS_FIXOS) // 2
    for i, no in enumerate(SEMAFOROS_FIXOS):
        semaforos[no] = Semaforo(no, verde=(i < metade))
    return semaforos
