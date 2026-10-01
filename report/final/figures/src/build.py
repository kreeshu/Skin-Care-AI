"""Build report figures: inline CSS/JS/brand icons, then render vector PDF + PNG with headless Chromium.

Usage: python3 report/final/figures/src/build.py
Icons are Simple Icons (CC0) SVGs in ./icons, coloured with their official brand hex.
"""
import re
import subprocess
from pathlib import Path

SRC = Path(__file__).resolve().parent
OUT = SRC.parent
BUILD = SRC / "build"
BROWSER = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
FIGURES = ["pipeline", "architecture"]
BRAND = {
    "expo": "000020", "react": "61DAFB", "typescript": "3178C6", "fastapi": "009688",
    "python": "3776AB", "tensorflow": "FF6F00", "keras": "D00000", "opencv": "5C3EE8",
    "huggingface": "FFD21E", "pandas": "150458", "streamlit": "FF4B4B", "onnx": "005CED",
    "google": "4285F4", "kaggle": "20BEFF", "numpy": "013243", "scikitlearn": "F7931E",
    "pydantic": "E92063", "pytorch": "EE4C2C",
}


def icon(name):
    svg = (SRC / "icons" / f"{name}.svg").read_text()
    svg = re.sub(r"<title>.*?</title>", "", svg)
    cls = ' class="wide"' if name == "kaggle" else ""  # wordmark logo needs extra width
    return svg.replace("<svg ", f'<svg{cls} fill="#{BRAND[name]}" ', 1)


def build(name):
    html = (SRC / f"{name}.html").read_text()
    html = html.replace("{{css}}", (SRC / "common.css").read_text())
    html = html.replace("{{js}}", (SRC / "wires.js").read_text())
    html = re.sub(r"\{\{(\w+)\}\}", lambda m: icon(m.group(1)), html)
    BUILD.mkdir(exist_ok=True)
    page = BUILD / f"{name}.html"
    page.write_text(html)
    common = [BROWSER, "--headless=new", "--disable-gpu", "--hide-scrollbars",
              "--virtual-time-budget=8000", "--run-all-compositor-stages-before-draw"]
    subprocess.run(common + ["--no-pdf-header-footer", f"--print-to-pdf={OUT / f'{name}.pdf'}",
                             page.as_uri()], check=True, capture_output=True)
    # 300 dpi PNG straight from the vector PDF (16 cm wide = 1890 px).
    subprocess.run(["pdftoppm", "-png", "-singlefile", "-scale-to-x", "1890", "-scale-to-y", "-1",
                    OUT / f"{name}.pdf", OUT / name], check=True)
    print("built", name)


if __name__ == "__main__":
    for f in FIGURES:
        if (SRC / f"{f}.html").exists():
            build(f)
