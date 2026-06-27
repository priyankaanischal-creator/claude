#!/usr/bin/env python3
"""
gui.py  --  Footage Collector (simple desktop app)
==================================================
A no-terminal window for the footage collector. Paste your title, pick your
visual instructor file (and optional clean script), choose a few options, and
click "Generate Footage". It runs collector.py under the hood and streams the
progress into the window.

Run it with:   python gui.py     (or double-click run.bat on Windows)

Tkinter ships with Python, so no extra install is needed for the window itself.
"""

from __future__ import annotations

import os
import queue
import subprocess
import sys
import threading

import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext

HERE = os.path.dirname(os.path.abspath(__file__))


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("Footage Collector")
        root.geometry("760x680")
        self.proc = None
        self.log_q: "queue.Queue[str]" = queue.Queue()

        pad = {"padx": 8, "pady": 4}
        frm = ttk.Frame(root, padding=10)
        frm.pack(fill="both", expand=True)

        row = 0
        ttk.Label(frm, text="Video title").grid(row=row, column=0, sticky="w", **pad)
        self.title_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.title_var, width=60).grid(
            row=row, column=1, columnspan=2, sticky="we", **pad)

        row += 1
        ttk.Label(frm, text="Topic / context\n(e.g. The Thing 1982)").grid(
            row=row, column=0, sticky="w", **pad)
        self.context_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.context_var, width=60).grid(
            row=row, column=1, columnspan=2, sticky="we", **pad)

        row += 1
        ttk.Label(frm, text="Visual instructor file").grid(row=row, column=0, sticky="w", **pad)
        self.instructor_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.instructor_var, width=48).grid(
            row=row, column=1, sticky="we", **pad)
        ttk.Button(frm, text="Browse…",
                   command=lambda: self._pick(self.instructor_var)).grid(row=row, column=2, **pad)

        row += 1
        ttk.Label(frm, text="Clean script (optional)").grid(row=row, column=0, sticky="w", **pad)
        self.script_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.script_var, width=48).grid(
            row=row, column=1, sticky="we", **pad)
        ttk.Button(frm, text="Browse…",
                   command=lambda: self._pick(self.script_var)).grid(row=row, column=2, **pad)

        row += 1
        ttk.Label(frm, text="Output folder").grid(row=row, column=0, sticky="w", **pad)
        self.out_var = tk.StringVar(value=os.path.join(HERE, "output"))
        ttk.Entry(frm, textvariable=self.out_var, width=48).grid(row=row, column=1, sticky="we", **pad)
        ttk.Button(frm, text="Browse…",
                   command=lambda: self._pick_dir(self.out_var)).grid(row=row, column=2, **pad)

        # options row
        row += 1
        opt = ttk.LabelFrame(frm, text="Options", padding=8)
        opt.grid(row=row, column=0, columnspan=3, sticky="we", **pad)

        ttk.Label(opt, text="Clips / scene").grid(row=0, column=0, sticky="w", padx=6)
        self.clips_var = tk.IntVar(value=2)
        ttk.Spinbox(opt, from_=0, to=5, width=5, textvariable=self.clips_var).grid(row=0, column=1, padx=6)

        ttk.Label(opt, text="Images / scene").grid(row=0, column=2, sticky="w", padx=6)
        self.images_var = tk.IntVar(value=4)
        ttk.Spinbox(opt, from_=0, to=10, width=5, textvariable=self.images_var).grid(row=0, column=3, padx=6)

        ttk.Label(opt, text="Clip length (sec)").grid(row=0, column=4, sticky="w", padx=6)
        self.dur_var = tk.IntVar(value=5)
        ttk.Spinbox(opt, from_=3, to=10, width=5, textvariable=self.dur_var).grid(row=0, column=5, padx=6)

        ttk.Label(opt, text="Frames / clip").grid(row=0, column=6, sticky="w", padx=6)
        self.frames_var = tk.IntVar(value=2)
        ttk.Spinbox(opt, from_=0, to=6, width=5, textvariable=self.frames_var).grid(row=0, column=7, padx=6)

        ttk.Label(opt, text="YouTube login (for clips)").grid(row=1, column=0, columnspan=2, sticky="w", padx=6, pady=6)
        self.cookies_var = tk.StringVar(value="none")
        ttk.Combobox(opt, textvariable=self.cookies_var, width=12, state="readonly",
                     values=["none", "chrome", "edge", "firefox", "brave", "opera"]).grid(
            row=1, column=2, padx=6, pady=6)
        ttk.Label(opt, text="(browser jisme YouTube logged-in ho; us browser ko BAND rakho)").grid(
            row=1, column=3, columnspan=3, sticky="w", padx=6)

        ttk.Label(opt, text="OR cookies.txt file\n(most reliable)").grid(
            row=2, column=0, columnspan=2, sticky="w", padx=6, pady=6)
        self.cookies_file_var = tk.StringVar()
        ttk.Entry(opt, textvariable=self.cookies_file_var, width=30).grid(
            row=2, column=2, columnspan=2, padx=6, pady=6, sticky="we")
        ttk.Button(opt, text="Browse…",
                   command=lambda: self._pick(self.cookies_file_var)).grid(row=2, column=4, padx=6)

        # buttons
        row += 1
        btns = ttk.Frame(frm)
        btns.grid(row=row, column=0, columnspan=3, sticky="we", **pad)
        self.run_btn = ttk.Button(btns, text="▶  Generate Footage", command=self.start)
        self.run_btn.pack(side="left", padx=4)
        self.stop_btn = ttk.Button(btns, text="■ Stop", command=self.stop, state="disabled")
        self.stop_btn.pack(side="left", padx=4)
        ttk.Button(btns, text="Open output folder", command=self.open_output).pack(side="left", padx=4)

        # log
        row += 1
        ttk.Label(frm, text="Progress").grid(row=row, column=0, sticky="w", **pad)
        row += 1
        self.log = scrolledtext.ScrolledText(frm, height=18, wrap="word", state="disabled")
        self.log.grid(row=row, column=0, columnspan=3, sticky="nsew", **pad)
        frm.rowconfigure(row, weight=1)
        frm.columnconfigure(1, weight=1)

        self.root.after(100, self._drain_log)

    # --- helpers ---
    def _pick(self, var):
        p = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if p:
            var.set(p)

    def _pick_dir(self, var):
        p = filedialog.askdirectory()
        if p:
            var.set(p)

    def _append(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text)
        self.log.see("end")
        self.log.configure(state="disabled")

    def _drain_log(self):
        try:
            while True:
                self._append(self.log_q.get_nowait())
        except queue.Empty:
            pass
        self.root.after(100, self._drain_log)

    def open_output(self):
        out = self.out_var.get()
        os.makedirs(out, exist_ok=True)
        if sys.platform.startswith("win"):
            os.startfile(out)  # type: ignore
        elif sys.platform == "darwin":
            subprocess.Popen(["open", out])
        else:
            subprocess.Popen(["xdg-open", out])

    # --- run ---
    def start(self):
        if self.proc is not None:
            return
        instructor = self.instructor_var.get().strip()
        if not instructor or not os.path.isfile(instructor):
            messagebox.showerror("Missing file", "Please pick a valid visual instructor file.")
            return

        cmd = [sys.executable, os.path.join(HERE, "collector.py"),
               "--instructor", instructor,
               "--out", self.out_var.get().strip() or os.path.join(HERE, "output"),
               "--clips-per-scene", str(self.clips_var.get()),
               "--images-per-scene", str(self.images_var.get()),
               "--clip-duration", str(self.dur_var.get()),
               "--frames-per-clip", str(self.frames_var.get())]
        if self.script_var.get().strip():
            cmd += ["--script", self.script_var.get().strip()]
        if self.context_var.get().strip():
            cmd += ["--context", self.context_var.get().strip()]
        if self.title_var.get().strip():
            cmd += ["--title", self.title_var.get().strip()]
        if self.cookies_file_var.get().strip():
            cmd += ["--cookies", self.cookies_file_var.get().strip()]
        elif self.cookies_var.get() != "none":
            cmd += ["--cookies-from-browser", self.cookies_var.get()]

        self._append("\n$ " + " ".join(f'"{c}"' if " " in c else c for c in cmd) + "\n\n")
        self.run_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        threading.Thread(target=self._run, args=(cmd,), daemon=True).start()

    def _run(self, cmd):
        try:
            self.proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1, cwd=HERE)
            for line in self.proc.stdout:
                self.log_q.put(line)
            self.proc.wait()
            self.log_q.put("\n--- finished ---\n")
        except Exception as e:
            self.log_q.put(f"\nERROR: {e}\n")
        finally:
            self.proc = None
            self.root.after(0, self._reset_buttons)

    def _reset_buttons(self):
        self.run_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")

    def stop(self):
        if self.proc is not None:
            try:
                self.proc.terminate()
            except Exception:
                pass
            self.log_q.put("\n--- stopped by user ---\n")


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
