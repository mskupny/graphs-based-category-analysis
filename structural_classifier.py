"""
Structural pre-assessment of EN ISO 13849-1 categories (B/1 vs 3/4) from circuit graphs.

Supplementary code for: M. Skupny, "Graph-Based Numerical Method for Safety Category
Assessment in Industrial Control Systems".

Usage:
    python structural_classifier.py classify  graphs/*.json
    python structural_classifier.py perturb   graphs/*.json

Conditions (Section 3.3 of the paper), evaluated for every input device i and actuator m:
    p_red : at least two simple paths i -> m in the path layer
    p_fb  : a logic node v on a path is reached, through feedback edges, from a node u
            lying after v on the same path
    p_log : some logic node on the paths receives >= 2 control/safety_input edges
            from the contacts of device i
    group = 3/4 if p_red and p_fb and p_log, else B/1
"""
import json, re, sys, glob, os, itertools, time
from collections import defaultdict, Counter
import networkx as nx

PATH_TYPES = ("control", "safety_input", "safety_output", "power")
CHANNEL_TYPES = ("control", "safety_input")
ALIASES = {"input": "control", "output": "safety_output"}   # legacy edge names
CUTOFF = 12

def device(node_id):
    m = re.match(r"([A-Za-z]+\d+)", node_id)
    return m.group(1) if m else node_id

def read(path):
    d = json.load(open(path)); d = d.get("diagram", d)
    els = [dict(x, IO="Input" if x.get("IO") == "Safety_Input" else x.get("IO")) for x in d["elements"]]
    cons = [dict(c, type=ALIASES.get(c["type"], c["type"])) for c in d["connections"]]
    return d.get("metadata", {}), els, cons

class Circuit:
    def __init__(self, els, cons):
        self.G = nx.DiGraph()
        for e in els: self.G.add_node(e["id"], **e)
        for c in cons: self.G.add_edge(c["from"], c["to"], **c)
        groups = defaultdict(list)
        for n in self.G: groups[device(n)].append(n)
        self.F = nx.DiGraph()
        for g, members in groups.items():
            types = [self.G.nodes[m].get("IO") for m in members]
            self.F.add_node(g, IO=max(set(types), key=types.count), members=members)
        self.P = nx.DiGraph(); self.FB = nx.DiGraph()
        self.P.add_nodes_from(self.F); self.FB.add_nodes_from(self.F)
        for u, v, d in self.G.edges(data=True):
            gu, gv = device(u), device(v)
            if gu == gv: continue
            if d.get("type") in PATH_TYPES: self.P.add_edge(gu, gv)
            if d.get("type") == "feedback": self.FB.add_edge(gu, gv)
    def type(self, n): return self.F.nodes[n].get("IO", "")
    def channels(self, logic, inp):
        members = self.F.nodes[logic]["members"]
        return sum(1 for u, v, d in self.G.in_edges(members, data=True)
                   if d.get("type") in CHANNEL_TYPES and device(u) == inp)
    def functions(self):
        out = {}
        for i in [n for n in self.F if self.type(n) == "Input"]:
            for m in [n for n in self.F if self.type(n) == "EndEffector"]:
                paths = list(nx.all_simple_paths(self.P, i, m, cutoff=CUTOFF)) if i in self.P and m in self.P else []
                if not paths: continue
                red = len(paths) >= 2
                fb = any(self.type(v) == "Logic" and any(nx.has_path(self.FB, u, v) for u in p[k + 1:])
                         for p in paths for k, v in enumerate(p))
                logic = {n for p in paths for n in p if self.type(n) == "Logic"}
                log = any(self.channels(l, i) >= 2 for l in logic)
                out[(i, m)] = dict(paths=paths, red=red, fb=fb, log=log,
                                   group="3/4" if red and fb and log else "B/1")
        return out

def group_of(els, cons, key):
    try: r = Circuit(els, cons).functions()
    except Exception: return "invalid"
    return r[key]["group"] if key in r else "invalid"

