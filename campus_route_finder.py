import math
import tkinter as tk
from tkinter import ttk

INF = math.inf

PRESETS = {
    "Campus paths (sample)": (True, "Gate Admin 120\nGate Library 200\nAdmin Library 90\nAdmin CSEBlock 150\n"
                              "Library CSEBlock 100\nLibrary Canteen 80\nCSEBlock Lab 60\nCanteen Auditorium 110\n"
                              "Canteen Hostel 250\nAuditorium Hostel 130\nLab Auditorium 180\nSports Hostel 90\n"
                              "Sports Canteen 160"),
    "Boundary: single path": (True, "A B 5"),
    "Boundary: disconnected buildings": (True, "A B 4\nC D 6"),
    "One-way paths": (False, "A B 2\nB C 3\nC A 4\nA C 9"),
    "Boundary: negative cycle": (False, "A B 1\nB C -3\nC A 1"),
    "Boundary: empty input": (True, ""),
    "Boundary: invalid distance": (True, "A B x"),
}

names, edges, steps, nxt, path = [], [], [], [], []
idx, two_way, negative = 0, True, False


def read_paths(data):
    names, edges = [], []
    for n, line in enumerate(data.splitlines(), 1):
        p = line.split()
        if not p:
            continue
        if len(p) != 3:
            raise ValueError(f"Line {n}: write it as Building1 Building2 Distance.")
        try:
            w = float(p[2])
            if not math.isfinite(w):
                raise ValueError
        except ValueError:
            raise ValueError(f"Line {n}: the distance must be a number.")
        for b in p[:2]:
            if b not in names:
                names.append(b)
        edges.append((names.index(p[0]), names.index(p[1]), w))
    if not edges:
        raise ValueError("Add at least one path.")
    if len(names) > 12:
        raise ValueError("This version supports up to 12 buildings.")
    return names, edges


def floyd_warshall(n, edges, two_way):
    d = [[0 if i == j else INF for j in range(n)] for i in range(n)]
    nxt = [[i if i == j else None for j in range(n)] for i in range(n)]
    for u, v, w in edges:
        for a, b in [(u, v), (v, u)] if two_way else [(u, v)]:
            if w < d[a][b]:
                d[a][b], nxt[a][b] = w, b
    steps = [(-1, [], [row[:] for row in d])]
    for k in range(n):
        changes = []
        for i in range(n):
            for j in range(n):
                if d[i][k] + d[k][j] < d[i][j]:
                    changes.append((i, j, d[i][j], d[i][k] + d[k][j]))
                    d[i][j] = d[i][k] + d[k][j]
                    nxt[i][j] = nxt[i][k]
        steps.append((k, changes, [row[:] for row in d]))
    return steps, nxt


def route(nxt, a, b):
    result = [a]
    while a != b:
        a = nxt[a][b]
        result.append(a)
    return result


def fmt(v):
    return "∞" if v == INF else f"{v:g}"


def build():
    global names, edges, steps, nxt, two_way, negative, idx, path
    path = []
    try:
        names, edges = read_paths(text.get("1.0", "end"))
    except ValueError as e:
        names, steps = [], []
        show()
        msg.config(text=str(e), fg="red")
        return
    two_way = two_var.get()
    steps, nxt = floyd_warshall(len(names), edges, two_way)
    negative = any(steps[-1][2][i][i] < 0 for i in range(len(names)))
    idx = 0
    for box in (qa, qb):
        box["values"] = names
    qa.set(names[0])
    qb.set(names[-1])
    show()


def step():
    global idx
    if steps and idx < len(steps) - 1:
        idx += 1
        show()


def back():
    global idx
    if steps and idx > 0:
        idx -= 1
        show()


def run_all():
    global idx
    if steps:
        idx = len(steps) - 1
        show()


def reset():
    global idx
    idx = 0
    show()


def show_route():
    global path
    if not steps:
        return
    run_all()
    if negative:
        route_lbl.config(text="No routes: negative cycle.")
        return
    a, b = names.index(qa.get()), names.index(qb.get())
    d = steps[-1][2][a][b]
    path = route(nxt, a, b) if d != INF else []
    route_lbl.config(text=" -> ".join(names[i] for i in path) + f":  {fmt(d)} m" if path else "No route.")
    draw()


