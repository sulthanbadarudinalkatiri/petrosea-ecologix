from fpdf import FPDF
import pandas as pd

def generate_pdf_from_dataframe(df: pd.DataFrame, title: str) -> bytes:
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Title
    pdf.set_font("helvetica", style="B", size=14)
    pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)
    
    if df.empty:
        pdf.set_font("helvetica", size=10)
        pdf.cell(0, 10, "No data available.", new_x="LMARGIN", new_y="NEXT")
        return bytes(pdf.output())
    
    # Table Header
    pdf.set_font("helvetica", style="B", size=8)
    col_width = pdf.epw / len(df.columns)
    th = pdf.font_size * 2
    
    for col in df.columns:
        # truncate column name to fit
        pdf.cell(col_width, th, str(col)[:20], border=1, align="C")
    pdf.ln(th)
    
    # Table Data
    pdf.set_font("helvetica", size=7)
    for row in df.itertuples(index=False):
        for datum in row:
            pdf.cell(col_width, th, str(datum)[:30].replace('\n', ' '), border=1)
        pdf.ln(th)
        
    return bytes(pdf.output())
