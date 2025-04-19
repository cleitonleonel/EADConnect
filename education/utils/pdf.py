from fpdf import FPDF
from bs4 import BeautifulSoup
import re
import textwrap


def html_to_text(html):
    text = BeautifulSoup(html, "html.parser").get_text()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[\u200b\u200e\u200f\u202f\u2060\u00a0]', ' ', text)
    return text.strip()


def safe_wrap(text, width=100):
    return '\n'.join(textwrap.wrap(text, width))


class PDF(FPDF):
    def __init__(self, data, output, logo_path=None):
        super().__init__()
        self.data = data
        self.output_dir = output
        self.title = data['title']
        self.logo_path = logo_path

        # Fontes precisam ser registradas ANTES de chamar add_page()
        self.add_font(
            "DejaVu",
            "",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            uni=True
        )
        self.add_font(
            "DejaVu",
            "B",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            uni=True
        )
        self.add_font(
            "DejaVu",
            "I",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
            uni=True
        )
        self.set_font("DejaVu", size=12)

        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()

    def header(self):
        if self.logo_path:
            self.image(self.logo_path, x=10, y=8, w=30)
            self.set_y(12)
        self.set_font("DejaVu", "B", 11)
        self.set_text_color(50, 60, 100)
        self.ln(2)
        self.cell(
            0,
            10,
            safe_wrap(self.title, 70),
            border=False,
            ln=True,
            align="C"
        )
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", "", 10)
        self.set_text_color(128)
        page = f"Página {self.page_no()}"
        self.cell(0, 10, page, 0, 0, "C")

    def create_document(self):
        self.set_font("DejaVu", "B", 14)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 10, safe_wrap("Exercícios"), align='C')
        self.ln(10)

        for idx, q in enumerate(self.data["content"]["questions"], start=1):
            enunciado = html_to_text(q["enunciated"])

            self.set_fill_color(240, 248, 255)
            self.set_text_color(0)

            self.set_font("DejaVu", "B", 12)
            self.multi_cell(
                0,
                10,
                f"Questão {idx}",
                new_x="LEFT",
                fill=True
            )

            self.set_font("DejaVu", "", 12)
            self.multi_cell(
                190,
                8,
                safe_wrap(enunciado, 90),
                new_x="LEFT",
                fill=True
            )
            self.ln(2)

            for i, opt in enumerate(q["options"]):
                if opt["isCorrect"]:
                    letra = chr(65 + i)
                    texto = html_to_text(opt["text"])
                    justificativa = html_to_text(opt["feedback"])

                    self.set_text_color(0, 128, 0)
                    self.set_font("DejaVu", "B", 12)
                    self.multi_cell(
                        0,
                        8,
                        safe_wrap(f"✅ Alternativa correta ({letra}): {texto}", 90),
                        new_x="LEFT",
                        fill=True
                    )

                    if justificativa:
                        self.set_text_color(0, 100, 0)
                        self.set_font("DejaVu", "I", 11)
                        self.multi_cell(
                            190,
                            7,
                            safe_wrap(f"Justificativa: {justificativa}", 90),
                            new_x="LEFT",
                            fill=True
                        )
                    break

            self.set_text_color(0, 0, 0)
            self.ln(6)

            self.dashed_line(
                self.l_margin,
                self.get_y(),
                self.w - self.r_margin,
                self.get_y(),
                dash_length=1,
                space_length=1
            )

            self.ln(6)

        pdf_file = self.output_dir / f"{self.title}.pdf"
        self.output(pdf_file.as_posix())
        print(f"[INFO] PDF gerado como: {pdf_file.name}")
