import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy import stats

# ============================================
#   ABA 3 – SEU PROGRAMA ORIGINAL DE nₑ
# ============================================
E_CHARGE = 1.602176634e-19  # C


def popup_selecionavel(texto):
    win = tk.Toplevel()
    win.title("Resultado")
    win.geometry("350x120")

    lbl = tk.Text(win, height=4, width=40)
    lbl.insert("1.0", texto)
    lbl.config(state="normal")
    lbl.pack(padx=10, pady=10)

    btn = tk.Button(win, text="Fechar", command=win.destroy)
    btn.pack(pady=5)


def create_ne_ui(parent):
    """Interface da aba 'Cálculo de nₑ' — exatamente igual ao programa original."""

    def calcular_ne():
        try:
            Isat_micro = float(entry_Isat.get().replace(",", "."))
            vd = float(entry_vd.get().replace(",", "."))
            A = float(entry_A.get().replace(",", "."))

            Isat = Isat_micro * 1e-6
            ne = Isat / (E_CHARGE * vd * A)

            nonlocal ultimo_resultado
            ultimo_resultado = f"nₑ = {ne:.6e} m⁻³"

            popup = tk.Toplevel()
            popup.title("Resultado")
            tk.Label(popup, text=ultimo_resultado).pack(padx=20, pady=10)
            tk.Button(popup, text="Fechar", command=popup.destroy).pack(pady=5)

        except ValueError:
            popup_selecionavel("Erro: insira valores numéricos válidos.")

    def salvar_dat():
        """Mesma janela da aba 2 — idêntica, só appenda no arquivo."""
        win = tk.Toplevel()
        win.title("Salvar resultado em .dat")

        tk.Label(win, text="Nome do arquivo .dat existente:").pack(padx=10, pady=5)
        entry_name = tk.Entry(win, width=30)
        entry_name.pack(padx=10, pady=5)

        def confirmar():
            nome = entry_name.get().strip()
            if nome:
                try:
                    with open(nome, "a") as f:
                        f.write(ultimo_resultado + "\n")
                except Exception as e:
                    tk.Message(win, text=f"Erro: {e}", width=260).pack(pady=10)
            win.destroy()

        tk.Button(win, text="Salvar", command=confirmar).pack(pady=5)
        tk.Button(win, text="Cancelar", command=win.destroy).pack(pady=5)

    # interface visual
    frame = tk.Frame(parent)
    frame.pack(pady=20)

    ultimo_resultado = ""

    tk.Label(frame, text="I_sat (microampere):").grid(row=0, column=0, sticky="e")
    entry_Isat = tk.Entry(frame)
    entry_Isat.grid(row=0, column=1)

    tk.Label(frame, text="v_d (m/s):").grid(row=1, column=0, sticky="e")
    entry_vd = tk.Entry(frame)
    entry_vd.grid(row=1, column=1)

    tk.Label(frame, text="A_sonda (m²):").grid(row=2, column=0, sticky="e")
    entry_A = tk.Entry(frame)
    entry_A.grid(row=2, column=1)

    # Botão calcular — igual ao original
    tk.Button(frame, text="Calcular nₑ", command=calcular_ne)\
        .grid(row=3, column=0, columnspan=2, pady=10)

    # Botão SALVAR .dat — igual ao da aba 2
    tk.Button(frame, text="Salvar resultado em .dat", command=salvar_dat)\
        .grid(row=4, column=0, columnspan=2, pady=5)

    return frame


# ============================================
#   ABA 1 — GERADOR DE GRÁFICO
#   (Seu código permanece intacto)
# ============================================

R = 502e3  # resistência 502 kΩ


# ---------- helpers para text undo custom ----------
def _get_text(widget):
    return widget.get("1.0", "end-1c")


def _index_from_offset(offset):
    return f"1.0+{offset}c"


def _find_diff(prev, cur):
    if prev == cur:
        return None, None, None

    min_len = min(len(prev), len(cur))
    first_diff = 0
    while first_diff < min_len and prev[first_diff] == cur[first_diff]:
        first_diff += 1

    if len(cur) > len(prev):
        inserted = len(cur) - len(prev)
        return "insert", first_diff, cur[first_diff:first_diff + inserted]

    if len(cur) < len(prev):
        deleted = len(prev) - len(cur)
        return "delete", first_diff, prev[first_diff:first_diff + deleted]

    return None, None, None


