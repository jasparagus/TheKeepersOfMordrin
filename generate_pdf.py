"""
PDF Generation Script for Chapter Books

Usage:
    python generate_pdf.py [folder_path] [--output OUTPUT_FILE] [--title "Book Title"]

Examples:
    # 1. Generate default book from the '2. Chapterbook' folder
    # This reads all numbered chapters and outputs '01_TKoM_00_The Keepers of Mordrin.pdf'
    # inside that folder.
    python generate_pdf.py

    # 2. Generate book from a different folder, specifying the title
    python generate_pdf.py "3. Novel" --title "The Keepers of Mordrin: The Novel"

Details:
    - Cover: If an image file (e.g., .png or .jpg) containing "_00" and "Cover" in its 
      filename (like '01_TKoM_00. Cover.png') is found in the target folder, it will 
      automatically be inserted as a full-width cover on the very first page.
    - TOC: A Table of Contents is automatically built from markdown headers starting with `#`.
    - Separators: Markdown lines containing exactly `---` or `***` will be drawn as graphical lines.
    - Images: Inline markdown images `![Alt](Path)` are rendered centered at 25% page height.
"""

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

# --- PDF CONFIGURATION ---
FONT_MAIN = "Times"
FONT_HEADER = "Helvetica"
FONT_TOC_BODY = "Times"

SIZE_TITLE = 36
SIZE_TOC_TITLE = 24
SIZE_TOC_BODY = 16
SIZE_H1 = 24
SIZE_H2 = 20
SIZE_MAIN = 18

# Intra-paragraph line height (should be around 1.15x to 1.5x the main size in points)
# 16pt font is roughly 5.6mm. 9mm line height provides a comfortable 1.5x spacing.
INTRA_PADDING = 9 
# -------------------------

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
    pdf.set_font(FONT_HEADER, "B", SIZE_TOC_TITLE)
    epw = getattr(pdf, 'epw', 170)
    try:
        pdf.cell(w=epw, h=15, txt="Table of Contents", align="C", new_x="LMARGIN", new_y="NEXT")
    except TypeError:
        pdf.cell(epw, 15, "Table of Contents", align="C", ln=1)
    
    pdf.ln(10)
    pdf.set_font(FONT_TOC_BODY, "", SIZE_TOC_BODY)
    
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
            self.set_font(FONT_HEADER, "I", 10)
            self.set_text_color(150, 150, 150)
            self.cell(0, 10, "The Keepers of Mordrin", align="C")
            self.set_text_color(0, 0, 0)
            self.ln(15)

    def footer(self):
        if self.page_no() > 1:
            self.set_y(-15)
            self.set_font(FONT_HEADER, "I", 10)
            self.set_text_color(150, 150, 150)
            self.cell(0, 10, f"- {self.page_no()} -", align="C")
            self.set_text_color(0, 0, 0)

def generate_book(folder_path, output_pdf="01_TKoM_00_The Keepers of Mordrin.pdf", book_title="The Keepers of Mordrin"):
    folder = Path(folder_path)
    output_path = folder / output_pdf
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
    
    # 0. Optional Cover Page
    cover_files = [f for f in folder.glob("*") if "_00" in f.name and "Cover" in f.name and f.suffix.lower() in [".png", ".jpg", ".jpeg"]]
    if cover_files:
        cover_path = cover_files[0]
        print(f"Found cover image: {cover_path.name}")
        pdf.add_page()
        try:
            # Full page cover
            pdf.image(str(cover_path), x=0, y=0, w=pdf.w, h=pdf.h)
        except Exception as e:
            print(f"Warning: Could not add cover image: {e}")
            
    # 1. Title Page
    pdf.add_page()
    pdf.set_font(FONT_HEADER, "B", SIZE_TITLE)
    pdf.ln(80)
    
    safe_title = sanitize_text(book_title)
    epw = getattr(pdf, 'epw', 170)
    try:
        pdf.cell(w=epw, h=20, txt=safe_title, align="C", new_x="LMARGIN", new_y="NEXT")
    except TypeError:
        pdf.cell(0, 20, safe_title, align="C", ln=1)
        
    # 2. Table of Contents Placeholder
    if hasattr(pdf, 'insert_toc_placeholder'):
        pdf.add_page() # Force TOC to be on its own dedicated separate page
        pdf.insert_toc_placeholder(render_toc, pages=1)
    else:
        print("Note: installed fpdf2 version does not support automatic TOC generation. Skipping TOC.")
        
    for i, file_path in enumerate(md_files):
        print(f"Processing: {file_path.name}")
        pdf.add_page()
        
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
            
        for line in lines:
            line = line.strip()
            
            # Markdown Separator
            if line in ["---", "***", "- - -", "* * *"]:
                pdf.ln(8)
                y = pdf.get_y()
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
                pdf.set_font(FONT_HEADER, "B", SIZE_H1)
                
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
                pdf.set_font(FONT_HEADER, "B", SIZE_H2)
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
                    target_h = getattr(pdf, 'eph', 257) * 0.3
                    try:
                        pdf.image(str(img_path), h=target_h, x="C")
                    except Exception as e:
                        print(f"Warning: Could not add image {img_path}: {e}")
                    pdf.ln(5)
                else:
                    print(f"Warning: Image not found at {img_path}")
                continue

            # Standard Text Paragraph
            line = sanitize_text(line)
            pdf.set_font(FONT_MAIN, "", SIZE_MAIN)
            
            parts = re.split(r'(\*\*.*?\*\*|\*.*?\*|_.*?_)', line)
            
            for part in parts:
                if not part:
                    continue
                
                if part.startswith('**') and part.endswith('**'):
                    pdf.set_font(FONT_MAIN, "B", SIZE_MAIN)
                    pdf.write(INTRA_PADDING, part[2:-2])
                elif (part.startswith('*') and part.endswith('*')) or (part.startswith('_') and part.endswith('_')):
                    pdf.set_font(FONT_MAIN, "I", SIZE_MAIN)
                    pdf.write(INTRA_PADDING, part[1:-1])
                else:
                    pdf.set_font(FONT_MAIN, "", SIZE_MAIN)
                    pdf.write(INTRA_PADDING, part)
                    
            # Move down properly at the end of the written paragraph text
            pdf.ln(INTRA_PADDING)

    print(f"Saving PDF to {output_path}...")
    pdf.output(str(output_path))
    print("Done!")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate PDF Book from Markdown Chapters")
    parser.add_argument("folder", nargs="?", default="2. Chapterbook", help="Path to the folder containing chapter markdown files")
    parser.add_argument("--output", default="01_TKoM_00_The Keepers of Mordrin.pdf", help="Output PDF file name")
    parser.add_argument("--title", default="The Keepers of Mordrin", help="Book title")
    
    args = parser.parse_args()
    generate_book(args.folder, args.output, args.title)
