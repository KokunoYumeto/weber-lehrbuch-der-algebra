"""Build the complete German and English readers of Weber, Lehrbuch der Algebra I-III: a title page and a short
edition page, the transcribed front matter (title pages, preface, printed table of contents with linked page
numbers), and the body in printed-page order (same ordering rules as work/build.py), with PDF bookmarks for every
Book, Section and paragraph taken from the printed contents.
usage: python -X utf8 -B build_readers.py [b1|b2|b3 ...] [--lang de|en] [--nocompile]"""
import argparse
import collections
import pathlib
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parent
W = ROOT / "sources"
C = ROOT
FM = ROOT / "sources" / "front_matter"
OUT = ROOT / "build"
OUT.mkdir(exist_ok=True)
DUPLICATE_RESCANS = {"b2": {711, 712}, "b3": set(range(415, 425))}
FM_PAGES = {"b1": [10, 12, 13, 14, 15, 16, 18, 19, 20, 21, 22, 23, 24],
            "b2": [6, 8, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19],
            "b3": [7, 8, 9, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]}
SCAN = {"b1": "lehrbuchderalgeb01weberich", "b2": "lehrbuchderalgeb02weberich", "b3": "lehrbuchderalgeb03webe_0"}
REPO = "https://github.com/KokunoYumeto/weber-lehrbuch-der-algebra"
CC0 = "https://creativecommons.org/publicdomain/zero/1.0/"
VOL = {
    "de": {"b1": ("Erster Band", "Braunschweig: Friedrich Vieweg und Sohn, 1895"),
           "b2": ("Zweiter Band", "Braunschweig: Friedrich Vieweg und Sohn, 1896"),
           "b3": ("Dritter Band: Elliptische Funktionen und algebraische Zahlen. Zweite Auflage",
                  "Braunschweig: Friedrich Vieweg und Sohn, 1908")},
    "en": {"b1": ("Volume I", "Braunschweig: Friedrich Vieweg und Sohn, 1895"),
           "b2": ("Volume II", "Braunschweig: Friedrich Vieweg und Sohn, 1896"),
           "b3": ("Volume III: Elliptic Functions and Algebraic Numbers. Second edition",
                  "Braunschweig: Friedrich Vieweg und Sohn, 1908")},
}
EDITION = {
    "de": r"""\begin{center}
{\Large Heinrich Weber}\\[6pt]
{\LARGE\textbf{Lehrbuch der Algebra}}\\[8pt]
{\large %(vol)s}\\[4pt]
%(imprint)s\\[24pt]
{\large Deutscher Text}\\[4pt]
mit den Seitenzahlen des Originals
\end{center}
\clearpage
\noindent Transkribiert vom Scan \url{https://archive.org/details/%(scan)s} (Internet Archive).
Der deutsche Text wurde von KI-Modellen (Anthropic Claude und OpenAI Codex) vom Scan transkribiert und am Scan
geprüft.%(extra_de)s Webers Text ist gemeinfrei; Transkription und Satz sind nach CC0~1.0 gemeinfrei gestellt
(\url{%(cc0)s}). Quelldateien: \url{%(repo)s}.
\clearpage
""",
    "en": r"""\begin{center}
{\Large Heinrich Weber}\\[6pt]
{\LARGE\textbf{Lehrbuch der Algebra}}\\[4pt]
{\large (Textbook of Algebra)}\\[8pt]
{\large %(vol)s}\\[4pt]
%(imprint)s\\[24pt]
{\large English translation}\\[4pt]
with the page numbers of the original
\end{center}
\clearpage
\noindent Translated from the scan \url{https://archive.org/details/%(scan)s} (Internet Archive).
The German text was transcribed from the scan and translated into English by AI models (Anthropic Claude and
OpenAI Codex), and both were checked against the scan by AI.%(extra_en)s Weber's text is in the public domain; the
transcription, translation and typesetting are dedicated to the public domain under CC0~1.0 (\url{%(cc0)s}).
Source files: \url{%(repo)s}.
\clearpage
""",
}
EXTRA = {"b3": {"de": " Das transkribierte Inhaltsverzeichnis wurde mit dem von Maxim Leyenson beigesteuerten verglichen.",
                "en": " The transcribed table of contents was checked against the one contributed by Maxim Leyenson."}}
