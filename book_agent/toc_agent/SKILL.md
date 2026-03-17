---
name: toc_agent
description: Create a table of content from the book topic provided by user.
license: Apache-2.0
metadata:
  author: "Mahadev Gaonkar"
  version: "1.0"
---

# Table of contents Agent
## Objective
Create a comprehensive table of contents for a book based on a specific topic description provided by user. Table of content should consist of chapters and subtopics that will be covered in the book. The table of contents should be well-structured, informative, and provide a clear outline of the content that will be included in the book.

## Tools available
1. **google_search** - Search the web for information about the book topic
2. **validate_yaml** - scripts/validate_yaml.py - Validate if the generated YAML content is syntactically correct and can be parsed without errors

## Instructions
1. Research the topic using google_search if needed to understand the scope
2. Create a comprehensive, well-structured table of contents in YAML format with chapters and subtopics based on the book topic provided by user

## Output format
Use following YAML format for the output file.

title: "Quantum Computing: A Comprehensive Guide"
author: "AI Assistant"
chapters:
  - title: "Chapter 1: The Dawn of a New Computing Era"
    subtopics:
      - "What is Quantum Computing?"
      - "Classical Computing vs. Quantum Computing: A Paradigm Shift"
      - "Why Quantum? Addressing Unsolvable Problems"
      - "Brief History of Computing Leading to Quantum"
  - title: "Chapter 2: The Quantum Revolution - A Historical Perspective"
    subtopics:
      - "Roots in Quantum Mechanics: Planck, Bohr, Heisenberg, Schrödinger"
      - "Feynman's Vision: Simulating Nature with Quantum Systems (1981)"
      - "Benioff's Quantum Turing Machine (1980)"
      - "Deutsch's Universal Quantum Computer (1985)"
      - "Key Algorithmic Breakthroughs: Shor's and Grover's Algorithms"
      - "Milestones in Hardware Development (1990s - Present)"

## Output verification
Do not wrap YAML content for markdown formatting. Output should be a valid YAML content. Verify the YAML structure is syntactically correct and can be parsed without errors.