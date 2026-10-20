import queue
import tkinter as tk

# The GUI is only fed when it is actually running (see JarvisUI.__init__)
ENABLED = False
_events = queue.Queue()

BG = "#0f172a"
PANEL = "#1e293b"
TEXT = "#e2e8f0"
MUTED = "#94a3b8"
ACCENT = "#38bdf8"

STATUS_COLORS = {
    "Idle": "#64748b",
    "Listening": "#22c55e",
    "Recognizing": "#eab308",
    "Thinking": "#a855f7",
    "Speaking": "#3b82f6",
}


# ---- Thread-safe helpers: any thread may call these -----------------------
def log(role, text):
    """role is 'you' or 'jarvis'."""
    if ENABLED:
        _events.put(("log", role, text))


def status(name):
    if ENABLED:
        _events.put(("status", name, None))


def request_quit():
    if ENABLED:
        _events.put(("quit", None, None))


# ---- The window itself (must run in the main thread) ----------------------
class JarvisUI:
    def __init__(self, on_text_command=None):
        global ENABLED
        ENABLED = True
        self.on_text_command = on_text_command

        self.root = tk.Tk()
        self.root.title("Jarvis")
        self.root.geometry("440x620")
        self.root.configure(bg=BG)
        self.root.minsize(360, 420)

        # Header
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=16, pady=(14, 6))
        tk.Label(header, text="JARVIS", bg=BG, fg=ACCENT,
                 font=("Segoe UI", 18, "bold")).pack(side="left")

        self.status_label = tk.Label(header, text="Idle", bg=BG, fg=MUTED,
                                     font=("Segoe UI", 10))
        self.status_label.pack(side="right")
        self.dot = tk.Canvas(header, width=14, height=14, bg=BG, highlightthickness=0)
        self.dot.pack(side="right", padx=(0, 6))
        self.dot_id = self.dot.create_oval(2, 2, 12, 12, fill=STATUS_COLORS["Idle"], outline="")

        # Conversation area
        body = tk.Frame(self.root, bg=PANEL)
        body.pack(fill="both", expand=True, padx=16, pady=6)

        self.chat = tk.Text(body, bg=PANEL, fg=TEXT, wrap="word", bd=0,
                            padx=12, pady=10, font=("Segoe UI", 11),
                            state="disabled", cursor="arrow")
        scroll = tk.Scrollbar(body, command=self.chat.yview)
        self.chat.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.chat.pack(side="left", fill="both", expand=True)

        self.chat.tag_configure("you_name", foreground="#38bdf8", font=("Segoe UI", 9, "bold"))
        self.chat.tag_configure("jarvis_name", foreground="#4ade80", font=("Segoe UI", 9, "bold"))
        self.chat.tag_configure("msg", spacing3=10)

        # Typed input (handy when you don't want to speak)
        bottom = tk.Frame(self.root, bg=BG)
        bottom.pack(fill="x", padx=16, pady=(6, 14))

        self.entry = tk.Entry(bottom, bg=PANEL, fg=TEXT, insertbackground=TEXT,
                              relief="flat", font=("Segoe UI", 11))
        self.entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 8))
        self.entry.bind("<Return>", self._send)

        tk.Button(bottom, text="Send", command=self._send, bg=ACCENT, fg="#0f172a",
                  relief="flat", font=("Segoe UI", 10, "bold"), padx=14,
                  pady=4).pack(side="right")

        self._add("jarvis", "Hi! Say \"Jarvis\" followed by a command, or type one below.")
        self.root.after(100, self._drain)

    # -- internal -----------------------------------------------------------
    def _add(self, role, text):
        name = "You" if role == "you" else "Jarvis"
        self.chat.configure(state="normal")
        self.chat.insert("end", name + "\n", f"{role}_name")
        self.chat.insert("end", text + "\n", "msg")
        self.chat.configure(state="disabled")
        self.chat.see("end")

    def _set_status(self, name):
        self.status_label.configure(text=name if name == "Idle" else name + "...")
        self.dot.itemconfig(self.dot_id, fill=STATUS_COLORS.get(name, STATUS_COLORS["Idle"]))

    def _send(self, event=None):
        text = self.entry.get().strip()
        if text and self.on_text_command:
            self.entry.delete(0, "end")
            self.on_text_command(text)

    def _drain(self):
        """Runs in the main thread every 100 ms and applies queued updates."""
        try:
            while True:
                kind, a, b = _events.get_nowait()
                if kind == "log":
                    self._add(a, b)
                elif kind == "status":
                    self._set_status(a)
                elif kind == "quit":
                    self.root.destroy()
                    return
        except queue.Empty:
            pass
        self.root.after(100, self._drain)

    def run(self):
        self.root.mainloop()