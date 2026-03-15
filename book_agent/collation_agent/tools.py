from sdk.utils import read_from_file
import uuid
from markdown_pdf import Section, MarkdownPdf
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_pdf_file(chapter_locations: list[str]) -> str:
    """Create a PDF file from chapter content.
    
    Args:
        chapter_locations: list[str] - list of chapter locations

    Returns:
        pdf_file: str - path to the created PDF file
    """

    pdf_file = f"file_system/collation_response_{uuid.uuid4()}.pdf"
    # toc_level=0 disables TOC; PyMuPDF requires the first TOC entry to be level 1,
    # and chapter content may start with ## or deeper, which would raise ValueError.
    markdown_pdf = MarkdownPdf(toc_level=0)
    markdown_pdf.meta["title"]    = "My Document"
    markdown_pdf.meta["author"]   = "AI Agent"
    markdown_pdf.meta["subject"]  = "Book"

    for chapter_location in chapter_locations:
        chapter_content = read_from_file(chapter_location)
        markdown_pdf.add_section(Section(chapter_content))

    markdown_pdf.save(pdf_file)
    logger.info(f"PDF file created successfully at {pdf_file}")

    return pdf_file

def main():
    chapter_locations = [
        "file_system/chapter_1_content.md",
        "file_system/chapter_2_content.md",
        "file_system/chapter_3_content.md"
    ]
    pdf_file = create_pdf_file(chapter_locations)
    print(pdf_file)

if __name__ == "__main__":
    main()