TOC_MACROS = r"""
% --- reader additions ---------------------------------------------------------
\usepackage{url}
\usepackage[unicode,bookmarksnumbered=false,bookmarksopen=true,bookmarksopenlevel=1,colorlinks=true,
  linkcolor=black,urlcolor=blue]{hyperref}
\usepackage{bookmark}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\weberpage}[1]{\phantomsection\label{wp:#1}}
\newcommand{\inhaltkopf}[1]{\begin{center}\large\textbf{#1}\end{center}\medskip}
\newcommand{\inhaltbuch}[2]{\par\medskip\begin{center}\if\relax\detokenize{#1}\relax\else#1\\[2pt]\fi{\large\textbf{#2}}\end{center}}
\newcommand{\inhaltabschnitt}[2]{\par\smallskip\begin{center}\small\if\relax\detokenize{#1}\relax\else#1\\\fi\textbf{#2}\end{center}}
\newcommand{\inhaltpar}[3]{\par\noindent\hangindent=3.4em\hbox to 3.4em{\S~#1.\hfil}#2\dotfill\,\hyperref[wp:#3]{#3}\par}
\newcommand{\inhaltzeile}[2]{\par\noindent #1\dotfill\,\hyperref[wp:#2]{#2}\par}
"""
GREEK = {"vartheta": "ϑ", "theta": "θ", "Theta": "Θ", "eta": "η", "sigma": "σ", "gamma": "γ", "wp": "℘", "varphi": "φ",
         "omega": "ω", "kappa": "κ", "lambda": "λ", "pi": "π", "Omega": "Ω", "tau": "τ", "mu": "μ", "nu": "ν",
         "alpha": "α", "beta": "β", "delta": "δ", "Delta": "Δ", "Gamma": "Γ", "chi": "χ", "psi": "ψ", "xi": "ξ",
         "zeta": "ζ", "rho": "ρ", "varrho": "ρ", "epsilon": "ε", "varepsilon": "ε", "phi": "φ", "Phi": "Φ",
         "Psi": "Ψ", "Pi": "Π", "Sigma": "Σ", "Lambda": "Λ", "Xi": "Ξ", "iota": "ι", "upsilon": "υ"}


def plain(s):
    s = re.sub(r"\\(?:gesperrt|textit|textbf|emph|mathrm|mathbf|mathit)\{((?:[^{}]|\{[^{}]*\})*)\}", r"\1", s)
    s = re.sub(r"\\mathfrak\{(\w)\}", r"\1", s)
    s = re.sub(r"\\([A-Za-z]+)", lambda m: GREEK.get(m.group(1), ""), s)
    s = s.replace("$", "").replace("{", "").replace("}", "").replace("^", "").replace("_", "").replace("~", " ")
    return re.sub(r"\s+", " ", s).strip()


ENTRY = re.compile(r"\\inhalt(buch|abschnitt|par|zeile)\{((?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*)\}"
                   r"(?:\{((?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*)\})?(?:\{([^}]*)\})?")


def bookmarks(band, lang):
    """printed page -> [(level, text)] from the transcribed table of contents."""
    pending, out = [], collections.defaultdict(list)
    for i in FM_PAGES[band]:
        t = (FM / lang / ("%s_i%04d.tex" % (band, i))).read_text(encoding="utf-8")
        for kind, a, b, c in ENTRY.findall(t):
            if kind == "buch":
                pending.append((0, plain(a) + " " + plain(b)))
            elif kind == "abschnitt":
                pending.append((1, plain(a) + " " + plain(b)))
            elif kind == "par":
                page = c.strip()
                for lv, txt in pending:
                    out[page].append((lv, txt))
                pending = []
                out[page].append((2, "§ %s. %s" % (a, plain(b))))
            elif kind == "zeile":
                page = b.strip()
                for lv, txt in pending:
                    out[page].append((lv, txt))
                pending = []
                out[page].append((1, plain(a)))
    return out


def ordered(band, lang):
    skip = DUPLICATE_RESCANS.get(band, set())
    root = W / lang / band
    raw = []
    for p in sorted(root.glob(band + "_i*.tex")):
        idx = int(re.search(r"_i(\d+)\.tex$", p.name).group(1))
        if idx in skip:
            continue
        text = p.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")
        m = re.search(r"^%\s*!PRINTED\s+(\d+)\s*$", text, re.M)
        raw.append((idx, int(m.group(1)) if m else None, text))
    raw.sort()
    frags, last_p, last_i = [], None, None
    for idx, printed, text in raw:
        if printed is not None:
            key, last_p, last_i = float(printed), printed, idx
        elif last_p is not None:
            key = last_p + 0.001 * (idx - last_i)
        else:
            key = -1000.0 + idx
        frags.append((key, idx, printed, text))
    frags.sort()
    return frags


