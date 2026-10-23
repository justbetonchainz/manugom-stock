"""Diagramme UML vectoriel avec généralisation des acteurs, style StarUML."""
from pathlib import Path

from reportlab.graphics import renderPDF, renderSVG
from reportlab.graphics.shapes import Rect
import pypdfium2 as pdfium

from staruml_style import (
    PAPER, LINE, actor, base, connector, multiline, text, triangle_head, use_case,
)


def diagram():
    from staruml_style import use_case_diagram
    return use_case_diagram()


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    output = root / "output" / "diagrams"
    scratch = root / "tmp" / "uml"
    output.mkdir(parents=True, exist_ok=True)
    scratch.mkdir(parents=True, exist_ok=True)
    figure = diagram()
    svg = output / "MANUGOM_Cas_utilisation_corrige.svg"
    png = output / "MANUGOM_Cas_utilisation_corrige.png"
    renderSVG.drawToFile(figure, str(svg))
    intermediate = scratch / "cas-utilisation-corrige.pdf"
    renderPDF.drawToFile(figure, str(intermediate))
    document = pdfium.PdfDocument(str(intermediate))
    document[0].render(scale=2).to_pil().save(png)
    print(svg)
    print(png)
