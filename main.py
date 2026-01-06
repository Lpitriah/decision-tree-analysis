
"""
SISTEM PENDUKUNG KEPUTUSAN
Decision Tree Analysis
Peluncuran Produk Baru Startup

Struktur Program:
1. Import Library
2. Struktur Data Utama
3. Fungsi-Fungsi Helper
4. Logika Perhitungan
5. Visualisasi & Analisis
6. Antarmuka Pengguna (GUI)
"""

# =======================
# 1. IMPORT LIBRARY
# =======================
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx


class DecisionTreeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SPK Peluncuran Produk - Decision Tree")
        self.root.geometry("950x650")

        # =======================
        # 2. STRUKTUR DATA UTAMA
        # =======================
        self.data = []
        self.ev = {}

        self.set_style()
        self.create_input_section()
        self.create_table()
        self.create_buttons()

    # =======================
    # STYLE
    # =======================
    def set_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)

    # =======================
    # INPUT
    # =======================
    def create_input_section(self):
        frame = ttk.LabelFrame(self.root, text=" Input Data ")
        frame.pack(fill="x", padx=15, pady=10)

        labels = ["Keputusan", "Kondisi Pasar", "Probabilitas", "Cost (Rp)", "Revenue (Rp)"]
        self.entries = {}

        for i, lbl in enumerate(labels):
            ttk.Label(frame, text=lbl).grid(row=0, column=i, padx=5)

        keys = ["keputusan", "kondisi", "prob", "cost", "revenue"]
        for i, key in enumerate(keys):
            self.entries[key] = ttk.Entry(frame, width=15)
            self.entries[key].grid(row=1, column=i, padx=5)

    # =======================
    # TABLE
    # =======================
    def create_table(self):
        frame = ttk.LabelFrame(self.root, text=" Dataset ")
        frame.pack(fill="both", expand=True, padx=15, pady=10)

        cols = ("Decision", "Condition", "Prob", "Cost", "Revenue", "Payoff")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings")

        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, anchor="center")

        self.tree.pack(fill="both", expand=True)

    # =======================
    # BUTTONS
    # =======================
    def create_buttons(self):
        frame = ttk.Frame(self.root)
        frame.pack(pady=10)

        ttk.Button(frame, text="Tambah Data", command=self.add_data).grid(row=0, column=0, padx=5)
        ttk.Button(frame, text="Hapus Data", command=self.delete_data).grid(row=0, column=1, padx=5)
        ttk.Button(frame, text="Hitung EV", command=self.calculate).grid(row=0, column=2, padx=5)
        ttk.Button(frame, text="Grafik EV", command=self.show_chart).grid(row=0, column=3, padx=5)
        ttk.Button(frame, text="Decision Tree", command=self.show_decision_tree).grid(row=0, column=4, padx=5)
        ttk.Button(frame, text="Sensitivity Analysis", command=self.sensitivity_analysis).grid(row=0, column=5, padx=5)

    # =======================
    # 3. FUNGSI-FUNGSI HELPER
    # =======================
    def parse_rupiah(self, value):
        return float(value.replace(".", ""))

    # =======================
    # 4. LOGIKA PERHITUNGAN
    # =======================
    def add_data(self):
        try:
            d = self.entries["keputusan"].get()
            c = self.entries["kondisi"].get()
            p = float(self.entries["prob"].get())
            cost = self.parse_rupiah(self.entries["cost"].get())
            rev = self.parse_rupiah(self.entries["revenue"].get())

            payoff = rev - cost
            row = [d, c, p, cost, rev, payoff]

            self.data.append(row)
            self.tree.insert("", "end", values=row)

            for e in self.entries.values():
                e.delete(0, tk.END)
        except:
            messagebox.showerror("Error", "Input tidak valid")

    def delete_data(self):
        for item in self.tree.selection():
            idx = self.tree.index(item)
            self.tree.delete(item)
            del self.data[idx]

    def calculate(self):
        df = pd.DataFrame(self.data,
                          columns=["Decision", "Cond", "Prob", "Cost", "Rev", "Payoff"])
        self.ev.clear()

        for d in df["Decision"].unique():
            self.ev[d] = (df[df["Decision"] == d]["Prob"]
                          * df[df["Decision"] == d]["Payoff"]).sum()

        best = max(self.ev, key=self.ev.get)

        hasil = "\n".join([f"{k} : Rp{v:,.0f}" for k, v in self.ev.items()])
        messagebox.showinfo("Hasil EV",
                            f"Expected Value:\n{hasil}\n\nKeputusan Terbaik:\n{best}")

    # =======================
    # 5. VISUALISASI & ANALISIS
    # =======================
    def show_chart(self):
        if not self.ev:
            messagebox.showwarning("Peringatan", "Hitung EV terlebih dahulu!")
            return

        plt.figure(figsize=(7, 4))
        plt.plot(self.ev.keys(), self.ev.values(), marker="o", linestyle="--")
        plt.title("Grafik Expected Value")
        plt.xlabel("Keputusan")
        plt.ylabel("Expected Value (Rp)")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def sensitivity_analysis(self):
        if not self.data:
            messagebox.showwarning("Peringatan", "Data kosong!")
            return

        df = pd.DataFrame(self.data,
                          columns=["Decision", "Cond", "Prob", "Cost", "Rev", "Payoff"])

        prob_range = [0.2, 0.4, 0.6, 0.8]

        plt.figure(figsize=(8, 5))

        for d in df["Decision"].unique():
            ev_list = []
            for p in prob_range:
                temp = df[df["Decision"] == d].copy()
                temp["Prob"] = p
                ev_list.append((temp["Prob"] * temp["Payoff"]).sum())

            plt.plot(prob_range, ev_list, marker="o", linestyle="--", label=d)

        plt.title("Sensitivity Analysis terhadap Probabilitas")
        plt.xlabel("Probabilitas")
        plt.ylabel("Expected Value (Rp)")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def show_decision_tree(self):
        if not self.data:
            messagebox.showwarning("Peringatan", "Data kosong!")
            return

        G = nx.DiGraph()
        G.add_node("Decision")
        pos = {"Decision": (0, 1)}

        for i, (d, c, p, cost, rev, payoff) in enumerate(self.data):
            chance = f"{c}\nP={p}"
            terminal = f"Rp{payoff:,.0f}"

            G.add_edge("Decision", chance)
            G.add_edge(chance, terminal)

            pos[chance] = (i, 0)
            pos[terminal] = (i, -1)

        plt.figure(figsize=(11, 6))
        nx.draw(G, pos, with_labels=True, node_size=2500)
        plt.title("Decision Tree Peluncuran Produk")
        plt.axis("off")
        plt.show()


# =======================
# 6. RUN PROGRAM
# =======================
if __name__ == "__main__":
    root = tk.Tk()
    app = DecisionTreeApp(root)
    root.mainloop()