import os
import re
import sys
import urllib.parse
from pathlib import Path

try:
    from fpdf import FPDF
except ImportError:
    print("Error: The 'fpdf2' library is not installed.")
    print("Please install it by running: python -m pip install fpdf2")
    sys.exit(1)

def sanitize_text(text):
    """Replace common unicode characters not supported by standard FPDF core fonts."""
    if not isinstance(text, str):
        return text
    text = text.replace("’", "'").replace("‘", "'")
    text = text.replace("“", '"').replace("”", '"')
    text = text.replace("—", "-").replace("–", "-")
    text = text.replace("…", "...")
    return text.encode('latin-1', 'replace').decode('latin-1')

def render_toc(pdf, outline):
    # This function is called by fpdf2 to render the TOC page(s)
    pdf.set_y(30)
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", "B", 24)
    epw = getattr(pdf, 'epw', 170)
    try:
        pdf.cell(w=epw, h=15, txt="Table of Contents", align="C", new_x="LMARGIN", new_y="NEXT")
    except TypeError:
        pdf.cell(epw, 15, "Table of Contents", align="C", ln=1)
    
    pdf.ln(10)
    pdf.set_font("Courier", "", 14)
    
    for section in outline:
        title = sanitize_text(section.name)
        page = str(section.page_number)
        
        # Calculate exactly how many dots fit in the remaining space
        title_w = pdf.get_string_width(title)
        page_w = pdf.get_string_width(page)
        dot_w = pdf.get_string_width(".")
        
        # 10mm buffer just to be safe so it doesn't clip
        avail_w = epw - title_w - page_w - 10
        
        num_dots = int(avail_w / dot_w) if dot_w > 0 else 1
        if num_dots < 1:
            num_dots = 1
            
        line_text = f"{title} {'.' * num_dots} {page}"
        
        try:
            pdf.cell(0, 10, txt=line_text, align="L", new_x="LMARGIN", new_y="NEXT")
        except TypeError:
            pdf.cell(0, 10, line_text, align="L", ln=1)

class BookPDF(FPDF):
    def header(self):
        if self.page_no() > 2:
            self.set_font("Helvetica", "I", 10)
            self.set_text_color(150, 150, 150)
            self.cell(0, 10, "The Keepers of Mordrin", align="C")
            self.set_text_color(0, 0, 0)
            self.ln(15)

    def footer(self):
        if self.page_no() > 1:
            self.set_y(-15)
            self.set_font("Helvetica", "I", 10)
            self.set_text_color(150, 150, 150)
            # Use format "- 1 -" for page numbers
            self.cell(0, 10, f"- {self.page_no()} -", align="C")
            self.set_text_color(0, 0, 0)