def attach_custom_undo(widget):
    widget._prev_text = _get_text(widget)
    widget._undo_stack = []

    def on_key_release(event):
        try:
            cur = _get_text(widget)
            prev = widget._prev_text
            typ, pos, txt = _find_diff(prev, cur)
            if typ is not None:
                widget._undo_stack.append((typ, pos, txt))
            widget._prev_text = cur
        except Exception:
            widget._prev_text = _get_text(widget)

    def do_ctrl_z(event):
        try:
            if not widget._undo_stack:
                return "break"
            typ, pos, txt = widget._undo_stack.pop()

            if typ == "insert":
                start = _index_from_offset(pos)
                end = _index_from_offset(pos + len(txt))
                widget.delete(start, end)

            elif typ == "delete":
                widget.insert(_index_from_offset(pos), txt)

            widget._prev_text = _get_text(widget)
        except tk.TclError:
            pass
        return "break"

    def do_ctrl_a(event):
        widget.tag_add("sel", "1.0", "end")
        return "break"

    widget.bind("<Control-a>", do_ctrl_a, add=True)
    widget.bind("<KeyRelease>", on_key_release, add=True)
    widget.bind("<Control-z>", do_ctrl_z, add=True)
    widget.bind("<<Paste>>", lambda e: widget.after(1, lambda: on_key_release(e)), add=True)


entrada_x = None
entrada_y = None
corrente_var = None
pressao_var = None


def ler_xy():
    x_text = entrada_x.get("1.0", tk.END).strip().splitlines()
    y_text = entrada_y.get("1.0", tk.END).strip().splitlines()

    x = [float(v.replace(",", ".")) for v in x_text if v.strip()]
    y1 = [float(v.replace(",", ".")) for v in y_text if v.strip()]

    if len(x) != len(y1):
        raise ValueError("As colunas X e Y precisam ter o MESMO número de linhas.")
    if len(x) == 0:
        raise ValueError("Nenhum dado inserido.")

    return x, y1


def gerar_grafico():
    try:
        x, y1 = ler_xy()

        I = [(v / R) * 1e6 for v in y1]  # µA
        I_err = [(0.1 / R) * 1e6] * len(y1)
        xerr = [0.1] * len(x)

        plt.errorbar(
            x, I,
            xerr=xerr, yerr=I_err,
            fmt='o-', ecolor='blue', color='blue',
            capsize=3,
            label=f"i = {corrente_var.get()} mA\np = {pressao_var.get()} mbar"
        )
        plt.title('Sonda de Langmuir', fontsize=14)
        plt.xlabel('Tensão Sonda (V)', fontsize=14)
        plt.ylabel('Corrente (µA)', fontsize=14)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend(fontsize=14)
        plt.tight_layout()
        plt.show()

    except Exception as e:
        messagebox.showerror("Erro", f"Algo deu errado:\n{e}")


def salvar_tabela_dat():
    try:
        x, y1 = ler_xy()
        I = [(v / R) * 1e6 for v in y1]

        filename = filedialog.asksaveasfilename(
            defaultextension=".dat",
            filetypes=[("Arquivo DAT", "*.dat"), ("Todos os arquivos", "*.*")],
            title="Salvar tabela como (.dat)"
        )
        if not filename:
            return

        df = pd.DataFrame({
            "Tensao_Sonda_V": x,
            "Corrente_microA": I
        })
        df.to_csv(filename, sep="\t", index=False, header=False)

        messagebox.showinfo("Sucesso", f"Arquivo salvo como:\n{filename}")

    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível salvar:\n{e}")


