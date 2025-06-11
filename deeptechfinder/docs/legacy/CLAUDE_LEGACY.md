# CLAUDE.md - Deep Tech Finder Patent Analytics

This file provides guidance to Claude Code (claude.ai/code) when working with the Deep Tech Finder patent analytics module.

## Project Overview

This module focuses on analyzing German university patents from the DeepTechFinder dataset using EPO OPS API integration. It provides comprehensive patent analytics specifically for academic institutions and their patent portfolios.

## Development Guidelines

### Important Workflow Tips
- Always use NotebookEdit when reading or changing Jupyter Notebooks to prevent errors like "Error: File is a Jupyter Notebook. Use the NotebookEdit to edit this file"
- 
- **Notebook Cell Best Practices**:
  - Use **markdown cells** for documentation, explanations, and static information
  - Start with a documentation of the content, methodology and expectations
  - Finish with a Executive Summary without dynamic content, of what was achieved be executing the cells
  - Use **code cells** only for executable code and dynamic outputs
  - Avoid code cells that only print static text or documentation, put this in markdown cells above instead
  - Comprehensive markdown documentation for patent searchers
  - Professional presentation format with clear methodology
  - Export capabilities for further analysis (CSV with complete bibliographic data)
  
### Critical CSV Data Encoding
- **DeepTechFinder CSV encoding**: The main data file `data/EPO_DeepTechFinder_20250513_DE_Uni_Top100.csv` requires **latin-1 encoding**
- **Standard UTF-8 fails**: Must explicitly specify `encoding='latin-1'` when reading with pandas
- **File structure**: 11,118 rows across 100 German universities with 10 columns
- **Script Implementation**: All scripts properly handle multiple encoding attempts (utf-8, latin-1, iso-8859-1, cp1252)

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

### Data Files and Structure

**Input Data**: 
- `data/EPO_DeepTechFinder_20250513_DE_Uni_Top100.csv` - German university patents from DeepTechFinder

**Output Structure**:
- `{university}_applicants.csv` - Extracted applicant information
- `{university}_inventors.csv` - Extracted inventor information  
- `{university}_german_priorities.csv` - German priority claims analysis
- `{university}_complete_analysis.csv` - Comprehensive patent analysis

**Analysis Scripts** (in `./scripts/` directory):
- `analyze_universities.py` - Complete university dataset analysis and JSON generation (creates `output/university_analysis.json`)
- `university_data_loader.py` - Easy-to-use data loader functions for interactive widgets (used by DTF_OPS_University_Analysis.ipynb)
- `humboldt_analysis.py` - Humboldt University specific patent analysis
- `tu_chemnitz_analysis.py` - TU Chemnitz comprehensive patent portfolio analysis  
- `tu_dresden_analysis.py` - TU Dresden analysis (validated methodology template, basis for interactive platform)
- `test_priority_analysis.py` - Priority analysis functionality testing
- `test_priority_analysis_fixed.py` - Fixed version of priority analysis tests

**Script Dependencies**:
- Interactive notebook `DTF_OPS_University_Analysis.ipynb` requires `output/university_analysis.json` (generated by `analyze_universities.py`)
- Widget functionality uses helper functions from `scripts/university_data_loader.py`
- Analysis methodology based on proven patterns from `tu_dresden_analysis.py`

### Interactive Analysis Platform Development

**DTF_OPS_University_Analysis.ipynb - Comprehensive Makeover Completed**:
- **Interactive University Selection**: Built complete widget-based interface with 100 German universities
- **Advanced Sorting & Filtering**: By student count, patent applications, grant rate, alphabetical
- **Real-time Search**: Dynamic filtering with instant university list updates
- **Multi-Analysis Options**: Complete, priority, collaboration, inventors, technology analysis types
- **Professional PDF Generation**: Automated report creation with ReportLab integration
- **Comprehensive CSV Exports**: Complete datasets for all analysis components

**Key Technical Achievements**:
- **Widget Event Handling**: Proper observer patterns for dynamic UI updates
- **Performance Optimization**: Configurable patent limits (10-200) for scalable analysis
- **Error Handling**: Comprehensive exception management and user feedback
- **Rate Limiting**: EPO OPS compliant 2-second intervals between requests
- **Data Normalization**: Advanced applicant/inventor name standardization
- **Category Classification**: Automated industry partner categorization across 6 sectors

