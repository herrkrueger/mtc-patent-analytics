# CLAUDE.md - DeepTechFinder Patent Analytics v2.0

This file provides guidance to Claude Code (claude.ai/code) when working with the ETL-based DeepTechFinder patent analytics platform.

## Project Architecture Overview

This is a **professional ETL-based patent analytics platform** designed for comprehensive university patent portfolio analysis. The system follows Extract → Transform → Load → Analyze principles with a focus on EPO OPS API integration and German university patents.

## Development Guidelines

### Core Architecture Principles

**ETL Pipeline Structure:**
```
Extract → Transform → Load → Analyze → Export
   ↓         ↓         ↓        ↓        ↓
 CSV +    Normalize  Structured Portfolio  Reports
EPO OPS   All Data   Models    Analysis   & Data
```

**Key Directories:**
- `src/etl/extract/` - Data acquisition (CSV + EPO OPS)
- `src/etl/transform/` - Data normalization (priorities, inventors, applicants)
- `src/etl/load/` - Structured data models (Pydantic validation)
- `src/analysis/` - Portfolio analysis engines
- `src/export/` - Report generation (CSV, PDF, JSON)
- `src/core/` - Configuration and orchestration
- `cli/` - Command-line interface (primary interface)

### Critical Implementation Notes

**Data Sources:**
- **DeepTechFinder CSV**: `data/EPO_DeepTechFinder_20250513_DE_Uni_Top100.csv` 
- **Encoding**: MUST use `latin-1` encoding (not UTF-8)
- **EPO OPS API**: Application endpoint with proper authentication

**EPO OPS Integration (Validated Patterns):**
- **Endpoint**: `published-data/application/epodoc/EP{number}/biblio`
- **Headers**: `Authorization: Bearer {token}` + `Accept: application/json` (CRITICAL)
- **Rate Limiting**: 2-second intervals between requests (mandatory)
- **Number Formatting**: Preserve leading zeros for 2000s patents
- **Fallback Strategy**: Try multiple number formats for compatibility

**Priority Extraction (Corrected Logic):**
- **JSON Structure**: `priority-claims` → `priority-claim` entries
- **Strategy**: Prefer German (DE) priorities, fallback to first available
- **Format**: `DE102123456A·2021-03-15` for German applications

**Data Normalization:**
- **Inventors**: Eliminate comma-based duplicates with proper name standardization
- **Applicants**: Categorize as "University" vs "Industry/Other"
- **Classifications**: Clean IPC formatting, remove extra spaces

### University Processing Workflow

**Single University Analysis (Core Capability):**
```python
from src.core.university_engine import UniversityEngine

engine = UniversityEngine()
result = engine.analyze_university("TU Dresden", patent_limit=50)

# ETL results available in structured format
portfolio = result.portfolio              # Complete portfolio data
collaboration = result.collaboration_insights  # Industry partnerships
priorities = result.priority_analysis     # Filing strategies  
inventors = result.inventor_network       # Research networks
```

**CLI Usage (Primary Interface):**
```bash
# System testing
python -m cli.main test
python -m cli.main list

# University analysis  
python -m cli.main analyze "TU Dresden" --limit 50
python -m cli.main test-api EP19196837A
```

### Proven Methodology Integration

**Legacy Code Preservation:**
- `legacy/scripts/` - Contains working EPO OPS patterns
- `legacy/notebooks/` - Development history and examples
- Reference implementation patterns from `tu_dresden_analysis.py`

**Validated Results (TU Dresden):**
- 265 granted EP patents analyzed successfully
- 100% EPO OPS retrieval success rate
- 88% German priority rate (systematic filing strategy)
- 38 industry collaboration partners identified

**Data Quality Assurance:**
- All transformations maintain data integrity
- Pydantic models ensure type safety
- Comprehensive error handling at each ETL stage
- Rate limiting compliance with EPO OPS terms

### Configuration Management

**Settings**: `config/settings.yaml`
- Application configuration
- EPO OPS endpoints and rate limits
- Analysis parameters and defaults
- Export options and file handling

**Credentials**: `../ipc-ops/.env`
- EPO OPS authentication (OPS_KEY, OPS_SECRET)
- Loaded automatically by configuration system

### Development Workflow

**For New Features:**
1. **Test CLI first** - Ensure core functionality works
2. **Add to ETL pipeline** - Maintain clean separation of concerns  
3. **Update data models** - Use Pydantic for validation
4. **Create tests** - Ensure reliability and regression prevention
5. **Document changes** - Update relevant documentation

**For Bug Fixes:**
1. **Reproduce with CLI** - Use command-line for debugging
2. **Check legacy patterns** - Reference working code in `legacy/`
3. **Validate with known data** - Test against TU Dresden results
4. **Maintain compatibility** - Ensure EPO OPS compliance

### Testing and Validation

**System Testing:**
```bash
python -m cli.main test                    # Test all components
python -m cli.main test-api EP19196837A   # Test EPO OPS specifically
python -m cli.main analyze "TU Dresden" --limit 5  # Quick validation
```

**Integration Testing:**
- Compare results with legacy outputs in `output/`
- Validate against known working patents
- Ensure 100% success rate on validated datasets

### Export Capabilities

**Data Export Options:**
- **CSV**: Complete datasets for further analysis
- **PDF**: Professional reports with ReportLab
- **JSON**: Structured data for applications

**File Naming**: Automatic sanitization for safe filesystem operations

### For Jupyter Notebook Development

**Simple Integration Pattern:**
```python
# Import the engine
from src.core.university_engine import UniversityEngine

# Use ETL pipeline
engine = UniversityEngine()
result = engine.analyze_university("University Name", limit=20)

# Access structured results
portfolio = result.portfolio
# ... create visualizations with clean data
```

**Notebook Best Practices:**
- Use the ETL engine rather than reimplementing logic
- Focus on visualization and presentation
- Import from `src/` modules for functionality
- Keep notebooks clean and focused on analysis presentation

### Legacy Migration Notes

**What's Preserved:**
- All working EPO OPS patterns
- Proven data extraction logic  
- Successful analysis methodologies
- Historical results for validation

**What's Improved:**
- Clean ETL architecture
- Proper error handling
- Pydantic data validation
- CLI-first development
- Comprehensive testing
- Professional documentation

### Performance Characteristics

- **Processing Speed**: ~2 patents/minute (EPO OPS rate limited)
- **Memory Usage**: Minimal (processes one university at a time)
- **Success Rate**: 100% on validated datasets
- **Scalability**: 10-200 patents per analysis

This architecture provides a solid foundation for professional patent analytics while maintaining compatibility with proven working patterns from the legacy implementation.