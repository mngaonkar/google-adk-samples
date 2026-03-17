---
name: collation_agent
description: Create a final book content by collating all chapter contents into a PDF.
license: Apache-2.0
metadata:
  author: "Mahadev Gaonkar"
  version: "1.0"
---
# Collation Agent

## Objective
Create a professional PDF book from chapter markdown files with an optional Table of Contents.

## Inputs
  - `chapter_locations`: List of paths to chapter markdown files
  - `toc_location`: Optional path to Table of Contents markdown file

## Tools Available
1. **create_pdf_file(chapter_locations: list[str], toc_location: str = None)** - Creates PDF from markdown files
   - `chapter_locations`: List of paths to chapter markdown files
   - `toc_location`: Optional path to Table of Contents markdown file
   - Returns: Path to created PDF file

## Instructions

### Step 1: Gather Inputs
- Extract `chapter_locations` list from the input
- Extract `toc_location` if available

### Step 2: Create PDF
- Call `create_pdf_file` with both parameters:
  ```python
  create_pdf_file(chapter_locations, toc_location)
  ```
- If TOC is available, it will be added as the first section in the PDF
- Chapters will follow in the order provided

### Step 3: Verify Output
- Tool returns the path to the created PDF file
- Log the success and return the PDF path

## Output Format
Return the PDF file path as text, for example:
```
file_system/collation_response_abc123.pdf
```

## Best Practices
- Always include TOC location if available for better book structure
- Ensure chapter locations are in correct order
- Verify all file paths exist before calling the tool
- Log any warnings or errors encountered
