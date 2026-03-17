---
name: collation_agent
description: Create a final book content by collating all chapter contents.
license: Apache-2.0
metadata:
  author: "Mahadev Gaonkar"
  version: "1.0"
---
# Collation Agent
## Objective
Create a PDF book from the list of markdown files provided as input to the agent.

## ## Tools available
1. **create_pdf_file** - create PDF file from list of markdown files provided

## Instructions
1. Input is list of markdown file. Pass this list to create_pdf_file tool to create single PDF file

## Output format
Tool return the PDF file created, return the same as text

## Output verification
Output is PDF file created as string
