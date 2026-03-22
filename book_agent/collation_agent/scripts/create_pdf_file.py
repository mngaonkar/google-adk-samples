from sdk.utils import read_from_file
import uuid
from markdown_pdf import Section, MarkdownPdf
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_pdf_file(chapter_locations: list[str], toc_location: Optional[str] = None) -> str:
    """Create a PDF file from chapter content.
    
    Args:
        chapter_locations: list[str] - list of chapter locations
        toc_location: str - path to the Table of Contents file (optional)

    Returns:
        pdf_file: str - path to the created PDF file
    """

    pdf_file = f"workspace/collation_response_{uuid.uuid4()}.pdf"
    
    # Enable TOC with level 2 (includes # and ## headings)
    markdown_pdf = MarkdownPdf(toc_level=2)

    # Set PDF metadata
    markdown_pdf.meta["title"]    = "AI Generated Book"
    markdown_pdf.meta["author"]   = "AI Agent"
    markdown_pdf.meta["subject"]  = "Book"

    # Add table of contents as first section if provided
    if toc_location:
        try:
            toc_content = read_from_file(toc_location)
            logger.info(f"Adding TOC from {toc_location}")
            
            # Add TOC as a dedicated section with title
            toc_section = f"# Table of Contents\n\n{toc_content}"
            markdown_pdf.add_section(Section(toc_section))
        except Exception as e:
            logger.warning(f"Could not read TOC file: {e}")

    # Add all chapter content
    for i, chapter_location in enumerate(chapter_locations, start=1):
        chapter_content = read_from_file(chapter_location)
        logger.info(f"Adding chapter {i} from {chapter_location}")
        markdown_pdf.add_section(Section(chapter_content))

    markdown_pdf.save(pdf_file)
    logger.info(f"PDF file created successfully at {pdf_file}")

    return pdf_file

def main():
    chapter_locations = [
        "workspace/chapter_1_content.md",
        "workspace/chapter_2_content.md",
        "workspace/chapter_3_content.md"
    ]
    toc_location = "workspace/table_of_contents.md"  # Optional TOC file
    
    pdf_file = create_pdf_file(chapter_locations, toc_location)
    print(f"PDF created: {pdf_file}")

if __name__ == "__main__":
    main()