def show():
    for w in matrix.winfo_children():
        w.destroy()
    log.delete("1.0", "end")
    ranking.config(text="")
    route_lbl.config(text="")
    if not steps:
        draw()
        return
    k, changes, d = steps[idx]
    last = idx == len(steps) - 1
    if not last:
        path.clear()
    for kk, ch, _ in steps[:idx + 1]:
        log.insert("end", "Start: direct paths only\n" if kk < 0 else f"Pivot {names[kk]}: {len(ch)} improved\n")
        for i, j, old, new in ch:
            log.insert("end", f"  {names[i]} -> {names[j]}: {fmt(old)} -> {fmt(new)}\n")
    log.see("end")
    n = len(names)
    changed = {(i, j) for i, j, _, _ in changes}
    for i in range(n):
        tk.Label(matrix, text=names[i], width=9, relief="solid", bd=1, bg="#eeeeee").grid(row=0, column=i + 1)
        tk.Label(matrix, text=names[i], width=9, relief="solid", bd=1, bg="#eeeeee").grid(row=i + 1, column=0)
        for j in range(n):
            color = "#bfe8c8" if (i, j) in changed else "#fde8b0" if k in (i, j) else "white"
            tk.Label(matrix, text=fmt(d[i][j]), bg=color, relief="solid", bd=1).grid(row=i + 1, column=j + 1, sticky="nsew")
    if last and negative:
        msg.config(text="Negative cycle detected: a diagonal value is below 0.", fg="red")
        ranking.config(text="Not available: negative cycle.")
    else:
        msg.config(text="Matrix holds direct paths only. Press Step to begin." if k < 0
                   else f"Pivot {names[k]}: {len(changes)} distance(s) improved.", fg="black")
    if last and not negative:
        rows = []
        for i in range(n):
            others = [d[i][j] for j in range(n) if j != i]
            if INF not in others:
                rows.append((sum(others), max(others, default=0), names[i]))
        rows.sort()
        if rows:
            lines = [f"Best location: {rows[0][2]} ({fmt(rows[0][0])} m total)", "", "Building      Total   Farthest"]
            lines += [f"{b:<12} {fmt(t):>6} {fmt(f):>9}" for t, f, b in rows]
            ranking.config(text="\n".join(lines))
        else:
            ranking.config(text="No building can reach every other building,\nso no best location exists.")
    draw()


def draw():
    canvas.delete("all")
    if not names:
        return
    n = len(names)
    pos = [(310 + 115 * math.cos(2 * math.pi * i / n), 150 + 115 * math.sin(2 * math.pi * i / n)) for i in range(n)]
    hops = {(path[i], path[i + 1]) for i in range(len(path) - 1)}
    for u, v, w in edges:
        if u == v:
            continue
        (x1, y1), (x2, y2) = pos[u], pos[v]
        length = math.hypot(x2 - x1, y2 - y1)
        dx, dy = (x2 - x1) / length * 18, (y2 - y1) / length * 18
        hot = (u, v) in hops or (two_way and (v, u) in hops)
        canvas.create_line(x1 + dx, y1 + dy, x2 - dx, y2 - dy, fill="red" if hot else "gray",
                           width=3 if hot else 1, arrow=None if two_way else tk.LAST)
        canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=f"{w:g}", fill="blue")
    for i, (x, y) in enumerate(pos):
        canvas.create_oval(x - 18, y - 18, x + 18, y + 18, fill="orange" if steps[idx][0] == i else "white",
                           outline="red" if i in path else "black", width=2)
        canvas.create_text(x, y, text=names[i][:5], font=("Arial", 8, "bold"))


def load_preset(event=None):
    two, data = PRESETS[preset.get()]
    two_var.set(two)
    text.delete("1.0", "end")
    text.insert("1.0", data)
    build()


root = tk.Tk()
root.title("Campus Route Finder - Floyd-Warshall")
root.geometry("1180x900")

top, mid, low = tk.Frame(root), tk.Frame(root), tk.Frame(root)
top.pack(fill="x", padx=8, pady=6)
msg = tk.Label(root, font=("Arial", 11, "bold"), anchor="w")
msg.pack(fill="x", padx=8)
mid.pack(fill="x", padx=8, pady=6)
low.pack(fill="x", padx=8, pady=6)

left = tk.LabelFrame(top, text="1. Enter paths (Building1 Building2 Distance)")
left.pack(side="left", anchor="n")
text = tk.Text(left, width=32, height=12)
text.pack(padx=4, pady=4)
two_var = tk.BooleanVar(value=True)
tk.Checkbutton(left, text="Paths are two-way", variable=two_var).pack(anchor="w")
preset = ttk.Combobox(left, values=list(PRESETS), state="readonly", width=30)
preset.pack(pady=4)
preset.bind("<<ComboboxSelected>>", load_preset)
buttons = tk.Frame(left)
buttons.pack(pady=4)
for label, command in [("Build", build), ("Back", back), ("Step", step), ("Run all", run_all), ("Reset", reset)]:
    tk.Button(buttons, text=label, command=command).pack(side="left", padx=2)
canvas = tk.Canvas(top, width=640, height=300, bg="white")
canvas.pack(side="left", padx=12)

matrix = tk.Frame(mid)
matrix.pack(side="left", anchor="n")
log = tk.Text(mid, width=36, height=14, font=("Courier", 9), wrap="none")
log.pack(side="left", padx=12, anchor="n")

bottom = tk.LabelFrame(low, text="Find a route")
bottom.pack(side="left", anchor="n")
qa = ttk.Combobox(bottom, state="readonly", width=11)
qb = ttk.Combobox(bottom, state="readonly", width=11)
qa.grid(row=0, column=0, padx=4, pady=4)
qb.grid(row=0, column=1, padx=4)
tk.Button(bottom, text="Show route", command=show_route).grid(row=0, column=2, padx=4)
route_lbl = tk.Label(bottom, font=("Arial", 10, "bold"), wraplength=380, justify="left")
route_lbl.grid(row=1, column=0, columnspan=3, sticky="w", padx=4, pady=4)
ranking = tk.Label(low, font=("Courier", 9), justify="left", anchor="nw")
ranking.pack(side="left", padx=12, anchor="n")

preset.current(0)
load_preset()

if __name__ == "__main__":
    root.mainloop()
