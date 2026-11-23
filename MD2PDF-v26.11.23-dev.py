import sys
import os
import subprocess
import importlib
import importlib.util
import threading
import platform
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


# ============================================================
#  DEPENDENCY MANAGER
# ============================================================
REQUIRED_PACKAGES = [
    ("markdown",  "markdown",  "Markdown → HTML parser"),
    ("xhtml2pdf", "xhtml2pdf", "HTML → PDF converter"),
]


def is_installed(module_name: str) -> bool:
    """Cek apakah module bisa di-import."""
    try:
        return importlib.util.find_spec(module_name) is not None
    except (ImportError, ValueError, ModuleNotFoundError):
        return False


def get_missing_packages():
    """Return list of (module, pip_name, desc) yang belum terinstall."""
    return [p for p in REQUIRED_PACKAGES if not is_installed(p[0])]


def install_package(pip_name: str, log_callback=None):
    """Install package via pip di subprocess. Return (success, output)."""
    try:
        proc = subprocess.Popen(
            [sys.executable, "-m", "pip", "install", "--upgrade", pip_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        output_lines = []
        for line in proc.stdout:
            output_lines.append(line)
            if log_callback:
                log_callback(line)
        proc.wait()
        return proc.returncode == 0, "".join(output_lines)
    except Exception as e:
        return False, str(e)


class DependencyInstaller:
    """Bootstrap window: cek + install dependencies sebelum app utama jalan."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🔧 Setup Dependencies - MD to PDF")
        self.root.geometry("720x440")
        self.root.configure(bg="#f0f0f0")
        self.root.resizable(False, False)
        self.ok = False
        self._build_ui()
        self.root.after(200, self._check)

    def _build_ui(self):
        tk.Label(
            self.root, text="🔧 Pemeriksaan Dependencies",
            font=("Segoe UI", 16, "bold"), bg="#f0f0f0", fg="#2c3e50"
        ).pack(pady=(18, 6))

        self.status_var = tk.StringVar(value="Memeriksa dependencies...")
        tk.Label(
            self.root, textvariable=self.status_var,
            font=("Segoe UI", 10, "bold"), bg="#f0f0f0", fg="#555"
        ).pack(pady=(0, 10))

        self.progress = ttk.Progressbar(
            self.root, mode="indeterminate", length=660
        )
        self.progress.pack(pady=(0, 10), padx=20, fill="x")

        log_frame = tk.Frame(self.root)
        log_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        self.log_text = tk.Text(
            log_frame, wrap="word", font=("Consolas", 8),
            bg="#1e1e1e", fg="#d4d4d4", relief="flat",
            insertbackground="white"
        )
        sb = tk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.log_text.pack(side="left", fill="both", expand=True)

        self.btn_continue = tk.Button(
            self.root, text="⏳ Memeriksa...",
            command=self._finish,
            bg="#4CAF50", fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=20, pady=6, relief="flat",
            cursor="hand2", state="disabled"
        )
        self.btn_continue.pack(pady=(0, 15))

    def _log(self, msg: str):
        self.log_text.insert("end", msg)
        self.log_text.see("end")
        self.root.update_idletasks()

    def _check(self):
        missing = get_missing_packages()

        if not missing:
            self._log("✅ Semua dependencies sudah terinstall:\n")
            for _, pip_name, desc in REQUIRED_PACKAGES:
                self._log(f"   ✓ {pip_name:12s}  ({desc})\n")
            self.status_var.set("✅ Dependencies lengkap!")
            self._enable_continue()
            return

        self.status_var.set(f"⚠️ {len(missing)} package belum terinstall")
        self._log("⚠️ Dependencies berikut belum terinstall:\n")
        for _, pip_name, desc in missing:
            self._log(f"   ✗ {pip_name:12s}  ({desc})\n")
        self._log("\n")

        answer = messagebox.askyesno(
            "Install Dependencies",
            "Package berikut belum terinstall:\n\n" +
            "\n".join(f"   • {p[0]}  ({p[2]})" for p in missing) +
            "\n\nInstall otomatis sekarang?\n"
            "(Membutuhkan koneksi internet)",
            parent=self.root
        )

        if not answer:
            self._log("❌ Instalasi dibatalkan oleh user.\n")
            messagebox.showwarning(
                "Dibatalkan",
                "Aplikasi membutuhkan dependencies ini.\n"
                "Silakan install manual:\n\n"
                "    pip install markdown xhtml2pdf",
                parent=self.root
            )
            self.root.after(500, self._abort)
            return

        self._install_all(missing)

    def _install_all(self, missing):
        self.progress.start(10)
        self.status_var.set(f"📦 Menginstall {len(missing)} package...")
        self.btn_continue.config(state="disabled", text="⏳ Installing...")

        def worker():
            all_ok = True
            for _, pip_name, _ in missing:
                self.root.after(0, lambda p=pip_name: self._log(
                    f"\n{'─' * 60}\n$ python -m pip install --upgrade {p}\n{'─' * 60}\n"
                ))
                ok, _ = install_package(
                    pip_name,
                    log_callback=lambda line: self.root.after(
                        0, lambda l=line: self._log(l)
                    ),
                )
                if ok:
                    self.root.after(0, lambda p=pip_name: self._log(
                        f"\n✅ {p} berhasil diinstall.\n"
                    ))
                else:
                    self.root.after(0, lambda p=pip_name: self._log(
                        f"\n❌ {p} GAGAL diinstall.\n"
                    ))
                    all_ok = False
            self.root.after(0, lambda: self._after_install(all_ok))

        threading.Thread(target=worker, daemon=True).start()

    def _after_install(self, all_ok: bool):
        self.progress.stop()

        if not all_ok:
            self.status_var.set("❌ Instalasi gagal")
            messagebox.showerror(
                "Install Error",
                "Beberapa package gagal diinstall.\n"
                "Cek log untuk detail. Install manual:\n\n"
                "    pip install markdown xhtml2pdf",
                parent=self.root
            )
            self.root.after(500, self._abort)
            return

        # Re-check setelah invalidate cache (penting!)
        importlib.invalidate_caches()
        still_missing = get_missing_packages()

        if still_missing:
            names = ", ".join(p[1] for p in still_missing)
            self.status_var.set("❌ Package belum terdeteksi")
            messagebox.showerror(
                "Restart Required",
                f"Package sudah diinstall tapi belum terdeteksi: {names}\n\n"
                "Coba tutup dan buka ulang aplikasi.",
                parent=self.root
            )
            self.root.after(500, self._abort)
            return

        self.status_var.set("✅ Semua dependencies siap!")
        self._log("\n✅ Semua dependencies berhasil diinstall.\n")
        self._enable_continue()

    def _enable_continue(self):
        self.btn_continue.config(
            state="normal", text="▶  Lanjutkan ke Aplikasi",
            bg="#4CAF50"
        )

    def _finish(self):
        self.ok = True
        self.root.destroy()

    def _abort(self):
        self.ok = False
        self.root.destroy()


# ============================================================
#  MAIN APP
# ============================================================
class MDtoPDFConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("📄 Markdown to PDF Converter")
        self.root.geometry("750x620")
        self.root.configure(bg="#f0f0f0")
        self.root.minsize(650, 500)
        self.md_file = None
        self._build_ui()

    def _build_ui(self):
        tk.Label(
            self.root, text="📄 Markdown → PDF Converter",
            font=("Segoe UI", 18, "bold"),
            bg="#f0f0f0", fg="#2c3e50"
        ).pack(pady=(15, 10))

        # --- Input Frame ---
        input_frame = tk.LabelFrame(
            self.root, text=" 📂 File Input ",
            font=("Segoe UI", 10, "bold"),
            bg="#f0f0f0", padx=10, pady=10
        )
        input_frame.pack(fill="x", padx=20, pady=5)

        self.md_path_var = tk.StringVar(value="Belum ada file dipilih")
        tk.Label(
            input_frame, textvariable=self.md_path_var,
            bg="white", anchor="w", relief="sunken",
            padx=8, pady=5, font=("Consolas", 9)
        ).pack(fill="x", pady=(0, 8))

        tk.Button(
            input_frame, text="📂 Pilih MD File",
            command=self.select_md,
            bg="#4CAF50", fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=18, pady=6, relief="flat", cursor="hand2"
        ).pack(anchor="w")

        # --- Output Frame ---
        output_frame = tk.LabelFrame(
            self.root, text=" 💾 File Output ",
            font=("Segoe UI", 10, "bold"),
            bg="#f0f0f0", padx=10, pady=10
        )
        output_frame.pack(fill="x", padx=20, pady=5)

        self.pdf_path_var = tk.StringVar(value="Belum ada file output dipilih")
        tk.Label(
            output_frame, textvariable=self.pdf_path_var,
            bg="white", anchor="w", relief="sunken",
            padx=8, pady=5, font=("Consolas", 9)
        ).pack(fill="x", pady=(0, 8))

        tk.Button(
            output_frame, text="💾 Pilih Lokasi Simpan",
            command=self.select_output,
            bg="#2196F3", fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=18, pady=6, relief="flat", cursor="hand2"
        ).pack(anchor="w")

        # --- Preview Frame ---
        preview_frame = tk.LabelFrame(
            self.root, text=" 👁️ Preview Markdown ",
            font=("Segoe UI", 10, "bold"),
            bg="#f0f0f0", padx=10, pady=10
        )
        preview_frame.pack(fill="both", expand=True, padx=20, pady=5)

        text_container = tk.Frame(preview_frame)
        text_container.pack(fill="both", expand=True)

        self.preview_text = tk.Text(
            text_container, wrap="word", font=("Consolas", 9),
            bg="#fafafa", state="disabled", relief="sunken", borderwidth=1
        )
        scrollbar = tk.Scrollbar(text_container, command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.preview_text.pack(side="left", fill="both", expand=True)

        # --- Bottom Bar ---
        bottom_frame = tk.Frame(self.root, bg="#f0f0f0")
        bottom_frame.pack(fill="x", padx=20, pady=12)

        self.convert_btn = tk.Button(
            bottom_frame, text="🔄  Convert to PDF",
            command=self.convert,
            bg="#FF9800", fg="white",
            font=("Segoe UI", 12, "bold"),
            padx=28, pady=10, relief="flat", cursor="hand2"
        )
        self.convert_btn.pack(side="left")

        self.status_var = tk.StringVar(value="✅ Ready")
        tk.Label(
            bottom_frame, textvariable=self.status_var,
            bg="#f0f0f0", font=("Segoe UI", 10, "italic"), fg="#555"
        ).pack(side="left", padx=20)

    def select_md(self):
        file = filedialog.askopenfilename(
            title="Pilih Markdown File",
            filetypes=[
                ("Markdown Files", "*.md *.markdown"),
                ("All Files", "*.*")
            ]
        )
        if file:
            self.md_file = file
            self.md_path_var.set(file)
            pdf_path = os.path.splitext(file)[0] + ".pdf"
            self.pdf_path_var.set(pdf_path)
            self.load_preview(file)

    def load_preview(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self.preview_text.config(state="normal")
            self.preview_text.delete("1.0", "end")
            self.preview_text.insert("end", content)
            self.preview_text.config(state="disabled")
            self.status_var.set(f"📖 Loaded: {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membaca file:\n{e}")

    def select_output(self):
        file = filedialog.asksaveasfilename(
            title="Simpan PDF Sebagai",
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")]
        )
        if file:
            self.pdf_path_var.set(file)

    def convert(self):
        if not self.md_file:
            messagebox.showwarning("Peringatan", "Pilih file Markdown dulu!")
            return
        pdf_path = self.pdf_path_var.get()
        if not pdf_path or pdf_path == "Belum ada file output dipilih":
            messagebox.showwarning("Peringatan", "Pilih lokasi simpan PDF dulu!")
            return
        self.convert_btn.config(state="disabled", text="⏳  Converting...")
        self.status_var.set("⏳ Sedang convert...")
        self.root.update()
        threading.Thread(
            target=self._do_convert,
            args=(self.md_file, pdf_path), daemon=True
        ).start()

    def _do_convert(self, md_path, pdf_path):
        # Import di sini — aman karena bootstrap sudah memastikan terinstall
        try:
            import markdown
            from xhtml2pdf import pisa
        except ImportError as e:
            self.root.after(0, lambda: self._on_error(
                f"Dependency hilang: {e}\nJalankan ulang aplikasi untuk install ulang."
            ))
            return

        try:
            with open(md_path, "r", encoding="utf-8") as f:
                md_content = f.read()

            html_body = markdown.markdown(
                md_content,
                extensions=["extra", "tables", "fenced_code", "toc", "nl2br"]
            )

            html_full = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
    @page {{ size: A4; margin: 2cm; }}
    body {{ font-family: Helvetica, Arial, sans-serif; font-size: 11pt;
            line-height: 1.6; color: #333; }}
    h1 {{ color: #1a1a1a; border-bottom: 2px solid #4CAF50; padding-bottom: 5px; }}
    h2 {{ color: #2c3e50; border-bottom: 1px solid #ddd; padding-bottom: 3px; }}
    h3 {{ color: #34495e; }}
    code {{ background-color: #f4f4f4; padding: 2px 4px;
            font-family: Courier, monospace; font-size: 10pt; }}
    pre {{ background-color: #f4f4f4; padding: 10px;
           border-left: 4px solid #4CAF50;
           font-family: Courier, monospace; font-size: 9pt; }}
    pre code {{ background-color: transparent; padding: 0; }}
    blockquote {{ border-left: 4px solid #ccc; margin: 0;
                  padding-left: 15px; color: #666; font-style: italic; }}
    table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
    th {{ background-color: #4CAF50; color: white; }}
    tr:nth-child(even) {{ background-color: #f9f9f9; }}
    a {{ color: #2196F3; text-decoration: none; }}
    img {{ max-width: 100%; }}
    hr {{ border: none; border-top: 1px solid #ddd; }}
</style>
</head>
<body>{html_body}</body>
</html>"""

            with open(pdf_path, "wb") as pdf_file:
                status = pisa.CreatePDF(html_full, dest=pdf_file, encoding="utf-8")

            if status.err:
                raise Exception(f"PDF generation error (code: {status.err})")

            self.root.after(0, lambda: self._on_success(pdf_path))
        except Exception as e:
            self.root.after(0, lambda: self._on_error(str(e)))

    def _on_success(self, pdf_path):
        self.convert_btn.config(state="normal", text="🔄  Convert to PDF")
        self.status_var.set("✅ Berhasil dibuat!")
        messagebox.showinfo("Sukses", f"PDF berhasil dibuat:\n{pdf_path}")
        if messagebox.askyesno("Buka File?", "Buka file PDF sekarang?"):
            try:
                if platform.system() == "Windows":
                    os.startfile(pdf_path)
                elif platform.system() == "Darwin":
                    subprocess.call(["open", pdf_path])
                else:
                    subprocess.call(["xdg-open", pdf_path])
            except Exception:
                pass

    def _on_error(self, err):
        self.convert_btn.config(state="normal", text="🔄  Convert to PDF")
        self.status_var.set("❌ Gagal")
        messagebox.showerror("Error", f"Gagal convert:\n{err}")


# ============================================================
#  ENTRY POINT
# ============================================================
def run_main_app():
    root = tk.Tk()
    MDtoPDFConverter(root)
    root.mainloop()


def bootstrap() -> bool:
    """Cek deps. Kalau sudah lengkap → skip window, langsung True."""
    missing = get_missing_packages()
    if not missing:
        return True

    root = tk.Tk()
    installer = DependencyInstaller(root)
    root.mainloop()
    return installer.ok


if __name__ == "__main__":
    if bootstrap():
        try:
            run_main_app()
        except Exception as e:
            import traceback
            traceback.print_exc()
            try:
                messagebox.showerror(
                    "Fatal Error",
                    f"Aplikasi gagal dijalankan:\n\n{e}"
                )
            except Exception:
                pass
            sys.exit(1)
    else:
        sys.exit(0)