def create_langmuir_ui(parent):
    global entrada_x, entrada_y, corrente_var, pressao_var

    frame_outer = tk.Frame(parent)
    frame_outer.pack(fill="both", expand=True, padx=10, pady=10)

    sub_center = tk.Frame(frame_outer)
    sub_center.pack(pady=5)

    frame_params = tk.Frame(sub_center)
    frame_params.pack(pady=5)

    corrente_var = tk.StringVar(value="0")
    pressao_var = tk.StringVar(value="0")

    tk.Label(frame_params, text="Corrente (mA):").grid(row=0, column=0)
    tk.Entry(frame_params, textvariable=corrente_var, width=10).grid(row=0, column=1)
    tk.Label(frame_params, text="Pressão (mbar):").grid(row=0, column=2)
    tk.Entry(frame_params, textvariable=pressao_var, width=10).grid(row=0, column=3)

    frame = tk.Frame(sub_center)
    frame.pack(pady=10, fill="both", expand=False)

    tk.Label(frame, text="Tensão na Sonda (V)").grid(row=0, column=0)
    entrada_x = tk.Text(frame, height=25, width=20, undo=True)
    entrada_x.grid(row=1, column=0, padx=10)

    tk.Label(frame, text="Tensão no Resistor (V)").grid(row=0, column=1)
    entrada_y = tk.Text(frame, height=25, width=20, undo=True)
    entrada_y.grid(row=1, column=1, padx=10)

    attach_custom_undo(entrada_x)
    attach_custom_undo(entrada_y)

    botoes_frame = tk.Frame(sub_center)
    botoes_frame.pack(pady=10)

    tk.Button(botoes_frame, text="Gerar Gráfico", command=gerar_grafico,
              font=("Arial", 12), bg="lightgreen", width=18).grid(row=0, column=0, padx=8)
    tk.Button(botoes_frame, text="Salvar Tabela (.dat)", command=salvar_tabela_dat,
              font=("Arial", 12), bg="lightblue", width=18).grid(row=0, column=1, padx=8)

    return frame_outer


# ============================================
#   ABA 2 — Cálculo de Te (seu código original)
# ============================================

