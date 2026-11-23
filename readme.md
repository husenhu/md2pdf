# MD2PDF — Markdown to PDF Converter

A simple, cross-platform desktop application built with **Python + Tkinter** that converts Markdown (`.md`) files into well-styled PDF documents. It features an auto-dependency installer, live preview, and one-click conversion — no external tools like Pandoc or wkhtmltopdf required.

---

## ✨ Features

- 📂 **File picker** — Select any `.md` or `.markdown` file with a native dialog.
- 👁️ **Live preview** — Inspect the raw Markdown content before converting.
- 💾 **Custom output** — Choose where to save the resulting PDF.
- ⚡ **Asynchronous conversion** — The UI stays responsive during conversion (runs in a background thread).
- 🎨 **Beautiful PDF styling** — A4 page, styled headings, code blocks, tables, blockquotes, links, and images.
- 🔧 **Auto dependency installer** — Detects and installs missing Python packages (`markdown`, `xhtml2pdf`) on first launch.
- 📖 **Auto-open** — Optionally open the generated PDF in your default viewer once finished.
- 🖥️ **Cross-platform** — Works on Windows, macOS, and Linux (including WSL with WSLg).

---

## 📋 Requirements

### System Requirements

| Requirement | Details |
|---|---|
| **Python** | 3.8 or newer (tested on 3.13) |
| **Tkinter** | Bundled with Python, but on Linux may need a separate system package |
| **OS** | Windows 10/11, macOS 10.14+, or a modern Linux distro (Ubuntu 20.04+, WSL2) |
| **Internet** | Required only for the first run (to auto-install Python dependencies) |

### Python Dependencies

These are installed automatically on first launch, or manually via `pip`:

