# Heinrich Weber, *Lehrbuch der Algebra* — German text and English translation

Heinrich Weber's *Lehrbuch der Algebra* in three volumes: the German text and an English translation. Every reader
keeps the page numbers of the original, reproduces the printed title pages, preface and table of contents with
linked page numbers, and has PDF bookmarks for every book, section and paragraph.

| Volume | German | English |
| --- | --- | --- |
| I (Braunschweig: Vieweg, 1895) | [PDF](pdf/Weber_Lehrbuch_der_Algebra_Band_I_German.pdf) · [LaTeX](tex/Weber_Lehrbuch_der_Algebra_Band_I_German.tex) | [PDF](pdf/Weber_Lehrbuch_der_Algebra_Band_I_English.pdf) · [LaTeX](tex/Weber_Lehrbuch_der_Algebra_Band_I_English.tex) |
| II (Braunschweig: Vieweg, 1896) | [PDF](pdf/Weber_Lehrbuch_der_Algebra_Band_II_German.pdf) · [LaTeX](tex/Weber_Lehrbuch_der_Algebra_Band_II_German.tex) | [PDF](pdf/Weber_Lehrbuch_der_Algebra_Band_II_English.pdf) · [LaTeX](tex/Weber_Lehrbuch_der_Algebra_Band_II_English.tex) |
| III: *Elliptische Funktionen und algebraische Zahlen*, 2nd edition (Braunschweig: Vieweg, 1908) | [PDF](pdf/Weber_Lehrbuch_der_Algebra_Band_III_German.pdf) · [LaTeX](tex/Weber_Lehrbuch_der_Algebra_Band_III_German.tex) | [PDF](pdf/Weber_Lehrbuch_der_Algebra_Band_III_English.pdf) · [LaTeX](tex/Weber_Lehrbuch_der_Algebra_Band_III_English.tex) |

## How it was made

The German text was transcribed from the Internet Archive scans
[lehrbuchderalgeb01weberich](https://archive.org/details/lehrbuchderalgeb01weberich),
[lehrbuchderalgeb02weberich](https://archive.org/details/lehrbuchderalgeb02weberich) and
[lehrbuchderalgeb03webe_0](https://archive.org/details/lehrbuchderalgeb03webe_0), and translated into English, by
AI models (Anthropic Claude and OpenAI Codex). Both were checked against the scans by AI. Misprints in Weber's text
are kept as printed and marked in the sources with `% [sic]` comments.

Maxim Leyenson contributed tables of contents of Volume III; they were used to check the transcribed contents.

## Sources

- `sources/de/` and `sources/en/`: one LaTeX file per printed page; `% !PRINTED n` gives the page of the original.
- `sources/front_matter/`: title pages, prefaces and tables of contents, in German and English.
- `figures/`: the figures; `sources/preamble.tex`: the shared preamble.
- `python build_readers.py` rebuilds the six readers with pdfLaTeX.

## Rights

Weber's text is in the public domain. The transcription, translation and typesetting are dedicated to the public
domain under [CC0 1.0](LICENSE).

---

[Sponsor this work](https://github.com/sponsors/KokunoYumeto)
