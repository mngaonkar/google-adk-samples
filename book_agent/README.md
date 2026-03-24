# Book Agent
This project demonstrates how to create a book agent using the Google ADK. The book agent is designed to generate comprehensive content on a specific topic, organize it into chapters, and ensure that the information is accurate and well-structured.

> **Note:** This agent uses the shared SDK located at `/sdk` in the workspace root. The SDK provides agent factories, registries, and utilities that can be used by any agent in the workspace.

## Agent Architecture

```mermaid
graph TD
    A["User Request: Book Topic"] --> B["TOC Agent"]
    B -->|"Creates comprehensive<br>Table of Contents"| C["TOC with Chapters"]
    
    C --> D1["Chapter Agent 1"]
    C --> D2["Chapter Agent 2"]
    C --> D3["Chapter Agent N"]
    
    D1 -->|"Chapter 1 Content"| E1["Reviewer Agent 1"]
    D2 -->|"Chapter 2 Content"| E2["Reviewer Agent 2"]
    D3 -->|"Chapter N Content"| E3["Reviewer Agent N"]
    
    E1 -->|"Reviewed and Revised"| F["Collation Agent"]
    E2 -->|"Reviewed and Revised"| F
    E3 -->|"Reviewed and Revised"| F
    
    F -->|"Compiled Book"| G["Final Book Document"]
```

### Architecture Flow

1. **TOC Agent** - Takes the user's book topic request and creates a comprehensive Table of Contents with all chapters

2. **Chapter Agents** - Multiple specialized agents that work in parallel, each picking up one chapter from the TOC and creating comprehensive content

3. **Reviewer Agents** - Each chapter's output is reviewed by a reviewer agent that revises and improves the content

4. **Collation Agent** - Collects all the reviewed chapter contents and compiles them into a single, cohesive book document
