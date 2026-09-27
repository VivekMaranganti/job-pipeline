#!/usr/bin/env python3
"""
Convert a resume .docx to PDF, render page 1, and measure how full it is.

Works on macOS, Linux, and Windows. Finds LibreOffice on its own, gives each
run its own LibreOffice profile (next to the .docx, so concurrent runs in
separate working directories never collide), and uses PyMuPDF for the page
count and preview, so Poppler and Pillow aren't needed.

Usage:
    python3 render_resume.py <resume.docx>

Output (one per line):
    pdf: <absolute path to the PDF>
    pages: <page count>
    fill: <percent of page 1 height used>%
    preview: <absolute path to page-1.png>

Exit status is non-zero if LibreOffice or PyMuPDF is missing or the
conversion fails. Set SOFFICE to override the LibreOffice path.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

# Windows pipes default to a legacy code page; company names can contain any
# Unicode character.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SOFFICE_CANDIDATES = [
    "/Applications/LibreOffice.app/Contents/MacOS/soffice",
    r"C:\Program Files\LibreOffice\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
]


def fail(msg):
    sys.stderr.write(f"render_resume: {msg}\n")
    sys.exit(1)


def find_soffice():
    if os.environ.get("SOFFICE"):
        return os.environ["SOFFICE"]
    for name in ("soffice", "libreoffice"):
        found = shutil.which(name)
        if found:
            return found
    for path in SOFFICE_CANDIDATES:
        if os.path.exists(path):
            return path
    fail("LibreOffice not found. Install it (see README step 1) or set SOFFICE "
         "to the full path of soffice.")


def convert(docx):
    outdir = docx.parent
    profile = outdir / ".lo_profile"
    cmd = [
        find_soffice(),
        "--headless",
        f"-env:UserInstallation={profile.as_uri()}",
        "--convert-to", "pdf",
        "--outdir", str(outdir),
        str(docx),
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=180)
    except subprocess.CalledProcessError as e:
        fail(f"LibreOffice failed: {e.stderr.decode(errors='replace').strip()}")
    except subprocess.TimeoutExpired:
        fail("LibreOffice timed out after 180 seconds")
    pdf = docx.with_suffix(".pdf")
    if not pdf.exists():
        fail(f"LibreOffice exited cleanly but {pdf.name} wasn't created")
    return pdf


def inspect(pdf):
    try:
        import pymupdf as fitz
    except ImportError:
        try:
            import fitz  # PyMuPDF older than 1.24.3
        except ImportError:
            fail("PyMuPDF not installed. Run: python3 -m pip install pymupdf")

    doc = fitz.open(pdf)
    pages = doc.page_count
    pix = doc[0].get_pixmap(dpi=120, colorspace=fitz.csGRAY)
    preview = pdf.parent / "page-1.png"
    pix.save(preview)

    # Lowest row on page 1 with any dark pixel, sampling every 4th column.
    samples, width, height, stride = pix.samples, pix.width, pix.height, pix.stride
    last = 0
    for y in range(height - 1, -1, -1):
        row = samples[y * stride: y * stride + width]
        if any(row[x] < 200 for x in range(0, width, 4)):
            last = y
            break
    return pages, 100 * last // height, preview


def main():
    if len(sys.argv) != 2:
        fail("usage: python3 render_resume.py <resume.docx>")
    docx = Path(sys.argv[1]).resolve()
    if not docx.exists():
        fail(f"{docx} not found")

    pdf = convert(docx)
    pages, fill, preview = inspect(pdf)
    print(f"pdf: {pdf}")
    print(f"pages: {pages}")
    print(f"fill: {fill}%")
    print(f"preview: {preview}")


if __name__ == "__main__":
    main()