def master(band, lang):
    pre = (W / "preamble.tex").read_text(encoding="utf-8")
    assets = "".join("{%s/}" % (ROOT / "figures" / b).as_posix() for b in ("b1", "b2", "b3"))
    pre = re.sub(r"\\graphicspath\{.*\}", lambda m: "\\graphicspath{%s}" % assets, pre)
    if lang == "en":
        pre = pre.replace(r"\usepackage[ngerman]{babel}", r"\usepackage[ngerman,english]{babel}", 1)
    pre += TOC_MACROS
    vol, imprint = VOL[lang][band]
    parts = [pre, r"\begin{document}", r"\selectlanguage{%s}" % ("english" if lang == "en" else "ngerman"),
             r"\pagenumbering{roman}",
             EDITION[lang] % {"vol": vol, "imprint": imprint, "scan": SCAN[band], "cc0": CC0, "repo": REPO,
                              "extra_de": EXTRA.get(band, {}).get("de", ""), "extra_en": EXTRA.get(band, {}).get("en", "")}]
    for i in FM_PAGES[band]:
        parts.append("%% ===== front matter, scan leaf %d =====" % i)
        parts.append((FM / lang / ("%s_i%04d.tex" % (band, i))).read_text(encoding="utf-8"))
        parts.append(r"\clearpage")
    parts.append(r"\pagenumbering{arabic}")
    bm = bookmarks(band, lang)
    used, n = set(), 0
    frags = ordered(band, lang)
    # Section-opening pages carry no printed number; when the unnumbered leaves between two numbered pages exactly
    # fill the gap, they are those page numbers, and get the link target the contents need.
    inferred = {}
    numbered = [(k, f[2]) for k, f in enumerate(frags) if f[2] is not None]
    for (ka, pa), (kb, pb) in zip(numbered, numbered[1:]):
        between = list(range(ka + 1, kb))
        if between and pb - pa - 1 == len(between):
            for off, k in enumerate(between, 1):
                inferred[k] = pa + off
    for k, (key, idx, printed, text) in enumerate(frags):
        if printed is None and k in inferred:
            printed = inferred[k]
            text = "\\weberpage{%d}%% page number not printed on this page\n" % printed + text
        p = str(printed) if printed is not None else None
        if p and p in bm and p not in used:
            used.add(p)
            lines = []
            for lv, txt in bm[p]:
                n += 1
                lines.append(r"\pdfbookmark[%d]{%s}{bm%d}" % (lv, txt.replace("\\", ""), n))
            text = re.sub(r"(\\weberpage\{%s\}[^\n]*\n)" % re.escape(p), lambda m: m.group(1) + "\n".join(lines) + "\n",
                          text, count=1) if re.search(r"\\weberpage\{%s\}" % re.escape(p), text) else "\n".join(lines) + "\n" + text
        parts.append("\n%% ===== scan leaf %d, printed %s =====" % (idx, printed))
        parts.append(text)
    parts.append(r"\end{document}" + "\n")
    missing = sorted(set(bm) - used, key=lambda s: (len(s), s))
    return "\n".join(parts), n, missing


def compile_tex(path):
    for run in (1, 2):
        r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", path.name], cwd=path.parent,
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode != 0:
            log = path.with_suffix(".log").read_text(encoding="utf-8", errors="replace")
            errs = [ln for ln in log.splitlines() if ln.startswith("!")][:6]
            ctx = log[log.find("!"):log.find("!") + 600] if "!" in log else ""
            return "FAIL run %d: %s\n%s" % (run, errs, ctx)
    log = path.with_suffix(".log").read_text(encoding="utf-8", errors="replace")
    pages = re.search(r"Output written .*?\((\d+) pages", log)
    undefined = len(re.findall(r"(?i)reference `[^']*' on page \S+ undefined", log))
    return "PASS %s pages, undefined references %d" % (pages.group(1) if pages else "?", undefined)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("bands", nargs="*", default=["b1", "b2", "b3"])
    ap.add_argument("--lang", choices=["de", "en"])
    ap.add_argument("--nocompile", action="store_true")
    a = ap.parse_args()
    for band in a.bands:
        for lang in ([a.lang] if a.lang else ["de", "en"]):
            text, nbm, missing = master(band, lang)
            dst = OUT / ("weber_%s_%s.tex" % (band, lang))
            dst.write_text(text, encoding="utf-8", newline="\n")
            msg = "" if a.nocompile else compile_tex(dst)
            print("%s %s: %d KB, %d bookmarks, contents pages without a body page: %s | %s" % (
                band, lang, len(text.encode("utf-8")) // 1024, nbm, missing[:8], msg), flush=True)
