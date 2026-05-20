#!/usr/bin/env python3
import os
# ===============================================================
# 🔄 AUTO-FIX ENVIRONMENT (v1.0)
# Vérifie et installe automatiquement les modules Python manquants
# ===============================================================
import importlib, subprocess, sys

required = ["watchdog", "psutil", "PIL", "tkinter"]

def ensure_modules():
    missing = []
    for mod in required:
        try:
            importlib.import_module(mod)
        except ModuleNotFoundError:
            missing.append(mod)
    if missing:
        print(f"[AUTO-FIX] Modules manquants détectés: {missing}")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "--break-system-packages"] + missing
            )
            print("[AUTO-FIX] Installation terminée. Redémarrage du moteur...")
            os.execv(sys.executable, [sys.executable] + sys.argv)
        except Exception as e:
            print("[AUTO-FIX] Erreur d'installation automatique:", e)

ensure_modules()
# ===============================================================
# coding: utf-8
"""
CPCDOS Engine - Full IUG Bridge (Wayland compatible)
Version stable - 2025
"""
import os, sys, time, threading, subprocess, re, traceback
from pathlib import Path
import json

# ===============================================================
# ⚙️ Configuration
# ===============================================================
HOME = str(Path.home())
ENGINE_HOME = os.path.join(HOME, ".cpc_engine")
OUTBOX = os.path.join(HOME, ".cpc_outbox")
INBOX = os.path.join(HOME, ".cpc_inbox")
HELPER = os.path.join(ENGINE_HOME, "cpcdos_helper")
ENABLE_GLOBAL_WATCH = True   # ← change à True si tu veux surveiller tout le disque

# ===============================================================
# 🧩 Fonctions utilitaires
# ===============================================================
def log(*a):
    print("[ENGINE]", *a)
    try:
        with open(os.path.join(ENGINE_HOME, "engine.log"), "a", encoding="utf-8") as f:
            f.write(f"[{time.ctime()}] " + " ".join(map(str, a)) + "\n")
    except Exception:
        pass

vars_by_level = {1:{},2:{},3:{},4:{},5:{}}
def set_var(name, val, level=2): vars_by_level[level][name] = val
def get_var(name):
    for lv in range(5,0,-1):
        if name in vars_by_level[lv]: return vars_by_level[lv][name]
    return None

sub_re = re.compile(r'\$\{([^}]+)\}')
def substitute(s):
    if not isinstance(s, str): return s
    def repl(m):
        key = m.group(1)
        return str(get_var(key) or "")
    return sub_re.sub(repl, s)

# ===============================================================
# 🧾 Parser CPC
# ===============================================================
def parse_cpc(path):
    blocks, functions = [], {}
    cur, cur_props, in_func, func_name, func_lines = None, {}, False, None, []
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        for raw in f:
            s = raw.strip()
            if not s: continue
            if s.lower().startswith("function/"):
                in_func, func_name, func_lines = True, s.split("/",1)[1].strip(), []
                continue
            if in_func:
                if s.lower().startswith("end/function"):
                    functions[func_name] = func_lines[:]
                    in_func = False
                else: func_lines.append(raw)
                continue
            if '/' in s and s.split('/',1)[0].lower() in (
                "window","button","picturebox","textblock","textbox","progressbar","listbox","explorer","checkbox","msgbox"):
                t = s.split('/',1)[0].lower()
                name = s.split('/',1)[1].strip()
                cur = {'type':t,'name':name,'props':{}}
                continue
            if s.startswith(".") and "=" in s and cur:
                k,v = s.split("=",1)
                cur['props'][k.strip().lstrip('.')] = v.strip().strip('"')
                continue
            if s.lower().startswith("end/") and cur:
                blocks.append(cur.copy()); cur=None
    return blocks, functions

# ===============================================================
# 🪟 GUI Driver
# ===============================================================
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

