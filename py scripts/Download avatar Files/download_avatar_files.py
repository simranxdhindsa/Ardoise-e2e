import json
import urllib.request
import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading

# ---------------------------
# Utilities
# ---------------------------

def get_downloads_folder():
    return os.path.join(os.path.expanduser("~"), "Downloads")

def detect_extension(url):
    url = url.lower()
    if ".png" in url:
        return ".png"
    if ".jpg" in url or ".jpeg" in url:
        return ".jpg"
    return ".png"  # fallback

def download_file(url, path, log):
    try:
        log(f"Downloading: {os.path.basename(path)}")
        urllib.request.urlretrieve(url, path)
        log(f"Saved: {path}")
    except Exception as e:
        log(f"❌ Failed to download {url}")
        log(str(e))

# ---------------------------
# Core Logic
# ---------------------------

def validate_json_structure(parsed):
    if "data" not in parsed:
        raise ValueError("Missing 'data' key")

    inner = parsed["data"]
    required_fields = ["data", "framework", "loader", "wasm"]

    for field in required_fields:
        if field not in inner or not inner[field]:
            raise ValueError(f"Missing or empty field: {field}")

    return inner

def parse_curl(curl_text):
    """
    Parse a curl command (bash or cmd style) and return (url, headers).
    Handles both single-quoted (bash) and double-quoted (cmd) -H values,
    plus backslash line continuations.
    """
    # Normalize line continuations: remove trailing \ and newlines
    text = curl_text.strip()
    text = text.replace("\\\n", " ").replace("\\\r\n", " ")

    url = None
    headers = {}

    # Extract URL — first token after 'curl' that looks like http(s)://
    url_match = __import__("re").search(r"""['"](https?://[^'"]+)['"]""", text)
    if url_match:
        url = url_match.group(1)

    # Extract all -H values (handles both 'Name: value' and "Name: value")
    for m in __import__("re").finditer(r"""-H\s+['"](.*?)['"](?=\s|$)""", text):
        header = m.group(1)
        if ":" in header:
            name, _, value = header.partition(":")
            headers[name.strip()] = value.strip()

    return url, headers


def run_download(raw_input, input_mode, avatar_name_override, log, on_done):
    try:
        if input_mode == "curl":
            url, headers = parse_curl(raw_input)
            if not url:
                log("❌ Could not extract URL from curl command.")
                on_done(False)
                return

            log(f"Fetching: {url}")
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req) as resp:
                    raw_json = resp.read().decode("utf-8")
            except Exception as e:
                log(f"❌ Request failed: {e}")
                on_done(False)
                return

            if not raw_json.strip().startswith("{"):
                log("❌ Response is not JSON (probably HTML/error page).")
                log(raw_json[:300])
                on_done(False)
                return
        else:
            raw_json = raw_input

        try:
            parsed_json = json.loads(raw_json)
        except json.JSONDecodeError:
            log("❌ Invalid JSON format.")
            on_done(False)
            return

        try:
            data = validate_json_structure(parsed_json)
        except ValueError as e:
            log(f"❌ JSON structure error: {e}")
            on_done(False)
            return

        # Avatar name
        detected_name = data.get("name", "").strip()
        avatar_name = avatar_name_override.strip() if avatar_name_override.strip() else detected_name.split("(")[0].strip()

        if not avatar_name:
            log("❌ Avatar name cannot be empty.")
            on_done(False)
            return

        version = data.get("description", "").split("_")[-1]
        base_name = f"{avatar_name} {version}" if version else avatar_name

        downloads = get_downloads_folder()
        folder_path = os.path.join(downloads, avatar_name)
        os.makedirs(folder_path, exist_ok=True)

        log(f"\nSaving files to: {folder_path}\n")

        files = {
            f"{base_name}.data": data.get("data"),
            f"{base_name}.framework.js": data.get("framework"),
            f"{base_name}.loader.js": data.get("loader"),
            f"{base_name}.wasm": data.get("wasm"),
        }

        for filename, url in files.items():
            if url:
                download_file(url, os.path.join(folder_path, filename), log)

        avatar_url = data.get("avatar_display")
        if avatar_url:
            ext = detect_extension(avatar_url)
            image_name = f"{avatar_name}{ext}"
            download_file(avatar_url, os.path.join(folder_path, image_name), log)

        log("\n✅ All done. Files are neatly organized for once in their life.")
        on_done(True)

    except Exception as e:
        log(f"❌ Unexpected error: {e}")
        on_done(False)

# ---------------------------
# GUI
# ---------------------------

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Avatar File Downloader")
        self.resizable(True, True)
        self.minsize(600, 500)
        self._build_ui()

    def _build_ui(self):
        pad = {"padx": 10, "pady": 5}

        # Mode selector
        mode_frame = ttk.LabelFrame(self, text="Input Method")
        mode_frame.pack(fill="x", **pad)

        self.mode = tk.StringVar(value="json")
        ttk.Radiobutton(mode_frame, text="Paste JSON", variable=self.mode, value="json", command=self._on_mode_change).pack(side="left", padx=10, pady=5)
        ttk.Radiobutton(mode_frame, text="Execute CURL", variable=self.mode, value="curl", command=self._on_mode_change).pack(side="left", padx=10, pady=5)

        # Input area
        self.input_label = ttk.Label(self, text="Paste JSON below:")
        self.input_label.pack(anchor="w", **pad)

        self.input_box = scrolledtext.ScrolledText(self, height=10, font=("Consolas", 9))
        self.input_box.pack(fill="both", expand=True, padx=10)

        # Avatar name override
        name_frame = ttk.Frame(self)
        name_frame.pack(fill="x", **pad)
        ttk.Label(name_frame, text="Avatar name (leave blank to auto-detect):").pack(side="left")
        self.name_entry = ttk.Entry(name_frame, width=30)
        self.name_entry.pack(side="left", padx=5)

        # Run button
        self.run_btn = ttk.Button(self, text="▶  Download", command=self._on_run)
        self.run_btn.pack(pady=8)

        # Output log
        ttk.Label(self, text="Output:").pack(anchor="w", padx=10)
        self.output_box = scrolledtext.ScrolledText(self, height=10, state="disabled", font=("Consolas", 9), bg="#1e1e1e", fg="#d4d4d4")
        self.output_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _on_mode_change(self):
        if self.mode.get() == "curl":
            self.input_label.config(text="Paste CURL command below:")
        else:
            self.input_label.config(text="Paste JSON below:")

    def _log(self, message):
        self.output_box.config(state="normal")
        self.output_box.insert("end", message + "\n")
        self.output_box.see("end")
        self.output_box.config(state="disabled")

    def _on_run(self):
        raw_input = self.input_box.get("1.0", "end").strip()
        if not raw_input:
            messagebox.showwarning("Missing Input", "Please paste your CURL command or JSON first.")
            return

        self.output_box.config(state="normal")
        self.output_box.delete("1.0", "end")
        self.output_box.config(state="disabled")

        self.run_btn.config(state="disabled", text="Downloading...")

        avatar_name_override = self.name_entry.get()
        mode = self.mode.get()

        def on_done(_):
            self.after(0, lambda: self.run_btn.config(state="normal", text="▶  Download"))

        threading.Thread(
            target=run_download,
            args=(raw_input, mode, avatar_name_override, lambda msg: self.after(0, lambda m=msg: self._log(m)), on_done),
            daemon=True
        ).start()

# ---------------------------

if __name__ == "__main__":
    app = App()
    app.mainloop()