**Analysis Framework Extensions**:
- **Portfolio Overview**: Key metrics, collaboration rates, filing strategies
- **Industry Collaboration Deep Dive**: Partner categorization, timeline evolution, strategic insights
- **Priority Family Analysis**: German filing strategy assessment, family relationships, timing patterns
- **Technology Portfolio Sampling**: Representative patent showcase with complete bibliographic data
- **Strategic Assessment**: Automated collaboration and filing strategy evaluation

**Proven Methodology Integration**:
- Based on validated TU Dresden (265 patents) and HTW Saarland frameworks
- 100% EPO OPS retrieval success rates maintained
- Leading zero handling for 2000s patents (critical discovery preserved)
- Application endpoint usage for German university patents (key finding applied)

**Export Capabilities**:
- **CSV Data Files**: Complete analysis, applicants, inventors, German priorities
- **PDF Reports**: Professional multi-page documents with tables, formatting, strategic insights
- **Safe Filename Handling**: University name normalization for file system compatibility
- **Stakeholder-Ready Outputs**: Executive summaries, detailed analysis sections, methodology notes

**User Experience Enhancements**:
- **Step-by-Step Workflow**: Clear progression from selection to analysis to export
- **Real-time Feedback**: Progress indicators, success/failure notifications, estimated time
- **Flexible Configuration**: Multiple analysis types, patent limits, PDF generation toggle
- **Professional Presentation**: Clean interface with proper spacing, headers, and visual hierarchy

### Project Structure

**Main Analysis Notebooks** (root directory):
- `DTF_OPS_University_Analysis.ipynb` - **PRIMARY**: Interactive analysis platform with university selection widgets

**Historical/Development Notebooks** (in `./notebooks/` directory):
- `1 DE Universities from DTF.ipynb` - Initial university data exploration
- `2 German_University_Patent_Analysis.ipynb` - Early analysis framework development  
- `3 EPO_OPS_Family_Analysis_Simple.ipynb` - **ORIGINAL**: Simple family analysis (basis for makeover)
- `4 Interactive_University_Widget_Example.ipynb` - Widget development examples and demonstrations (updated to use `./scripts/` imports)
- `Humboldt_University_Analysis.ipynb` - Humboldt University case study
- `TU_Chemnitz_Analysis.ipynb` - TU Chemnitz analysis results
- `TU_Dresden_Analysis.ipynb` - TU Dresden comprehensive analysis (validated methodology)

**Data Sources**:
- `./data/EPO_DeepTechFinder_20250513_DE_Uni_Top100.csv` - Master dataset with 100 German universities

**Data Format Notes**:
- EP patent numbers extracted from `Espacenet_link` column (format: https://worldwide.espacenet.com/patent/search?q=EP80100298A)
- Filing dates in `Filing_year` column use M/D/YY or M/D/YYYY format requiring conversion
- University names in `University` column must match exactly for filtering
- Patent status filtering via `Patent_status` column (focus on 'EP granted' patents)

**Output Directory**:
- `./output/` - All analysis results, CSV exports, PDF reports, and generated data files

**Scripts Directory**:
- `./scripts/` - All Python analysis scripts and utility functions

**Proven Methodology Available**: The implementation can directly leverage the working code from:
- `scripts/tu_dresden_analysis.py` (validated with 100% success rate on 265 patents)
- `scripts/humboldt_analysis.py` (comprehensive analysis framework)
- `scripts/university_data_loader.py` (data loading utilities already in use)
- `mtc-patent-analytics/deeptechfinder/notebooks/4 Interactive_University_Widget_Examples.ipynb` (widget with university data)

### For Python/Jupyter Development
- Follow existing code patterns for university-specific analysis
- Document analysis methodology clearly for patent professionals
- **Interactive Widgets**: Use ipywidgets for user-friendly interfaces with proper event handling
- **PDF Generation**: ReportLab integration for professional report creation
- **Data Export**: Systematic CSV generation with proper filename sanitization
- **Notebook Organization**: Keep main analysis tools in root, archive development notebooks in `./notebooks/`
- **EPO OPS Credentials**: Located in `../ipc-ops/.env` with working OPS_KEY and OPS_SECRET