def cmd_classify(files):
    for f in sorted(files):
        md, els, cons = read(f)
        print(f"== {os.path.basename(f)}  reference category: {md.get('category')}")
        for (i, m), r in sorted(Circuit(els, cons).functions().items()):
            print(f"   {i:>6} -> {m:<4} paths={len(r['paths']):<2} red={r['red']!s:<5} "
                  f"fb={r['fb']!s:<5} log={r['log']!s:<5} => {r['group']}")

def cmd_perturb(files):
    stats = defaultdict(Counter); times = []; unsafe = []
    for f in sorted(files):
        _, els, cons = read(f); c = Circuit(els, cons)
        for key, r in c.functions().items():
            i, m = key; g0 = r["group"]
            on = {n for p in r["paths"] for n in p}
            rel = lambda e: device(e["from"]) in on and device(e["to"]) in on
            nonfb = [k for k, e in enumerate(cons) if e["type"] != "feedback" and rel(e)]
            fbe = [k for k, e in enumerate(cons) if e["type"] == "feedback" and (device(e["from"]) in on or device(e["to"]) in on)]
            inner = [x["id"] for x in els if device(x["id"]) in on and device(x["id"]) not in (i, m)]
            logic = sorted(n for n in on if c.type(n) == "Logic")
            drop = lambda ids: ([x for x in els if x["id"] not in ids],
                                [e for e in cons if e["from"] not in ids and e["to"] not in ids])
            V = []
            V += [("Removal of one edge", els, [e for j, e in enumerate(cons) if j != k]) for k in nonfb]
            V += [("Removal of two edges", els, [e for j, e in enumerate(cons) if j not in (a, b)]) for a, b in itertools.combinations(nonfb, 2)]
            V += [("Removal of one element",) + drop({n}) for n in inner]
            V += [("Removal of two elements",) + drop({a, b}) for a, b in itertools.combinations(inner, 2)]
            V += [("Removal of one feedback edge", els, [e for j, e in enumerate(cons) if j != k]) for k in fbe]
            for l in logic:
                nc = [e for e in cons if not (e["type"] == "feedback" and device(e["to"]) == l)]
                if len(nc) < len(cons): V.append(("All feedback of a logic node", els, nc))
            if g0 == "B/1":
                for p in r["paths"]:
                    for k, v in enumerate(p):
                        if c.type(v) == "Logic":
                            V += [("Spurious feedback edge", els, cons + [{"from": u, "to": v, "type": "feedback"}]) for u in p[k + 1:]]
            for kind, ne, nc in V:
                t = time.perf_counter(); g = group_of(ne, nc, key); times.append(time.perf_counter() - t)
                if g == g0: stats[kind]["unchanged"] += 1
                elif g0 == "B/1" and g == "3/4": stats[kind]["unsafe"] += 1; unsafe.append((os.path.basename(f), key, kind))
                else: stats[kind]["safe"] += 1
    order = ["Removal of one edge", "Removal of two edges", "Removal of one element", "Removal of two elements",
             "Removal of one feedback edge", "All feedback of a logic node", "Spurious feedback edge"]
    tot = Counter()
    print(f"{'Perturbation':32s} {'variants':>8} {'safe':>6} {'unsafe':>6} {'unchanged':>9}")
    for k in order:
        s = stats[k]; tot.update(s)
        print(f"{k:32s} {sum(s.values()):8d} {s['safe']:6d} {s['unsafe']:6d} {s['unchanged']:9d}")
    print(f"{'Total':32s} {sum(tot.values()):8d} {tot['safe']:6d} {tot['unsafe']:6d} {tot['unchanged']:9d}")
    times.sort(); print(f"median time per variant: {times[len(times)//2]*1e3:.1f} ms")
    if unsafe: print("UNSAFE:", unsafe)

if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in ("classify", "perturb"):
        print(__doc__); sys.exit(1)
    files = [f for pat in sys.argv[2:] for f in glob.glob(pat)]
    (cmd_classify if sys.argv[1] == "classify" else cmd_perturb)(files)
