# ---------------------------------------------------------------------------
# interface.py
# Interface gráfica — Otimização de Trânsito com Semáforos.
# Responsabilidade exclusiva: UI (janela, painel, canvas, eventos).
# Toda lógica de busca está em BuscaP.py / BuscaNP.py.
# Toda lógica de semáforos está em Semaforo.py.
# ---------------------------------------------------------------------------

import tkinter as tk
from tkinter import ttk, font as tkfont
import math, sys, os

sys.path.insert(0, os.path.dirname(__file__))

from BuscaP  import busca  as BuscaP
from BuscaNP import buscaNP
from Semaforo import criar_semaforos, SEMAFOROS_FIXOS


# ── Posições geográficas dos 30 nós no canvas ─────────────────────────────────
_POS = {
    "SATU_MARE":    ( 95,  30), "BAIA_MARE":    (165,  40),
    "ORADEA":       (130,  70), "BISTRITA":     (295,  75),
    "ZERIND":       ( 85, 145), "ALBA_IULIA":   (225, 195),
    "TARGU_MURES":  (325, 155), "NEAMT":        (535,  90),
    "ARAD":         ( 55, 225), "SIBIU":        (295, 275),
    "BRASOV":       (395, 290), "IASI":         (620, 105),
    "TIMISOARA":    ( 80, 315), "FAGARAS":      (405, 230),
    "VASLUI":       (650, 175), "LUGOJ":        (170, 350),
    "RIMINCUVILCEA":(355, 395), "PITESTI":      (430, 390),
    "GALATI":       (680, 265), "MEHADIA":      (215, 415),
    "BUCARESTE":    (530, 355), "URZICENI":     (590, 290),
    "BRAILA":       (660, 320), "DOBRETA":      (185, 490),
    "CRAIOVA":      (265, 500), "GIURGIU":      (495, 440),
    "HIRSOVA":      (700, 365), "TULCEA":       (740, 310),
    "CONSTANTA":    (750, 435), "EFORIE":       (760, 490),
}

# ── Paleta de cores ───────────────────────────────────────────────────────────
C = dict(
    bg          = "#07090f",
    painel_bg   = "#0c1018",
    painel_brd  = "#1e2535",
    card_bg     = "#111827",
    card_brd    = "#1f2d45",
    txt_h       = "#e2e8f0",
    txt_b       = "#94a3b8",
    txt_dim     = "#475569",
    accent      = "#38bdf8",
    accent2     = "#818cf8",
    aresta      = "#1e2d42",
    aresta_bg   = "#0f1929",
    no_bg       = "#0f1929",
    no_brd      = "#1e3a5f",
    no_txt      = "#7dd3fc",
    r1_line     = "#38bdf8",
    r1_no_bg    = "#0c2340",
    r1_no_bd    = "#38bdf8",
    r2_line     = "#4ade80",
    r2_no_bg    = "#0f2a1a",
    r2_no_bd    = "#4ade80",
    sem_verde   = "#22c55e",
    sem_verm    = "#ef4444",
    sem_bg      = "#1c1c1c",
    ini_bg      = "#1a1240", ini_bd = "#818cf8",
    fim_bg      = "#1a2e1a", fim_bd = "#4ade80",
    peso_txt    = "#2a3a4a",
    btn         = "#1d4ed8", btn_hov = "#2563eb", btn_txt = "#e0f2fe",
    ok          = "#4ade80", err = "#f87171",
)


# ── Carregamento dos grafos ───────────────────────────────────────────────────
def _carregar_com_pesos(arq):
    """Lê Romenia_Com_Pesos.txt e devolve nos, grafo, arestas_para_desenho."""
    nos, grafo, arestas = [], [], []
    with open(arq) as f:
        for linha in f:
            p = linha.strip().split(",")
            no = p[0].upper()
            nos.append(no)
            adj = []
            for i in range(1, len(p), 2):
                viz  = p[i].upper()
                peso = int(p[i + 1])
                adj.append([viz, peso])
                par = tuple(sorted([no, viz]))
                if (par[0], par[1], peso) not in arestas:
                    arestas.append((par[0], par[1], peso))
            grafo.append(adj)
    return nos, grafo, arestas


