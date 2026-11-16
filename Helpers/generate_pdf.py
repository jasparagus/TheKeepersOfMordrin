"""
PDF Generation Script for The Keepers of Mordrin Book Adaptations

Interactive Usage (Default — launched by _generate_pdf.sh or _generate_pdf.bat):
    python Helpers/generate_pdf.py

Direct CLI Usage (Optional):
    python Helpers/generate_pdf.py [prefix] [--folder FOLDER_PATH] [--output OUTPUT_FILE] [--title "Book Title"]
"""

import argparse
import os
import re
import sys
import urllib.parse
from pathlib import Path

try:
    from fpdf import FPDF
except ImportError:
    print("Error: The 'fpdf2' library is not installed.")
    print("Please install requirements by running: pip install -r Helpers/requirements.txt")
    sys.exit(1)

# --- PATH CONFIGURATION ---
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

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

# Intra-paragraph line height (16-18pt font is ~6mm; 9mm provides ~1.5x line spacing)
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
    return text.encode("latin-1", "replace").decode("latin-1")


def render_toc(pdf, outline):
    """Callback used by fpdf2 to render the Table of Contents page."""
    pdf.set_y(30)
    pdf.set_x(pdf.l_margin)
    pdf.set_font(FONT_HEADER, "B", SIZE_TOC_TITLE)
    epw = getattr(pdf, "epw", 170)
    try:
        pdf.cell(w=epw, h=15, txt="Table of Contents", align="C", new_x="LMARGIN", new_y="NEXT")
    except TypeError:
        pdf.cell(epw, 15, "Table of Contents", align="C", ln=1)

    pdf.ln(10)
    pdf.set_font(FONT_TOC_BODY, "", SIZE_TOC_BODY)

    for section in outline:
        title = sanitize_text(section.name)
        page = str(section.page_number)

        title_w = pdf.get_string_width(title)
        page_w = pdf.get_string_width(page)
        dot_w = pdf.get_string_width(".")

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
    def __init__(self, header_title="The Keepers of Mordrin", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.header_title = sanitize_text(header_title)

    def header(self):
        if self.page_no() > 2:
            self.set_font(FONT_HEADER, "I", 10)
            self.set_text_color(150, 150, 150)
            self.cell(0, 10, self.header_title, align="C")
            self.set_text_color(0, 0, 0)
            self.ln(15)

    def footer(self):
        if self.page_no() > 1:
            self.set_y(-15)
            self.set_font(FONT_HEADER, "I", 10)
            self.set_text_color(150, 150, 150)
            self.cell(0, 10, f"- {self.page_no()} -", align="C")
            self.set_text_color(0, 0, 0)


# --- DISCOVERY & PREVIEW HELPERS ---

def resolve_folder_path(folder_arg):
    """Resolve a folder path relative to either current working directory or PROJECT_ROOT."""
    candidate = Path(folder_arg)
    if candidate.exists():
        return candidate.resolve()
    root_candidate = PROJECT_ROOT / folder_arg
    if root_candidate.exists():
        return root_candidate.resolve()
    return candidate


def discover_book_folders(root_dir=PROJECT_ROOT):
    """Return sorted list of book directories in the project root."""
    excluded = {".git", ".venv", "venv", "__pycache__", "Helpers", "Images", "Reference Materials"}
    folders = []
    for entry in sorted(root_dir.iterdir(), key=lambda p: p.name):
        if not entry.is_dir() or entry.name.startswith(".") or entry.name in excluded:
            continue
        # Include numbered adaptation folders (e.g. '1. Picturebook', '2. Chapterbook') or any folder with .md files
        if re.match(r"^\d+\.", entry.name) or any(entry.glob("*.md")):
            folders.append(entry)
    return folders


def get_chapter_files(folder, prefix):
    """Return sorted list of chapter markdown files for a given book prefix (excluding outlines/00)."""
    md_files = []
    for f in folder.glob(f"{prefix}_*.md"):
        if "_00" in f.name or "Outline" in f.name or "Table of Contents" in f.name or "Review" in f.name:
            continue
        md_files.append(f)
    md_files.sort(key=lambda x: x.name)
    return md_files


def get_cover_files(folder, prefix):
    """Return sorted list of cover image files for a given book prefix."""
    return sorted(
        [
            f
            for f in folder.glob(f"{prefix}*")
            if "_00" in f.name and "Cover" in f.name and f.suffix.lower() in [".png", ".jpg", ".jpeg"]
        ],
        key=lambda x: x.name,
    )


def detect_book_title(folder, prefix):
    """Automatically infer the book's human-readable title from its Outline or chapter files."""
    outline_files = sorted(folder.glob(f"{prefix}_00*.md"), key=lambda x: x.name)
    for outline_path in outline_files:
        try:
            content = outline_path.read_text(encoding="utf-8")
            # Pattern 1: '# Book N: Title'
            m = re.search(r"^#\s*Book\s+\d+\s*:\s*(.+)$", content, flags=re.MULTILINE)
            if m:
                return m.group(1).strip()
            # Pattern 2: 'This document describes the book "Title"'
            m = re.search(r'describes the book\s+"([^"]+)"', content, flags=re.IGNORECASE)
            if m:
                return m.group(1).strip()
            # Pattern 3: First top-level '# Heading' if not generic '# Overview'
            m = re.search(r"^#\s+(.+)$", content, flags=re.MULTILINE)
            if m and m.group(1).strip().lower() not in {"overview", "outline"}:
                return m.group(1).strip()
        except Exception:
            pass

    # Pattern 4: Derive from first chapter filename if it's a single-file story (e.g. '01_KoboldCaper_01. The Clytin Claw Kobold Caper.md')
    chapters = get_chapter_files(folder, prefix)
    if len(chapters) == 1:
        m = re.match(rf"^{re.escape(prefix)}_\d+\.\s*(.+)\.md$", chapters[0].name)
        if m and not m.group(1).lower().startswith("chapter"):
            return m.group(1).strip()

    # Fallback: clean up prefix
    parts = prefix.split("_", 1)
    if len(parts) == 2:
        return re.sub(r"(?<!^)(?=[A-Z])", " ", parts[1]).strip()
    return prefix


def discover_books_in_folder(folder):
    """Discover all distinct book prefixes in a folder and summarize their contents."""
    prefixes = set()
    for f in folder.glob("*.md"):
        m = re.match(r"^(\d+_[A-Za-z0-9]+)_", f.name)
        if m:
            prefixes.add(m.group(1))

    books = []
    for prefix in sorted(prefixes):
        title = detect_book_title(folder, prefix)
        chapters = get_chapter_files(folder, prefix)
        covers = get_cover_files(folder, prefix)
        outlines = sorted(folder.glob(f"{prefix}_00*.md"), key=lambda x: x.name)
        books.append(
            {
                "prefix": prefix,
                "title": title,
                "chapters": chapters,
                "covers": covers,
                "outlines": outlines,
            }
        )
    return books


def inspect_chapter(md_path):
    """Extract chapter heading, word count, and referenced image status for preview."""
    heading = md_path.stem
    word_count = 0
    images = []
    try:
        lines = md_path.read_text(encoding="utf-8").splitlines()
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("# ") and heading == md_path.stem:
                heading = stripped.lstrip("#").strip()
            img_match = re.match(r"^!\[.*?\]\((.*?)\)$", stripped)
            if img_match:
                img_rel = urllib.parse.unquote(img_match.group(1).strip())
                img_path = md_path.parent / img_rel
                images.append((img_rel, img_path.exists()))
            else:
                word_count += len(stripped.split())
    except Exception:
        pass
    return {"heading": heading, "word_count": word_count, "images": images}


# --- CORE PDF GENERATOR ---

def get_default_output_filename(prefix, book_title):
    safe_out_title = book_title.replace(" ", "_").replace(":", "")
    return f"{prefix}_00_{safe_out_title}.pdf"


def generate_book(prefix, folder_path="2. Chapterbook", output_pdf=None, book_title=None):
    folder = resolve_folder_path(folder_path)
    if not folder.exists():
        print(f"Directory not found: {folder}")
        return False

    if not book_title:
        book_title = detect_book_title(folder, prefix)

    if not output_pdf:
        output_pdf = get_default_output_filename(prefix, book_title)

    output_path = Path(output_pdf) if Path(output_pdf).is_absolute() else (folder / output_pdf)

    md_files = get_chapter_files(folder, prefix)
    if not md_files:
        print(f"No valid chapter files found for prefix '{prefix}' in '{folder.name}'.")
        return False

    print(f"\nFound {len(md_files)} chapter(s) for '{prefix}' ({book_title}).")

    header_label = (
        "The Keepers of Mordrin"
        if book_title == "The Keepers of Mordrin"
        else f"The Keepers of Mordrin: {book_title}"
    )
    pdf = BookPDF(header_title=header_label, unit="mm", format="A4")
    pdf.set_margins(20, 20, 20)
    pdf.set_auto_page_break(auto=True, margin=20)

    # 0. Optional Cover Page
    cover_files = get_cover_files(folder, prefix)
    if cover_files:
        cover_path = cover_files[0]
        print(f"Found cover image: {cover_path.name}")
        pdf.add_page()
        try:
            pdf.image(str(cover_path), x=0, y=0, w=pdf.w, h=pdf.h)
        except Exception as e:
            print(f"Warning: Could not add cover image: {e}")

    # 1. Title Page
    pdf.add_page()
    pdf.set_font(FONT_HEADER, "B", SIZE_TITLE)
    pdf.ln(80)

    safe_title = sanitize_text(book_title)
    epw = getattr(pdf, "epw", 170)
    try:
        pdf.cell(w=epw, h=20, txt=safe_title, align="C", new_x="LMARGIN", new_y="NEXT")
    except TypeError:
        pdf.cell(0, 20, safe_title, align="C", ln=1)

    # 2. Table of Contents Placeholder
    if hasattr(pdf, "insert_toc_placeholder"):
        pdf.add_page()
        pdf.insert_toc_placeholder(render_toc, pages=1)
    else:
        print("Note: installed fpdf2 version does not support automatic TOC generation. Skipping TOC.")

    for file_path in md_files:
        print(f"  Processing: {file_path.name}")
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
                pdf.set_draw_color(0, 0, 0)
                pdf.set_line_width(0.2)
                pdf.ln(12)
                continue

            if not line:
                pdf.ln(INTRA_PADDING)
                continue

            # Headers
            if line.startswith("# "):
                header_text = sanitize_text(line.lstrip("#").strip())
                pdf.set_font(FONT_HEADER, "B", SIZE_H1)

                if hasattr(pdf, "start_section"):
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
            img_match = re.match(r"^!\[.*?\]\((.*?)\)$", line)
            if img_match:
                img_rel_path = urllib.parse.unquote(img_match.group(1).strip())
                img_path = file_path.parent / img_rel_path

                if img_path.exists():
                    pdf.ln(5)
                    target_h = getattr(pdf, "eph", 257) * 0.3
                    try:
                        pdf.image(str(img_path), h=target_h, x="C")
                    except Exception as e:
                        print(f"  Warning: Could not add image {img_path.name}: {e}")
                    pdf.ln(5)
                else:
                    print(f"  Warning: Image not found at {img_path.name}")
                continue

            # Standard Text Paragraph
            line = sanitize_text(line)
            pdf.set_font(FONT_MAIN, "", SIZE_MAIN)

            parts = re.split(r"(\*\*.*?\*\*|\*.*?\*|_.*?_)", line)

            for part in parts:
                if not part:
                    continue

                if part.startswith("**") and part.endswith("**"):
                    pdf.set_font(FONT_MAIN, "B", SIZE_MAIN)
                    pdf.write(INTRA_PADDING, part[2:-2])
                elif (part.startswith("*") and part.endswith("*")) or (
                    part.startswith("_") and part.endswith("_")
                ):
                    pdf.set_font(FONT_MAIN, "I", SIZE_MAIN)
                    pdf.write(INTRA_PADDING, part[1:-1])
                else:
                    pdf.set_font(FONT_MAIN, "", SIZE_MAIN)
                    pdf.write(INTRA_PADDING, part)

            pdf.ln(INTRA_PADDING)

    print(f"Saving PDF to: {output_path}")
    pdf.output(str(output_path))
    print("Done!")
    return True


# --- INTERACTIVE CLI WORKFLOW ---

def print_preview(folder, book_info):
    """Display a detailed preview of the selected book before generating."""
    prefix = book_info["prefix"]
    title = book_info["title"]
    chapters = book_info["chapters"]
    covers = book_info["covers"]
    out_name = get_default_output_filename(prefix, title)
    out_path = folder / out_name

    print("\n" + "=" * 64)
    print(f"  BOOK PREVIEW: {prefix} — \"{title}\"")
    print("=" * 64)
    print(f"  Folder      : {folder.name}")
    print(f"  Output File : {out_name}" + (" (will overwrite existing)" if out_path.exists() else " (new file)"))
    if covers:
        print(f"  Cover Image : {covers[0].name}")
    else:
        print("  Cover Image : None (will start with Title Page)")

    print(f"  Chapters    : {len(chapters)} file(s)")
    print("-" * 64)

    total_words = 0
    total_imgs_ok = 0
    total_imgs_missing = 0

    for idx, ch_path in enumerate(chapters, start=1):
        info = inspect_chapter(ch_path)
        total_words += info["word_count"]
        imgs = info["images"]
        ok_count = sum(1 for _, exists in imgs if exists)
        missing = [name for name, exists in imgs if not exists]
        total_imgs_ok += ok_count
        total_imgs_missing += len(missing)

        img_summary = f"{ok_count}/{len(imgs)} images" if imgs else "no images"
        if missing:
            img_summary += f" [MISSING: {', '.join(missing)}]"

        print(f"  {idx:2d}. {ch_path.name}")
        print(f"      Heading: {info['heading']} (~{info['word_count']} words, {img_summary})")

    print("-" * 64)
    print(
        f"  Total: ~{total_words:,} words | {total_imgs_ok} image(s) ready"
        + (f" | {total_imgs_missing} MISSING" if total_imgs_missing else "")
    )
    print("=" * 64)


def interactive_wizard():
    """Run the step-by-step interactive folder -> book -> preview -> generate workflow."""
    print("================================================================")
    print("        The Keepers of Mordrin — PDF Book Generator             ")
    print("================================================================")

    while True:
        # Step 2: Select a folder
        folders = discover_book_folders(PROJECT_ROOT)
        if not folders:
            print(f"No book folders found in {PROJECT_ROOT}")
            return

        print("\nStep 1: Select a Book Folder:")
        for idx, folder in enumerate(folders, start=1):
            books = discover_books_in_folder(folder)
            ReadyCount = sum(1 for b in books if b["chapters"])
            print(f"  [{idx}] {folder.name} ({ReadyCount} book(s) with chapters, {len(books)} total)")
        print("  [Q] Quit")

        choice = input("\nEnter folder number (or Q to quit): ").strip()
        if choice.lower() in {"q", "quit", "exit", "c", "cancel"}:
            print("Cancelled.")
            return

        if not choice.isdigit() or not (1 <= int(choice) <= len(folders)):
            print("Invalid selection. Please enter a number from the list.")
            continue

        selected_folder = folders[int(choice) - 1]

        # Step 3: Present list of matching books in the selected folder
        while True:
            books = discover_books_in_folder(selected_folder)
            if not books:
                print(f"\nNo books found in '{selected_folder.name}'.")
                break

            print(f"\nStep 2: Select a Book in '{selected_folder.name}':")
            for idx, b in enumerate(books, start=1):
                ch_count = len(b["chapters"])
                cov_status = f"cover: {b['covers'][0].name}" if b["covers"] else "no cover"
                status = f"{ch_count} chapter(s), {cov_status}" if ch_count > 0 else "outline only (no chapters yet)"
                print(f"  [{idx}] {b['prefix']} — \"{b['title']}\" ({status})")
            print("  [B] Back to folder list")
            print("  [Q] Quit")

            b_choice = input("\nEnter book number (or B to go back, Q to quit): ").strip()
            if b_choice.lower() in {"q", "quit", "exit"}:
                print("Cancelled.")
                return
            if b_choice.lower() in {"b", "back"}:
                break

            if not b_choice.isdigit() or not (1 <= int(b_choice) <= len(books)):
                print("Invalid selection. Please enter a book number from the list.")
                continue

            selected_book = books[int(b_choice) - 1]
            if not selected_book["chapters"]:
                print(
                    f"\nNote: '{selected_book['prefix']}' ({selected_book['title']}) only has an outline so far and has no chapter markdown files to generate."
                )
                continue

            # Step 4: Preview contents with Generate / Cancel choice
            while True:
                print_preview(selected_folder, selected_book)
                action = input(
                    "\nStep 3: Choose action — [G]enerate PDF / [T]itle edit / [B]ack / [C]ancel [default: G]: "
                ).strip().lower()

                if action in {"", "g", "generate", "y", "yes"}:
                    # Step 5: Generate PDF
                    generate_book(
                        prefix=selected_book["prefix"],
                        folder_path=selected_folder,
                        book_title=selected_book["title"],
                    )
                    again = input("\nGenerate another book? [y/N]: ").strip().lower()
                    if again in {"y", "yes"}:
                        break
                    return
                elif action in {"t", "title"}:
                    new_title = input(f"Enter new book title [{selected_book['title']}]: ").strip()
                    if new_title:
                        selected_book["title"] = new_title
                elif action in {"b", "back"}:
                    break
                elif action in {"c", "cancel", "q", "quit", "n", "no"}:
                    print("Cancelled.")
                    return
                else:
                    print("Please enter G (Generate), T (Title edit), B (Back), or C (Cancel).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate PDF Book from Markdown Chapters")
    parser.add_argument(
        "prefix",
        nargs="?",
        default=None,
        help="Optional prefix for the book's files (e.g., '01_TKoM'). Omit to run interactive wizard.",
    )
    parser.add_argument(
        "--folder",
        default="2. Chapterbook",
        help="Path to the folder containing chapter markdown files (used when prefix is given).",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output PDF file name (defaults to {prefix}_00_{title}.pdf).",
    )
    parser.add_argument(
        "--title",
        default=None,
        help="Book title (auto-detected from Outline if omitted).",
    )

    args = parser.parse_args()
    if args.prefix:
        generate_book(args.prefix, args.folder, args.output, args.title)
    else:
        try:
            interactive_wizard()
        except KeyboardInterrupt:
            print("\nCancelled.")
