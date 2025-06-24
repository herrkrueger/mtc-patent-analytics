# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **comprehensive patent analytics toolkit** designed for patent information professionals, PATLIB staff, and patent office personnel. The repository contains multiple specialized modules for different aspects of patent data analysis, from interactive web applications to Jupyter-based analytical workflows. The toolkit demonstrates various approaches to patent data analysis using EPO data sources and modern visualization techniques.

## Development Guidelines

### Important Workflow Tips
- Always use NotebookEdit when reading or changing Jupyter Notebooks to prevent errors like "Error: File is a Jupyter Notebook. Use the NotebookEdit to edit this file"
- **Notebook Cell Best Practices**:
  - Use **markdown cells** for documentation, explanations, and static information
  - Use **code cells** only for executable code and dynamic outputs
  - Avoid code cells that only print static text or documentation
  - Keep notebooks clean and focused on functionality, not verbose explanations

### EPO OPS API Integration (Key Findings)
**Working Configuration for German University Patents:**
- **Endpoint**: `published-data/application/epodoc/EP{number}/biblio`
- **Authentication**: OAuth2 with credentials in `ipc-ops/.env`
- **Format Processing**: Remove "EP" prefix, remove leading zeros, remove kind codes (A/B)
- **Example**: EP19196837A → `published-data/application/epodoc/EP19196837/biblio`

**Critical Discovery**: German university patents from DeepTechFinder are **application numbers**, NOT publication numbers. Must use `/application/` endpoint instead of `/publication/`.

**OPS Response Structure for Data Extraction:**
- **Applicants**: Search for keys containing 'applicant' → extract 'applicant-name' + 'residence.country'
- **Inventors**: Search for keys containing 'inventor' → extract 'inventor-name' + 'residence.country'  
- **Priority Claims**: Search for 'priority-claim' → extract 'country' + 'doc-number' + 'date'
- **Application Info**: Search for 'application-reference' → extract 'document-id' components
- **Title**: Search for 'invention-title' → extract text content (may be in '$' or '#text' fields)

**Verified Working Patents:**
- EP19196837A (Technische Universität Dresden)
- EP18826058A (University of Applied Sciences Saarbrücken)
- EP09735811A (University of Applied Sciences Saarbrücken) - required leading zero fix

**Critical Leading Zero Discovery**: 
- Patents from 2000s (EP09735811A) require leading zero preservation: `EP09735811` not `EP9735811`
- Older patents (EP80100298A) can have leading zeros removed: `EP80100298`
- Implement fallback strategy: try with leading zero first, then without if 404

**Rate Limiting**: Standard EPO OPS limits apply - implement delays between requests.

**Data Extraction Issues Resolved**:
- **Duplicate Data**: EPO OPS returns multiple formats (epodoc, original) for same entities
- **Solution**: Prefer 'original' format for cleaner names, deduplicate entries
- **Priority Claims**: Extract from `priority-claims` section with proper date formatting
- **CPC Classifications**: Located in `patent-classifications` not `classifications-cpc`
- **IPC Formatting**: Clean spaces from "G01B   5/    00" → "G01B5/00"
- **Title Selection**: Prefer English (@lang="en"), fallback to first available

**Production Notebook Structure**:
- Comprehensive markdown documentation for patent searchers
- Professional presentation format with clear methodology
- Each code cell has purpose statement and searcher context
- Export capabilities for further analysis (CSV with complete bibliographic data)

### For Python/Jupyter Development
- Use virtual environments for dependency management
- Follow existing code patterns in each module
- Test with PATSTAT TEST environment before PROD
- Document new analysis workflows in notebooks

[... rest of the original file content remains the same ...]