def _carregar_sem_pesos(arq):
    """Lê Romenia_Sem_Pesos.txt e devolve nos, grafo."""
    nos, grafo = [], []
    with open(arq) as f:
        for linha in f:
            p = linha.strip().split(",")
            nos.append(p[0].upper())
            grafo.append([x.upper() for x in p[1:]])
    return nos, grafo


# ── Aplicação principal ───────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Otimização de Trânsito — Eng. Computação")
        self.configure(bg=C["bg"])
        self.geometry("1420x780")
        self.minsize(1100, 640)

        base = os.path.dirname(__file__)
        self._nos_p, self._grafo_p, self._arestas = _carregar_com_pesos(
            os.path.join(base, "Romenia_Com_Pesos.txt"))
        self._nos_np, self._grafo_np = _carregar_sem_pesos(
            os.path.join(base, "Romenia_Sem_Pesos.txt"))

        # Semáforos criados por Semaforo.py
        self._semaforos = criar_semaforos()
        self._sem_ativo = True

        # Resultados das rotas
        self._rota1: list = []
        self._rota2: list = []
        self._custo1 = self._custo2 = 0
        self._sem1   = self._sem2   = 0

        self._build_ui()
        self._redraw()

    # ── Eventos de semáforo ───────────────────────────────────────────────────
    def _toggle_semaforos(self):
        self._sem_ativo = not self._sem_ativo
        estado = "LIGADO"    if self._sem_ativo else "DESLIGADO"
        cor    = C["sem_verde"] if self._sem_ativo else C["sem_verm"]
        self._btn_sem_lbl.config(text=f"◉  SEMÁFOROS: {estado}", bg=cor)
        self._redraw()

    # ── Construção da UI ──────────────────────────────────────────────────────
    def _build_ui(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self._build_panel()
        self._build_canvas()
        self._build_styles()

    def _build_panel(self):
        outer = tk.Frame(self, bg=C["painel_brd"], width=315)
        outer.grid(row=0, column=0, sticky="nsew", padx=(10, 0), pady=10)
        outer.grid_propagate(False)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(0, weight=1)

        pnl = tk.Frame(outer, bg=C["painel_bg"])
        pnl.grid(row=0, column=0, sticky="nsew", padx=(0, 1))

        # Cabeçalho
        hdr = tk.Frame(pnl, bg=C["card_bg"])
        hdr.pack(fill="x")
        tk.Canvas(hdr, bg=C["accent"], height=3, highlightthickness=0).pack(fill="x")
        tk.Label(hdr, text="ROUTE OPTIMIZER",
                 bg=C["card_bg"], fg=C["accent"],
                 font=tkfont.Font(family="Courier", size=13, weight="bold")
                 ).pack(anchor="w", padx=16, pady=(14, 0))
        tk.Label(hdr, text="Eng. Computação  ·  IA Aplicada",
                 bg=C["card_bg"], fg=C["txt_dim"],
                 font=tkfont.Font(family="Courier", size=8)
                 ).pack(anchor="w", padx=16, pady=(0, 12))

        # 01 Método
        self._section(pnl, "01  MÉTODO DE BUSCA")
        self._metodo = tk.StringVar(value="A*")
        self._combo(pnl, self._metodo,
                    ["A*", "Greedy", "Custo Uniforme", "AIA*",
                     "Amplitude", "Profundidade",
                     "Prof. Limitada", "Aprofundamento Iterativo", "Bidirecional"])

        # 02 Estado Inicial
        cidades = sorted(_POS.keys())
        self._section(pnl, "02  ESTADO INICIAL")
        self._ini = tk.StringVar(value="ARAD")
        self._combo(pnl, self._ini, cidades)

        # 03 Estado Objetivo
        self._section(pnl, "03  ESTADO OBJETIVO")
        self._fim_var = tk.StringVar(value="BUCARESTE")
        self._combo_fim = self._combo(pnl, self._fim_var, cidades)

        # Limite de profundidade (aparece só para Prof. Limitada / Aprofund. Iter.)
        self._frm_lim = tk.Frame(pnl, bg=C["painel_bg"])
        tk.Label(self._frm_lim, text="LIMITE DE PROFUNDIDADE",
                 bg=C["painel_bg"], fg=C["txt_dim"],
                 font=tkfont.Font(family="Courier", size=7, weight="bold")
                 ).pack(anchor="w", padx=16, pady=(8, 2))
        self._lim = tk.IntVar(value=10)
        tk.Spinbox(self._frm_lim, from_=1, to=99, textvariable=self._lim,
                   width=5, bg=C["card_bg"], fg=C["accent"],
                   buttonbackground=C["card_bg"],
                   font=tkfont.Font(family="Courier", size=10),
                   relief="flat", highlightthickness=1,
                   highlightbackground=C["card_brd"]
                   ).pack(anchor="w", padx=16, pady=(0, 4))
        self._metodo.trace_add("write", self._toggle_lim)
        self._metodo.trace_add("write", self._limpar_resultados)
        self._toggle_lim()

        # 04 Semáforos
        tk.Frame(pnl, bg=C["painel_brd"], height=1).pack(fill="x", pady=6)
        self._section(pnl, "04  SEMÁFOROS")
        sem_info = tk.Frame(pnl, bg=C["painel_bg"])
        sem_info.pack(fill="x", padx=14, pady=(0, 4))
        tk.Label(sem_info,
                 text=f"{len(SEMAFOROS_FIXOS)} nós com semáforo fixo  "
                      f"({len(SEMAFOROS_FIXOS)//2} verdes · {len(SEMAFOROS_FIXOS) - len(SEMAFOROS_FIXOS)//2} vermelhos)",
                 bg=C["painel_bg"], fg=C["txt_b"],
                 font=tkfont.Font(family="Courier", size=7)
                 ).pack(anchor="w", pady=(0, 4))

        btn_tog = tk.Frame(sem_info, bg=C["sem_verde"], cursor="hand2")
        btn_tog.pack(fill="x")
        self._btn_sem_lbl = tk.Label(btn_tog, text="◉  SEMÁFOROS: LIGADO",
                                      bg=C["sem_verde"], fg="white",
                                      font=tkfont.Font(family="Courier", size=9, weight="bold"),
                                      pady=6, cursor="hand2")
        self._btn_sem_lbl.pack(fill="x")
        btn_tog.bind("<Button-1>",           lambda _: self._toggle_semaforos())
        self._btn_sem_lbl.bind("<Button-1>", lambda _: self._toggle_semaforos())

        # Botão calcular
        tk.Frame(pnl, bg=C["painel_brd"], height=1).pack(fill="x", pady=6)
        btn_calc = tk.Frame(pnl, bg=C["btn"], cursor="hand2")
        btn_calc.pack(fill="x", padx=14, pady=(0, 8))
        btn_lbl = tk.Label(btn_calc, text="▶  CALCULAR ROTAS",
                           bg=C["btn"], fg=C["btn_txt"],
                           font=tkfont.Font(family="Courier", size=10, weight="bold"),
                           pady=10, cursor="hand2")
        btn_lbl.pack(fill="x")
        btn_calc.bind("<Button-1>", lambda _: self._run())
        btn_lbl.bind("<Button-1>",  lambda _: self._run())
        btn_calc.bind("<Enter>", lambda _: (btn_calc.config(bg=C["btn_hov"]),
                                             btn_lbl.config(bg=C["btn_hov"])))
        btn_calc.bind("<Leave>", lambda _: (btn_calc.config(bg=C["btn"]),
                                             btn_lbl.config(bg=C["btn"])))
        
        # Botão limpar
        btn_clear = tk.Frame(pnl, bg=C["txt_dim"], cursor="hand2")
        btn_clear.pack(fill="x", padx=14, pady=(0, 8))
        btn_clear_lbl = tk.Label(btn_clear, text="✕  LIMPAR",
                         bg=C["txt_dim"], fg=C["btn_txt"],
                         font=tkfont.Font(family="Courier", size=10, weight="bold"),
                         pady=6, cursor="hand2")
        btn_clear_lbl.pack(fill="x")
        btn_clear.bind("<Button-1>", lambda _: self._limpar_resultados())
        btn_clear_lbl.bind("<Button-1>", lambda _: self._limpar_resultados())
        btn_clear.bind("<Enter>", lambda _: (btn_clear.config(bg=C["txt_b"]),
                                      btn_clear_lbl.config(bg=C["txt_b"])))
        btn_clear.bind("<Leave>", lambda _: (btn_clear.config(bg=C["txt_dim"])),
                                      btn_clear_lbl.config(bg=C["txt_dim"]))


        # 05 Resultado
        tk.Frame(pnl, bg=C["painel_brd"], height=1).pack(fill="x")
        self._section(pnl, "05  RESULTADO")
        res_frame = tk.Frame(pnl, bg=C["card_bg"],
                             highlightthickness=1,
                             highlightbackground=C["card_brd"])
        res_frame.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        self._txt = tk.Text(res_frame, bg=C["card_bg"], fg=C["txt_b"],
                             font=tkfont.Font(family="Courier", size=8),
                             relief="flat", wrap="word", state="disabled",
                             padx=10, pady=8,
                             selectbackground=C["card_brd"],
                             insertbackground=C["accent"])
        self._txt.pack(fill="both", expand=True)

        # Tags de cor para o painel de resultado
        self._txt.tag_config("h",
                              foreground=C["accent"],
                              font=tkfont.Font(family="Courier", size=9, weight="bold"))
        self._txt.tag_config("r1",
                              foreground=C["r1_line"],
                              font=tkfont.Font(family="Courier", size=8, weight="bold"))
        self._txt.tag_config("r2",
                              foreground=C["r2_line"],
                              font=tkfont.Font(family="Courier", size=8, weight="bold"))
        self._txt.tag_config("ok",  foreground=C["ok"])
        self._txt.tag_config("er",  foreground=C["err"])
        self._txt.tag_config("dim", foreground=C["txt_dim"])
        self._txt.tag_config("val", foreground=C["accent2"])

    def _section(self, parent, text):
        f = tk.Frame(parent, bg=C["painel_bg"])
        f.pack(fill="x", padx=16, pady=(10, 3))
        tk.Label(f, text=text, bg=C["painel_bg"], fg=C["txt_dim"],
                 font=tkfont.Font(family="Courier", size=7, weight="bold")
                 ).pack(side="left")
        tk.Frame(f, bg=C["painel_brd"], height=1).pack(
            side="left", fill="x", expand=True, padx=(8, 0), pady=4)

    def _combo(self, parent, var, values):
        cb = ttk.Combobox(parent, textvariable=var, values=values,
                          state="readonly",
                          font=tkfont.Font(family="Courier", size=9))
        cb.pack(fill="x", padx=14, pady=(0, 2))
        return cb

    def _build_canvas(self):
        cv_frame = tk.Frame(self, bg=C["bg"])
        cv_frame.grid(row=0, column=1, sticky="nsew", padx=(4, 10), pady=10)
        cv_frame.rowconfigure(0, weight=1)
        cv_frame.columnconfigure(0, weight=1)
        self._cv = tk.Canvas(cv_frame, bg=C["bg"], highlightthickness=0)
        self._cv.grid(row=0, column=0, sticky="nsew")
        self._cv.bind("<Configure>", lambda _: self._redraw())

    def _build_styles(self):
        st = ttk.Style(self)
        st.theme_use("clam")
        st.configure("TCombobox",
                     fieldbackground=C["card_bg"], background=C["card_bg"],
                     foreground=C["txt_h"], selectbackground=C["card_brd"],
                     selectforeground=C["accent"], arrowcolor=C["accent"],
                     bordercolor=C["card_brd"], lightcolor=C["card_brd"],
                     darkcolor=C["card_brd"], padding=6)
        st.map("TCombobox",
               fieldbackground=[("readonly", C["card_bg"])],
               foreground=[("readonly", C["txt_h"])])

    def _toggle_lim(self, *_):
        if self._metodo.get() in ("Prof. Limitada", "Aprofundamento Iterativo"):
            self._frm_lim.pack(fill="x", after=self._combo_fim)
        else:
            self._frm_lim.pack_forget()

    def _limpar_resultados(self, *_):
        self._rota1  = []
        self._rota2  = []
        self._custo1 = self._custo2 = 0
        self._sem1   = self._sem2   = 0
        self._txt.config(state="normal")
        self._txt.delete("1.0", "end")
        self._txt.config(state="disabled")
        self._redraw()

    # ── Execução das buscas ───────────────────────────────────────────────────
    def _run(self):
        ini    = self._ini.get().upper()
        fim    = self._fim_var.get().upper()
        metodo = self._metodo.get()
        lim    = self._lim.get()
        sems   = self._semaforos if self._sem_ativo else {}

        if ini not in self._nos_p or fim not in self._nos_p:
            self._show_erro("Nó não encontrado no grafo."); return

        sol_p  = BuscaP()
        sol_np = buscaNP()

        # Caminho pelo método clássico escolhido
        cam_classico   = None
        custo_classico = 0

        if metodo == "A*":
            cam_classico, custo_classico = sol_p.a_estrela(
                ini, fim, self._nos_p, self._grafo_p)
        elif metodo == "Greedy":
            cam_classico, custo_classico = sol_p.greedy(
                ini, fim, self._nos_p, self._grafo_p)
        elif metodo == "Custo Uniforme":
            cam_classico, custo_classico = sol_p.custo_uniforme(
                ini, fim, self._nos_p, self._grafo_p)
        elif metodo == "AIA*":
            cam_classico, custo_classico = sol_p.aia_estrela(
                ini, fim, self._nos_p, self._grafo_p)
        elif ini in self._nos_np and fim in self._nos_np:
            if metodo == "Amplitude":
                cam_classico = sol_np.amplitude_grafo(
                    ini, fim, self._nos_np, self._grafo_np)
            elif metodo == "Profundidade":
                cam_classico = sol_np.profundidade_grafo(
                    ini, fim, self._nos_np, self._grafo_np)
            elif metodo == "Prof. Limitada":
                cam_classico = sol_np.prof_limitada_grafo(
                    ini, fim, self._nos_np, self._grafo_np, lim)
            elif metodo == "Aprofundamento Iterativo":
                cam_classico = sol_np.aprof_iterativo_grafo(
                    ini, fim, self._nos_np, self._grafo_np, lim)
            elif metodo == "Bidirecional":
                cam_classico = sol_np.bidirecional_grafo(
                    ini, fim, self._nos_np, self._grafo_np)
            if cam_classico:
                custo_classico = len(cam_classico) - 1

        # Rota 1 — Menor Tempo (sempre com grafo ponderado + semáforos)
        r1, c1, s1 = sol_p.menor_tempo(
            ini, fim, self._nos_p, self._grafo_p, sems)

        # Rota 2 — Menos Semáforos (sempre com grafo ponderado + semáforos)
        r2, c2, s2 = sol_p.menos_semaforos(
            ini, fim, self._nos_p, self._grafo_p, sems)

        if self._sem_ativo:    
            self._rota1  = [x.upper() for x in r1] if r1 else []
            self._rota2  = [x.upper() for x in r2] if r2 else []
            self._custo1 = c1;  self._sem1 = s1
            self._custo2 = c2;  self._sem2 = s2

        else:
            self._rota1  = [x.upper() for x in cam_classico] if cam_classico else []
            self._rota2  = []
            self._custo1 = custo_classico
            self._custo2 = 0
            self._sem1   = self._sem2 = 0

        self._show_resultado(ini, fim, metodo, cam_classico, custo_classico)
        self._redraw()

    # ── Exibição de resultados ────────────────────────────────────────────────
    def _show_erro(self, msg):
        t = self._txt
        t.config(state="normal")
        t.delete("1.0", "end")
        t.insert("end", "ERRO\n", "dim")
        t.insert("end", f"  {msg}\n", "er")
        t.config(state="disabled")

    def _show_resultado(self, ini, fim, metodo, cam_classico, custo_classico):
        t = self._txt
        t.config(state="normal")
        t.delete("1.0", "end")

        t.insert("end", f"  {ini}  →  {fim}\n\n", "h")

        # Caminho clássico
        t.insert("end", f"━━  {metodo.upper()}\n", "dim")
        if cam_classico:
            cam_up = [x.upper() for x in cam_classico]
            t.insert("end", self._fmt(cam_up) + "\n", "ok")
            t.insert("end", f"  Custo : {custo_classico}\n\n", "val")
        else:
            t.insert("end", "  Caminho não encontrado\n\n", "er")

        if self._sem_ativo:

        # Rota 1 — Menor Tempo
            t.insert("end", "━━  ROTA 1 — MENOR TEMPO\n", "r1")
            if self._rota1:
                t.insert("end", self._fmt(self._rota1) + "\n", "ok")
                t.insert("end", f"  Tempo total : {self._custo1:.0f}\n", "val")
                if self._sem_ativo:
                    t.insert("end", f"  Semáforos   : {self._sem1}\n\n", "val")
                else:
                    t.insert("end", "\n", "val")
            else:
                t.insert("end", "  Caminho não encontrado\n\n", "er")

        # Rota 2 — Menos Semáforos
            t.insert("end", "━━  ROTA 2 — MENOS SEMÁFOROS\n", "r2")
            if self._rota2:
                t.insert("end", self._fmt(self._rota2) + "\n", "ok")
                t.insert("end", f"  Distância   : {self._custo2} km\n", "val")
                if self._sem_ativo:
                    t.insert("end", f"  Semáforos   : {self._sem2}\n\n", "val")
                else: 
                    t.insert ("end", "\n", "val")
            else:
                t.insert("end", "  Caminho não encontrado\n\n", "er")

        # Comparativo
            if self._rota1 and self._rota2:
                t.insert("end", "─── COMPARATIVO ─────────────\n", "dim")
                if self._sem_ativo:                                           # ← adicionar
                    if self._sem1 < self._sem2:
                        t.insert("end", "  Rota 1 passa por menos semáforos\n", "r1")
                    elif self._sem2 < self._sem1:
                        t.insert("end", "  Rota 2 passa por menos semáforos\n", "r2")
                    else:
                        t.insert("end", "  Mesmo número de semáforos\n", "dim")
                if self._custo1 <= self._custo2:
                    t.insert("end", "  Rota 1 tem menor tempo total\n", "r1")
                else:
                    t.insert("end", "  Rota 2 tem menor tempo total\n", "r2")

        t.config(state="disabled")

    def _fmt(self, cam):
        """Formata caminho em linhas de ~28 chars."""
        line = "  "; lines = []
        for i, n in enumerate(cam):
            sep = " → " if i < len(cam) - 1 else ""
            if len(line) + len(n) + len(sep) > 28 and line.strip():
                lines.append(line); line = "  "
            line += n + sep
        if line.strip():
            lines.append(line)
        return "\n".join(lines)

    # ── Desenho do grafo ──────────────────────────────────────────────────────
    def _redraw(self):
        cv = self._cv
        cv.delete("all")
        W = cv.winfo_width()  or 1060
        H = cv.winfo_height() or 700

        # Grid de fundo
        for gx in range(0, W, 40):
            cv.create_line(gx, 0, gx, H, fill="#0d1520", width=1)
        for gy in range(0, H, 40):
            cv.create_line(0, gy, W, gy, fill="#0d1520", width=1)

        # Escala proporcional ao canvas
        xs = [p[0] for p in _POS.values()]
        ys = [p[1] for p in _POS.values()]
        mx, Mx = min(xs), max(xs)
        my, My = min(ys), max(ys)
        pad = 55
        s   = min((W - 2*pad) / (Mx - mx), (H - 2*pad) / (My - my))

        def Proj(n):
            x, y = _POS[n]
            return pad + (x - mx)*s, pad + (y - my)*s

        # Conjuntos de arestas por rota
        ar1 = set(); ar2 = set()
        for i in range(len(self._rota1) - 1):
            a, b = self._rota1[i], self._rota1[i+1]
            ar1.add((a, b)); ar1.add((b, a))
        for i in range(len(self._rota2) - 1):
            a, b = self._rota2[i], self._rota2[i+1]
            ar2.add((a, b)); ar2.add((b, a))

        ini = self._ini.get().upper()
        fim = self._fim_var.get().upper()
        R   = max(11, int(s * 11))

        # ── Arestas ───────────────────────────────────────────────────────────
        for a, b, w in self._arestas:
            if a not in _POS or b not in _POS:
                continue
            x1, y1 = Proj(a); x2, y2 = Proj(b)
            em1      = (a, b) in ar1
            em2      = (a, b) in ar2
            em_ambas = em1 and em2

            if em_ambas:
                cv.create_line(x1, y1, x2, y2,
                               fill="#0d3550", width=11, capstyle="round")
                cv.create_line(x1, y1, x2, y2,
                               fill=C["r1_line"], width=4,
                               capstyle="round", dash=(8, 8))
                cv.create_line(x1, y1, x2, y2,
                               fill=C["r2_line"], width=4,
                               capstyle="round", dash=(8, 8), dashoffset=8)
            elif em1:
                cv.create_line(x1, y1, x2, y2,
                               fill="#0d3550", width=9, capstyle="round")
                cv.create_line(x1, y1, x2, y2,
                               fill="#0e5e8a", width=5, capstyle="round")
                cv.create_line(x1, y1, x2, y2,
                               fill=C["r1_line"], width=2, capstyle="round")
            elif em2:
                cv.create_line(x1, y1, x2, y2,
                               fill="#0d2e1a", width=9, capstyle="round")
                cv.create_line(x1, y1, x2, y2,
                               fill="#166534", width=5, capstyle="round")
                cv.create_line(x1, y1, x2, y2,
                               fill=C["r2_line"], width=2, capstyle="round")
            else:
                cv.create_line(x1, y1, x2, y2,
                               fill=C["aresta"], width=1, dash=(4, 6))

            # Peso da aresta
            ang = math.atan2(y2 - y1, x2 - x1)
            tx  = (x1 + x2)/2 + 10*math.sin(ang)
            ty  = (y1 + y2)/2 - 10*math.cos(ang)
            cor_p = (C["r1_line"] if em1 else
                     C["r2_line"] if em2 else C["peso_txt"])
            cv.create_text(tx, ty, text=str(w),
                           font=("Courier", 6), fill=cor_p)

        # ── Setas rota 1 (posição 40%) ────────────────────────────────────────
        for i in range(len(self._rota1) - 1):
            a, b = self._rota1[i], self._rota1[i+1]
            if a not in _POS or b not in _POS: continue
            x1, y1 = Proj(a); x2, y2 = Proj(b)
            ang = math.atan2(y2 - y1, x2 - x1)
            px, py = x1*0.6 + x2*0.4, y1*0.6 + y2*0.4
            sz = 8
            pts = [px + sz*math.cos(ang),     py + sz*math.sin(ang),
                   px + sz*math.cos(ang+2.5),  py + sz*math.sin(ang+2.5),
                   px + sz*math.cos(ang-2.5),  py + sz*math.sin(ang-2.5)]
            cv.create_polygon(pts, fill=C["r1_line"], outline="")

        # ── Setas rota 2 (posição 60%) ────────────────────────────────────────
        for i in range(len(self._rota2) - 1):
            a, b = self._rota2[i], self._rota2[i+1]
            if a not in _POS or b not in _POS: continue
            x1, y1 = Proj(a); x2, y2 = Proj(b)
            ang = math.atan2(y2 - y1, x2 - x1)
            px, py = x1*0.4 + x2*0.6, y1*0.4 + y2*0.6
            sz = 8
            pts = [px + sz*math.cos(ang),     py + sz*math.sin(ang),
                   px + sz*math.cos(ang+2.5),  py + sz*math.sin(ang+2.5),
                   px + sz*math.cos(ang-2.5),  py + sz*math.sin(ang-2.5)]
            cv.create_polygon(pts, fill=C["r2_line"], outline="")

        # ── Nós ───────────────────────────────────────────────────────────────
        nos_r1 = set(self._rota1)
        nos_r2 = set(self._rota2)

        for nome in _POS:
            x, y = Proj(nome)
            is_i     = nome == ini
            is_f     = nome == fim
            em1      = nome in nos_r1
            em2      = nome in nos_r2
            em_ambas = em1 and em2

            if is_i:
                fill, brd, bw, glw = C["ini_bg"], C["ini_bd"], 2, "#2a1f6e"
            elif is_f:
                fill, brd, bw, glw = C["fim_bg"], C["fim_bd"], 2, "#1a3d1a"
            elif em_ambas:
                fill, brd, bw, glw = "#0c2225", C["r1_line"], 2, "#091a20"
            elif em1:
                fill, brd, bw, glw = C["r1_no_bg"], C["r1_no_bd"], 2, "#0a2a40"
            elif em2:
                fill, brd, bw, glw = C["r2_no_bg"], C["r2_no_bd"], 2, "#0a2010"
            else:
                fill, brd, bw, glw = C["no_bg"], C["no_brd"], 1, C["aresta_bg"]

            cv.create_oval(x-R-3, y-R-3, x+R+3, y+R+3, fill=glw, outline="")
            cv.create_oval(x-R, y-R, x+R, y+R, fill=fill, outline=brd, width=bw)

            # Semáforo (bolinha no canto superior direito do nó)
            if self._sem_ativo and nome in self._semaforos:
                sem = self._semaforos[nome]
                sr  = max(4, int(R * 0.38))
                sx  = x + R - sr + 1
                sy  = y - R + sr - 1
                cor_s = C["sem_verde"] if sem.verde else C["sem_verm"]
                cv.create_oval(sx-sr, sy-sr, sx+sr, sy+sr,
                               fill=C["sem_bg"], outline=cor_s, width=1)
                cv.create_oval(sx-sr+2, sy-sr+2, sx+sr-2, sy+sr-2,
                               fill=cor_s, outline="")

            # Rótulo do nó
            lbl = nome.replace("_", " ")
            lbl = lbl[:6] if len(lbl) > 8 else lbl
            fz  = max(5, min(7, int(R * 0.50)))
            cv.create_text(x+1, y+1, text=lbl, fill="#000000",
                           font=("Courier", fz, "bold"))
            cor_txt = (C["ini_bd"] if is_i else
                       C["fim_bd"] if is_f else
                       C["r1_line"] if em1 else
                       C["r2_line"] if em2 else C["no_txt"])
            cv.create_text(x, y, text=lbl, fill=cor_txt,
                           font=("Courier", fz, "bold"))

        # ── Título ────────────────────────────────────────────────────────────
        cv.create_text(W//2, 16,
                       text="MAPA RODOVIÁRIO — ROMÊNIA  (30 cidades)",
                       fill=C["txt_dim"], font=("Courier", 9, "bold"), anchor="n")

        # ── Legenda ───────────────────────────────────────────────────────────
        lx, ly = 10, H - 152
        itens = [
            (C["r1_line"],  "━━  Rota 1 — Menor Tempo"),
            (C["r2_line"],  "━━  Rota 2 — Menos Semáforos"),
            (C["aresta"],   "╌╌  Via disponível"),
            (C["ini_bd"],   "◉   Estado inicial"),
            (C["fim_bd"],   "◉   Estado objetivo"),
            (C["sem_verde"],"●   Semáforo verde"),
            (C["sem_verm"], "●   Semáforo vermelho"),
        ]
        bw2 = 200; bh = len(itens)*17 + 18
        cv.create_rectangle(lx-4, ly-4, lx+bw2, ly+bh,
                            fill=C["card_bg"], outline=C["card_brd"])
        cv.create_text(lx+4, ly+2, text="LEGENDA",
                       fill=C["txt_dim"], font=("Courier", 7, "bold"), anchor="nw")
        for i, (cor, txt) in enumerate(itens):
            yy = ly + 16 + i*17
            cv.create_rectangle(lx+2, yy+3, lx+14, yy+12, fill=cor, outline="")
            cv.create_text(lx+18, yy+7, text=txt, anchor="w",
                           fill=C["txt_b"], font=("Courier", 8))

        # ── Info rápida no topo direito ───────────────────────────────────────
        if self._rota1 or self._rota2:
            infos = []
            if self._rota1:
                infos.append(f"R1: {self._custo1:.0f} | {self._sem1} sem")
            if self._rota2:
                infos.append(f"R2: {self._custo2} km | {self._sem2} sem")
            info = "   ".join(infos)
            tw = len(info)*6 + 20
            cv.create_rectangle(W-tw-8, 8, W-8, 28,
                                fill=C["card_bg"], outline=C["r1_line"])
            cv.create_text(W-12, 18, text=info, fill=C["accent"],
                           font=("Courier", 8, "bold"), anchor="e")


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = App()
    app.mainloop()