- [`markdown`](https://pypi.org/project/Markdown/) — Markdown to HTML parser
- [`xhtml2pdf`](https://pypi.org/project/xhtml2pdf/) — HTML to PDF renderer (pure Python, no external binaries)

---

## 🚀 Installation

### 1. Clone or download the project

Download the `MD2PDF-v26.11.23-dev.py` file into an empty folder.

### 2. Set up a Python environment (recommended)

#### 🐧 Linux / 🪟 WSL

```bash
# Install system packages (needed for venv + Tkinter)
sudo apt update
sudo apt install -y python3 python3-venv python3-tk

# For Python 3.13 specifically, install the version-matched packages:
sudo apt install -y python3.13-venv python3.13-tk
```

> If `python3.13-venv` or `python3.13-tk` is not found, add the deadsnakes PPA:
> ```bash
> sudo add-apt-repository ppa:deadsnakes/ppa
> sudo apt update
> sudo apt install -y python3.13-venv python3.13-tk
> ```

Then create and activate the virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

#### 🍎 macOS

```bash
# Tkinter is included in the python.org installer.
# If using Homebrew Python:
brew install python-tk

python3 -m venv venv
source venv/bin/activate
```

#### 🪟 Windows

```powershell
# Tkinter is bundled with the standard Python installer for Windows.
py -m venv venv
venv\Scripts\activate
```

> ⚠️ If `activate` is missing from `venv/bin/` (or `venv\Scripts\`), your Python installation is missing the `ensurepip` module. Install the system package `python3-venv` (Linux) and recreate the venv. See [Troubleshooting](#-troubleshooting).

### 3. Install Python dependencies (optional — auto-installed on first run)

```bash
pip install markdown xhtml2pdf
```

Or simply skip this step — the app will detect missing packages and offer to install them for you when you first launch it.

---

## 🎮 Usage

### Running the application

```bash
python MD2PDF-v26.11.23-dev.py
```

### First launch (auto-install flow)

1. On the very first launch, a **Setup Dependencies** window appears if `markdown` or `xhtml2pdf` is missing.
2. The window lists which packages are missing and asks for your permission to install them.
3. Click **Yes** to allow automatic installation. A live log shows the `pip install` output.
4. Once complete, click **▶ Lanjutkan ke Aplikasi** (Continue to App) to open the main window.
5. On subsequent launches, this window is skipped entirely — the app opens instantly.

### Converting a Markdown file

1. Click **📂 Pilih MD File** and select your `.md` file.
   - The Markdown content appears in the **Preview** panel.
   - The output PDF path is auto-filled as `<same-name>.pdf` next to the input file.
2. (Optional) Click **💾 Pilih Lokasi Simpan** to change the output location.
3. Click **🔄 Convert to PDF**.
4. Wait for the success dialog, then choose whether to open the PDF immediately.

### Supported Markdown syntax

The converter supports the standard Markdown extensions via `markdown`:

- Headings (`#`, `##`, `###`, …)
- Bold, italic, strikethrough
- Lists (ordered and unordered, nested)
- Links and images (relative paths and URLs)
- Code blocks (fenced with ` ``` `)
- Inline code (`` `code` ``)
- Tables (GFM-style)
- Blockquotes
- Horizontal rules

### PDF Styling

The generated PDF uses:

- **Page size:** A4
- **Margins:** 2 cm on all sides
- **Font:** Helvetica / Arial, 11pt body
- **Heading accents:** Green `#4CAF50` underline on `h1`, subtle borders on `h2`
- **Code blocks:** Light grey background with a green left border
- **Tables:** Green header row with zebra-striped body rows

> 💡 To customize styling, edit the CSS block inside the `_do_convert` method in `MD2PDF-v26.11.23-dev.py`.

---

## 🗂️ Project Structure

```
md2pdf/
├── MD2PDF-v26.11.23-dev.py   # Main application
├── README.md                 # This file
└── venv/                     # Virtual environment (created by you)
```

The entire application is a **single Python file** — easy to distribute, modify, and embed.

---

## 🛠️ Troubleshooting

### ❌ `ModuleNotFoundError: No module named 'tkinter'`

Tkinter is not a pip package — it must be installed via your system's package manager.

| OS | Command |
|---|---|
| Ubuntu / Debian / WSL | `sudo apt install -y python3-tk` |
| Matching Python 3.13 | `sudo apt install -y python3.13-tk` |
| Fedora | `sudo dnf install python3-tkinter` |
| Arch | `sudo pacman -S tk` |
| macOS (Homebrew) | `brew install python-tk` |
| Windows | Reinstall Python and check "tcl/tk and IDLE" during setup |

### ❌ `venv/bin/activate: No such file or directory`

Your venv is broken because `ensurepip` is missing from the base Python installation.

```bash
# Fix on Ubuntu / Debian / WSL
sudo apt install -y python3-venv python3-full
rm -rf venv
python3 -m venv venv
source venv/bin/activate
ls venv/bin/   # should now contain 'activate', 'pip', 'python'
```

### ❌ `ModuleNotFoundError: No module named 'ensurepip'`

Same root cause as above — install `python3-venv` (Linux) or reinstall Python from python.org (Windows/macOS).

### ❌ `xhtml2pdf` fails to install

- Ensure you're using Python 3.8+.
- On Linux, some environments need: `sudo apt install -y python3-dev libxml2-dev libxslt1-dev`.
- Try upgrading pip first: `pip install --upgrade pip setuptools wheel`.

### ❌ PDF is blank / images missing

- Relative image paths in your `.md` file are resolved relative to **the current working directory**, not the Markdown file. Use absolute paths or run the app from the Markdown file's folder.
- Remote images require an internet connection.

### ❌ GUI does not appear (WSL)

- On **Windows 11** with **WSLg**, GUI should work out of the box.
- On **Windows 10**, install an X server (VcXsrv or Xming), set `export DISPLAY=:0`, and start the server before launching the app.

### ❌ "Unable to locate package python3.13-tk"

You're using a Python version not available in your distro's default repos. Add the deadsnakes PPA:

```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.13-venv python3.13-tk
```

---

## ⚡ Alternative: Use `uv` (fastest setup, no `pip`/`ensurepip` needed)

If you don't want to deal with `pip` or system packages, [`uv`](https://github.com/astral-sh/uv) can create a venv and run the app in one step — no `ensurepip` required.

```bash
# Install uv (one line, no sudo)
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc   # or: source ~/.local/bin/env

# Create a venv (uses whatever Python you have)
cd md2pdf
uv venv
source .venv/bin/activate
uv pip install markdown xhtml2pdf
python MD2PDF-v26.11.23-dev.py
```

Or run without activating a venv at all:

```bash
uv run --with markdown --with xhtml2pdf python MD2PDF-v26.11.23-dev.py
```

---

## 🗺️ Roadmap / Ideas

- [ ] Batch conversion (select multiple `.md` files at once)
- [ ] Custom page size selector (A4 / Letter / A5)
- [ ] Dark mode UI
- [ ] Drag-and-drop support
- [ ] PDF metadata (author, title, subject)
- [ ] Alternative engine (`weasyprint`) for better CSS support

---

## 📜 License

This project is released under the **MIT License**. See [`LICENSE`](LICENSE) for details.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you'd like to change.

---

## 📬 Contact

Maintained by **@husen** — feel free to open an issue for bugs or feature requests.