def generate_book(folder_path, output_pdf="Book_Output.pdf", book_title="The Keepers of Mordrin"):
    folder = Path(folder_path)
    if not folder.exists():
        print(f"Directory not found: {folder}")
        return

    md_files = []
    for f in folder.glob("*.md"):
        if "00" in f.name or "Outline" in f.name or "Table of Contents" in f.name:
            continue
        md_files.append(f)
        
    md_files.sort(key=lambda x: x.name)
    
    if not md_files:
        print("No valid chapter files found.")
        return

    print(f"Found {len(md_files)} chapters.")

    pdf = BookPDF(unit="mm", format="A4")
    pdf.set_margins(20, 20, 20)
    pdf.set_auto_page_break(auto=True, margin=20)
    
    # 1. Title Page
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 36)
    pdf.ln(80)
    # Title Case, instead of Upper Case
    safe_title = sanitize_text(book_title)
    epw = getattr(pdf, 'epw', 170)
    try:
        pdf.cell(w=epw, h=20, txt=safe_title, align="C", new_x="LMARGIN", new_y="NEXT")
    except TypeError:
        pdf.cell(0, 20, safe_title, align="C", ln=1)
        
    # We omit the subtitle to simplify
    
    if hasattr(pdf, 'insert_toc_placeholder'):
        pdf.insert_toc_placeholder(render_toc, pages=1)
    else:
        print("Note: installed fpdf2 version does not support automatic TOC generation. Skipping TOC.")
        
    for i, file_path in enumerate(md_files):
        print(f"Processing: {file_path.name}")
        pdf.add_page()
        
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
            
        INTRA_PADDING = 8 # Represents proper 1.5x spacing
            
        for line in lines:
            line = line.strip()
            
            # Markdown Separator
            if line == "---" or line == "***" or line == "- - -":
                pdf.ln(8)
                y = pdf.get_y()
                # Draw a sleek line in the center
                center = pdf.w / 2
                pdf.set_draw_color(150, 150, 150)
                pdf.set_line_width(0.5)
                pdf.line(center - 20, y, center + 20, y)
                pdf.set_draw_color(0, 0, 0) # reset
                pdf.set_line_width(0.2)
                pdf.ln(12)
                continue
            
            if not line:
                # Add normal extra gap on blank lines for double spacing between paragraphs
                pdf.ln(INTRA_PADDING) 
                continue
                
            # Headers
            if line.startswith("# "):
                header_text = sanitize_text(line.lstrip("#").strip())
                pdf.set_font("Helvetica", "B", 22) # Headers stay sans-serif
                
                if hasattr(pdf, 'start_section'):
                    pdf.start_section(header_text)
                    
                try:
                    pdf.cell(0, 15, txt=header_text, align="C", new_x="LMARGIN", new_y="NEXT")
                except TypeError:
                    pdf.cell(0, 15, header_text, align="C", ln=1)
                pdf.ln(8)
                continue
            elif line.startswith("##"):
                header_text = sanitize_text(line.lstrip("#").strip())
                pdf.set_font("Helvetica", "B", 18)
                try:
                    pdf.cell(0, 12, txt=header_text, new_x="LMARGIN", new_y="NEXT")
                except TypeError:
                    pdf.cell(0, 12, header_text, ln=1)
                pdf.ln(4)
                continue

            # Inline Images
            img_match = re.match(r'^!\[.*?\]\((.*?)\)$', line)
            if img_match:
                img_rel_path = urllib.parse.unquote(img_match.group(1).strip())
                img_path = file_path.parent / img_rel_path
                
                if img_path.exists():
                    pdf.ln(5)
                    # Changed width to 25% of page height
                    target_h = getattr(pdf, 'eph', 257) * 0.25
                    try:
                        pdf.image(str(img_path), h=target_h, x="C")
                    except Exception as e:
                        print(f"Warning: Could not add image {img_path}: {e}")
                    pdf.ln(5)
                else:
                    print(f"Warning: Image not found at {img_path}")
                continue

            # Standard Text Paragraph
            # Switching body text to serif font: "Times"
            line = sanitize_text(line)
            pdf.set_font("Times", "", 14)
            
            parts = re.split(r'(\*\*.*?\*\*|\*.*?\*|_.*?_)', line)
            
            for part in parts:
                if not part:
                    continue
                
                if part.startswith('**') and part.endswith('**'):
                    pdf.set_font("Times", "B", 14)
                    pdf.write(INTRA_PADDING, part[2:-2])
                elif (part.startswith('*') and part.endswith('*')) or (part.startswith('_') and part.endswith('_')):
                    pdf.set_font("Times", "I", 14)
                    pdf.write(INTRA_PADDING, part[1:-1])
                else:
                    pdf.set_font("Times", "", 14)
                    pdf.write(INTRA_PADDING, part)
                    
            # Move down properly at the end of the written paragraph text
            pdf.ln(INTRA_PADDING)

    print(f"Saving PDF to {output_pdf}...")
    pdf.output(output_pdf)
    print("Done!")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate PDF Book from Markdown Chapters")
    parser.add_argument("folder", nargs="?", default="2. Chapterbook", help="Path to the folder containing chapter markdown files")
    parser.add_argument("--output", default="The_Keepers_of_Mordrin.pdf", help="Output PDF file name")
    parser.add_argument("--title", default="The Keepers of Mordrin", help="Book title")
    
    args = parser.parse_args()
    generate_book(args.folder, args.output, args.title)