class EngineGUI:
    def __init__(self):
        self.windows, self.widgets, self.functions = {}, {}, {}

    def new_handle(self): return f"H{len(self.windows)+len(self.widgets)+1}"

    def create_window(self, name, props):
        title = substitute(props.get("title") or name)
        sx, sy = int(props.get("sx",420)), int(props.get("sy",260))
        px, py = int(props.get("px",80)), int(props.get("py",60))
        bg = props.get("BackColor","200,200,200")
        try: r,g,b=[int(x) for x in bg.split(",")]; hexcol=f"#{r:02x}{g:02x}{b:02x}"
        except: hexcol="#C8C8C8"
        root = tk.Toplevel() if self.windows else tk.Tk()
        root.title(title); root.geometry(f"{sx}x{sy}+{px}+{py}"); root.configure(bg=hexcol)
        h = self.new_handle(); self.windows[h]=root; set_var(name,h,4)
        log(f"Window created {name} -> {h}")
        return h

    def create_button(self, parent, name, props):
        p = self._resolve_parent(parent)
        txt = substitute(props.get("text",name))
        px,py,sx,sy = [int(props.get(k,10)) for k in ("px","py","sx","sy")]
        btn = tk.Button(p, text=txt)
        btn.place(x=px,y=py,width=sx,height=sy)
        h=self.new_handle(); self.widgets[h]=btn
        return h

    def _resolve_parent(self, ph):
        if not ph and self.windows: return list(self.windows.values())[-1]
        if ph in self.windows: return self.windows[ph]
        if ph in vars_by_level[4]: 
            val=get_var(ph)
            if val in self.windows: return self.windows[val]
        return list(self.windows.values())[-1] if self.windows else tk.Tk()

engine_gui = EngineGUI()

# ===============================================================
# 🧠 Runner
# ===============================================================
def run_blocks(blocks, functions):
    for k,v in functions.items(): engine_gui.functions[k]=v
    created_windows=[]
    for b in blocks:
        if b["type"].lower()=="window":
            h=engine_gui.create_window(b["name"], b["props"])
            created_windows.append(h)
    for b in blocks:
        t=b["type"].lower()
        if t=="window": continue
        parent = b["props"].get("handle") or (created_windows[-1] if created_windows else None)
        if t=="button":
            engine_gui.create_button(parent,b["name"],b["props"])
        elif t=="msgbox":
            messagebox.showinfo("CPCDOS", substitute(b["name"]))
        else:
            log("Type non géré:",t)

def run_cpc_file(path):
    try:
        blocks, functions = parse_cpc(path)
        run_blocks(blocks, functions)
    except Exception as e:
        log("Erreur exécution:", e)
        traceback.print_exc()

# ===============================================================
# 👀 Watcher .cpc_outbox
# ===============================================================
def watcher_loop():
    Path(OUTBOX).mkdir(parents=True, exist_ok=True)
    log("Watcher démarré sur:", OUTBOX)
    while True:
        for f in os.listdir(OUTBOX):
            fp = os.path.join(OUTBOX,f)
            if os.path.isfile(fp):
                log("Fichier détecté:",fp)
                run_cpc_file(fp)
                os.remove(fp)
        time.sleep(0.8)

# ===============================================================
# 🌍 Surveillance globale (optionnelle)
# ===============================================================
if ENABLE_GLOBAL_WATCH:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    class GlobalWatcher(FileSystemEventHandler):
        def on_created(self, event):
            if not event.is_directory and event.src_path.lower().endswith(".cpc"):
                os.system(f"notify-send '🧩 Bridge CPCDOS' 'Script détecté : {os.path.basename(event.src_path)}'")
                run_cpc_file(event.src_path)
    obs=Observer(); handler=GlobalWatcher()
    for d in os.listdir("/"):
        p=os.path.join("/",d)
        if os.path.isdir(p) and d not in ("proc","sys","run","dev"):
            try: obs.schedule(handler,p,recursive=True)
            except: pass
    obs.start()
    log("🌍 Surveillance globale activée.")

# ===============================================================
# 🚀 Main
# ===============================================================
def main():
    log("CPCDOS Engine (Full) démarré.")
    threading.Thread(target=watcher_loop, daemon=True).start()
    root = tk.Tk(); root.withdraw(); root.mainloop()

if __name__ == "__main__":
    main()

