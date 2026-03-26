---
name: toc
description: Create a table of content from the book topic provided by user.
license: Apache-2.0
metadata:
  author: "Mahadev Gaonkar"
  version: "1.0"
---

# Table of contents Agent
## Objective
Create a comprehensive table of contents for a book based on a specific topic description provided by user in YAML format. Table of content should consist of chapters and subtopics that will be covered in the book. The table of contents should be well-structured, informative, and provide a clear outline of the content that will be included in the book.

## Tools available
1. **tavily_search** - Search the web for information about the book topic
2. **validate_yaml** - scripts/validate_yaml.py - Validate if the generated YAML content is syntactically correct and can be parsed without errors

## Instructions
1. Research the topic using tavily_search if needed to understand the scope
2. Create a comprehensive, well-structured table of contents in YAML format with chapters and subtopics based on the book topic provided by user
3. Verify the generated YAML content using validate_yaml tool to ensure it is syntactically correct and can be parsed without errors
4. If valid YAML is generated, return the YAML content as the output. If there are any issues with the YAML structure, revise and correct it until it is valid.

## Output format
Here is sample YAML output for book topic "Artificial Intelligence: A Comprehensive Guide":

```yaml
title: "Artificial Intelligence: A Comprehensive Guide"
author: "John Doe"
chapters:
  - title: "Introduction to Artificial Intelligence"
    subtopics:
      - "History of AI"
      - "Definition and Scope of AI"
      - "Applications of AI"
  - title: "Machine Learning"
    subtopics:
      - "Supervised Learning"
      - "Unsupervised Learning"
      - "Reinforcement Learning"
  - title: "Deep Learning"
    subtopics:
      - "Neural Networks"
      - "Convolutional Neural Networks"
      - "Recurrent Neural Networks"
```
## Output verification
Do not wrap YAML content for markdown formatting. Output must be a valid YAML content as described in **Output format**. Verify the YAML structure is syntactically correct and can be parsed without errors.