def detect_knee(V, I, smoothing_window=7, derivative_window=5):
    order = np.argsort(V)
    Vs = np.array(V)[order]
    Is = np.array(I)[order]

    kern = np.ones(smoothing_window) / smoothing_window
    Is_smooth = np.convolve(Is, kern, mode='same')

    dIdV = np.gradient(Is_smooth, Vs)

    mask_pos = Vs >= 0
    if not np.any(mask_pos):
        return Vs[len(Vs)//2]

    V_pos = Vs[mask_pos]
    d_pos = dIdV[mask_pos]

    d_smooth = np.convolve(d_pos, np.ones(derivative_window)/derivative_window, mode='same')

    idx_max = np.argmax(d_smooth)
    return V_pos[idx_max]


def fit_line(V, I, vmin, vmax):
    mask = (V >= vmin) & (V <= vmax)
    if np.sum(mask) < 2:
        raise ValueError(f"Interval [{vmin},{vmax}] não tem pontos suficientes para ajuste.")
    slope, intercept, r, p, se = stats.linregress(V[mask], I[mask])
    return slope, intercept, mask


def calcular_Te_automatico(
    V, I, neg_range=(-30, -5), deriv_range=(-2, 2), use_auto_knee=True,
    manual_pos_range=None, manual_sat_range=None, plot=True, I_in_microamp=False
):
    V = np.array(V)
    I = np.array(I).astype(float)

    if I_in_microamp:
        I = I * 1e-6

    order = np.argsort(V)
    V = V[order]
    I = I[order]

    try:
        slope_neg, intercept_neg, mask_neg = fit_line(V, I, neg_range[0], neg_range[1])
    except Exception as e:
        neg_mask_fallback = V < 0
        if np.sum(neg_mask_fallback) >= 3:
            slope_neg, intercept_neg, mask_neg = fit_line(
                V, I,
                np.min(V[neg_mask_fallback]),
                np.max(V[neg_mask_fallback])
            )
        else:
            raise RuntimeError("Falha ao ajustar reta negativa.") from e

    if manual_pos_range is not None and manual_sat_range is not None:
        pos_vmin, pos_vmax = manual_pos_range
        sat_vmin, sat_vmax = manual_sat_range
    else:
        if use_auto_knee:
            knee = detect_knee(V, I)
            pos_vmin, pos_vmax = 0.0, max(knee, 1.0)
            sat_vmin, sat_vmax = knee, np.max(V)
            pos_vmax = max(pos_vmax, 0.5)
        else:
            pos_vmin, pos_vmax = 0.0, 10.0
            sat_vmin, sat_vmax = 10.0, np.max(V)

    if manual_pos_range is not None:
        pos_vmin, pos_vmax = manual_pos_range
    if manual_sat_range is not None:
        sat_vmin, sat_vmax = manual_sat_range

    slope_pos, intercept_pos, mask_pos = fit_line(V, I, pos_vmin, pos_vmax)

    try:
        slope_sat, intercept_sat, mask_sat = fit_line(V, I, sat_vmin, sat_vmax)
    except Exception:
        sat_vmin2 = sat_vmin
        sat_vmax2 = sat_vmin + (sat_vmax - sat_vmin) * 0.6
        slope_sat, intercept_sat, mask_sat = fit_line(V, I, sat_vmin2, sat_vmax2)

    if slope_pos == slope_sat:
        raise RuntimeError("As duas retas ficaram paralelas.")

    V_intersect = (intercept_sat - intercept_pos) / (slope_pos - slope_sat)
    Isat = slope_pos * V_intersect + intercept_pos

    try:
        slope_der, intercept_der, mask_der = fit_line(V, I, deriv_range[0], deriv_range[1])
        dIdV = slope_der
    except Exception:
        idx0 = np.argmin(np.abs(V - 0.0))
        if idx0 > 0 and idx0 < len(V)-1:
            dIdV = (I[idx0+1] - I[idx0-1]) / (V[idx0+1] - V[idx0-1])
        else:
            dIdV = slope_pos

    Te = Isat / (2.0 * dIdV)

    result = {
        "Te_eV": Te,
        "Isat_A": Isat,
        "dIdV_AperV": dIdV,
        "V_intersect": V_intersect,
        "slope_neg": slope_neg,
        "intercept_neg": intercept_neg,
        "slope_pos": slope_pos,
        "intercept_pos": intercept_pos,
        "slope_sat": slope_sat,
        "intercept_sat": intercept_sat,
        "mask_neg": mask_neg,
        "mask_pos": mask_pos,
        "mask_sat": mask_sat,
        "V": V,
        "I": I,
        "pos_range": (pos_vmin, pos_vmax),
        "sat_range": (sat_vmin, sat_vmax),
        "knee": (detect_knee(V, I) if use_auto_knee else None)
    }

    if plot:
        plt.figure(figsize=(10, 6))
        plt.scatter(V, I, s=40, alpha=0.9)

        plt.autoscale(enable=True, axis='both', tight=True)
        xlim = plt.xlim()
        ylim = plt.ylim()
        plt.autoscale(enable=False)

        Vlin = np.linspace(np.min(V), np.max(V), 400)
        plt.plot(Vlin, slope_pos * Vlin + intercept_pos, 'g-', lw=2)
        plt.plot(Vlin, slope_sat * Vlin + intercept_sat, 'c-', lw=2)
        plt.axvline(V_intersect, color='m', linestyle='--')

        plt.xlim(xlim)
        plt.ylim(ylim)

        plt.xlabel("Tensão (V)")
        plt.ylabel("Corrente (µA)")
        plt.title("Ajustes para cálculo de Te (sonda dupla)")
        plt.grid(True)
        plt.show()

    return result


class App:
    def __init__(self, master):
        master.winfo_toplevel().title("LangDouble")
        self.master = master
        self.V = None
        self.I = None

        tk.Button(master, text="Carregar arquivo (tab)", command=self.load_file).pack()

        self.path_label = tk.Label(master, text="Nenhum arquivo carregado.")
        self.path_label.pack()

        # ==========================
        # Intervalo Negativo (somente leitura)
        # ==========================
        #tk.Label(master, text="Intervalo Negativo:").pack()
        self.entry_neg = tk.Entry(master)
        self.entry_neg.insert(0, "-12,-4")
        self.entry_neg.config(state="readonly")
        #self.entry_neg.pack()

        # ==========================
        # Intervalo Derivada (somente leitura)
        # ==========================
        tk.Label(master, text="Intervalo Derivada:").pack()
        self.entry_der = tk.Entry(master)
        self.entry_der.insert(0, "-1,1")
        self.entry_der.config(state="readonly")
        self.entry_der.pack()

        # ==========================
        # Intervalo Positivo (editável)
        # ==========================
        tk.Label(master, text="Intervalo Positivo:").pack()
        self.entry_pos = tk.Entry(master)
        self.entry_pos.insert(0, "0,9.5")
        self.entry_pos.pack()

        # ==========================
        # Intervalo Saturação (editável)
        # ==========================
        tk.Label(master, text="Intervalo Saturação:").pack()
        self.entry_sat = tk.Entry(master)
        self.entry_sat.insert(0, "9.5,40.5")
        self.entry_sat.pack()

        self.use_auto = tk.IntVar(value=1)
        tk.Checkbutton(master, text="Usar auto knee", variable=self.use_auto).pack()

        tk.Button(master, text="Calcular", command=self.run_calc).pack()

    def load_file(self):
        path = filedialog.askopenfilename()
        if not path:
            return
        data = np.loadtxt(path, delimiter="\t")
        self.V = data[:, 0]
        self.I = data[:, 1]

        self.path_label.config(text=f"Carregado:\n{path}")
        self.loaded_path = path

    def run_calc(self):
        if self.V is None:
            messagebox.showerror("Erro", "Nenhum arquivo carregado.")
            return

        neg_range = tuple(map(float, self.entry_neg.get().split(",")))
        der_range = tuple(map(float, self.entry_der.get().split(",")))
        pos_range = tuple(map(float, self.entry_pos.get().split(",")))
        sat_range = tuple(map(float, self.entry_sat.get().split(",")))

        res = calcular_Te_automatico(
            self.V, self.I,
            neg_range=neg_range,
            deriv_range=der_range,
            use_auto_knee=bool(self.use_auto.get()),
            manual_pos_range=pos_range,
            manual_sat_range=sat_range,
            plot=True,
            I_in_microamp=False
        )

        msg = (
            f"Te = {res['Te_eV']:.3f} eV\n"
            f"I_sat = {res['Isat_A']:.3f} µA\n"
            f"dI/dV = {res['dIdV_AperV']:.3f} µA/V\n"
            f"V_intersecção = {res['V_intersect']:.3f} V"
        )
        messagebox.showinfo("Resultado", msg)

        save_path = filedialog.asksaveasfilename(
            defaultextension=".dat",
            filetypes=[("Arquivo DAT", "*.dat")]
        )
        if save_path:
            with open(save_path, "w") as f:
                f.write("# Resultado do cálculo de Te (sonda dupla)\n")
                f.write(f"# Arquivo carregado: {self.loaded_path}\n\n")
                f.write(f"Te (eV) = {res['Te_eV']:.3f}\n")
                f.write(f"I_sat (µA) = {res['Isat_A']:.3f}\n")
                f.write(f"dIdV_V=0 (µA/V) = {res['dIdV_AperV']:.3f}\n")
                f.write(f"V_intersect (V) = {res['V_intersect']:.3f}\n")
                f.write(f"pos_range = {res['pos_range']}\n")
                f.write(f"sat_range = {res['sat_range']}\n")


# ============================================
#   JANELA FINAL — 3 ABAS
# ============================================

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Sonda de Langmuir — Ferramentas Unificadas")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    # Aba 1 — Gerador de Gráfico
    frame1 = tk.Frame(notebook)
    create_langmuir_ui(frame1)
    notebook.add(frame1, text="Gerador de Gráfico")

    # Aba 2 — Cálculo de Te
    frame2 = tk.Frame(notebook)
    app2 = App(frame2)
    notebook.add(frame2, text="Cálculo de Te")

    # Aba 3 — Cálculo de nₑ (seu programa 1 intacto)
    frame3 = tk.Frame(notebook)
    create_ne_ui(frame3)
    notebook.add(frame3, text="Cálculo de nₑ")

    root.geometry("900x700")
    root.mainloop()