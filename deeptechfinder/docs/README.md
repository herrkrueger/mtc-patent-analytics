# DeepTechFinder Patent Analytics v2.0

A comprehensive ETL-based platform for analyzing German university patent portfolios using EPO's DeepTechFinder data and EPO OPS API integration.

## 🚀 Features

- **ETL Architecture**: Clean Extract → Transform → Load → Analyze workflow
- **University-Focused**: Dynamic analysis of individual university patent portfolios
- **EPO OPS Integration**: Real-time bibliographic data enrichment
- **Advanced Normalization**: Proper handling of priorities, inventors, and applicants
- **CLI-First Design**: Command-line interface for reliable automation
- **Jupyter Ready**: Simple notebook integration for interactive analysis

## 📊 Coverage

- **100 German Universities** with 11,118 total patent applications
- **4,907 granted patents** across all institutions  
- **1.8M+ students** represented in the dataset
- **Real-time EPO OPS data** for complete patent intelligence

## 🏗️ Architecture

```
deeptechfinder/
├── src/
│   ├── etl/           # Extract, Transform, Load pipeline
│   ├── analysis/      # Portfolio analysis engines
│   ├── export/        # CSV, PDF, JSON exporters
│   └── core/          # Configuration and orchestration
├── cli/               # Command-line interface
├── tests/             # Comprehensive test suite
├── legacy/            # Archived working scripts
└── docs/              # Documentation
```

## 🔧 Quick Start

### 1. Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Ensure EPO OPS credentials are available in `../ipc-ops/.env`:
```
OPS_KEY=your_consumer_key
OPS_SECRET=your_consumer_secret
```

### 3. Test System

```bash
# Test all components
python -m cli.main test

# List available universities
python -m cli.main list

# Test EPO OPS API
python -m cli.main test-api EP19196837A
```

### 4. Analyze University

```bash
# Quick analysis (10 patents)
python -m cli.main analyze "TU Dresden" --limit 10

# Comprehensive analysis (50 patents)
python -m cli.main analyze "Technische Universität Dresden" --limit 50

# Maximum analysis (200 patents)
python -m cli.main analyze "Karlsruhe Institute of Technology" --limit 200
```

## 📋 ETL Pipeline

### Extract Phase
- **DeepTechFinder CSV**: University patent applications (latin-1 encoding)
- **EPO OPS API**: Complete bibliographic data with rate limiting

### Transform Phase  
- **Priority Normalization**: German priorities + fallback to first priority
- **Inventor Standardization**: Eliminates comma-based duplicates
- **Applicant Categorization**: University vs Industry/Other classification

### Load Phase
- **Structured Data Models**: Pydantic validation and type safety
- **Portfolio Aggregation**: University-specific patent portfolios

### Analyze Phase
- **Collaboration Analysis**: Industry partnerships and research networks
- **Priority Strategy**: Filing patterns and family relationships  
- **Inventor Networks**: Research community mapping
- **Technology Classification**: Patent category analysis

## 🎯 Key Capabilities

### University Portfolio Analysis
```python
from src.core.university_engine import UniversityEngine

engine = UniversityEngine()
result = engine.analyze_university("TU Dresden", patent_limit=50)

# Access results
portfolio = result.portfolio
collaboration = result.collaboration_insights
priorities = result.priority_analysis
inventors = result.inventor_network
```

### Data Export
- **CSV Files**: Complete datasets for further analysis
- **PDF Reports**: Professional documents for stakeholders
- **JSON Export**: Structured data for applications

### Proven Methodology
- **100% EPO OPS Success Rate**: Validated on TU Dresden (265 patents)
- **German Priority Detection**: Correct handling of DE priorities
- **Industry Collaboration**: Complete partnership mapping
- **Leading Zero Handling**: Critical for 2000s-era patents

## 🔍 Example Analysis

**TU Dresden Analysis Results:**
- 265 granted EP patents (full portfolio available)
- 88% German priority rate (exceptional filing strategy)
- 169 unique inventors (extensive research network)
- 38 industry partners (strong collaboration ecosystem)
- 100% EPO OPS retrieval success

## 📚 Documentation

- [`ETL_PIPELINE.md`](ETL_PIPELINE.md) - Detailed ETL process documentation
- [`API_REFERENCE.md`](API_REFERENCE.md) - Code API documentation  
- [`MIGRATION_GUIDE.md`](MIGRATION_GUIDE.md) - Legacy → v2.0 migration
- [`legacy/CLAUDE_LEGACY.md`](legacy/CLAUDE_LEGACY.md) - Original implementation notes

## 🧪 Testing

```bash
# Run test suite
python -m pytest tests/

# Test specific component
python -m pytest tests/test_etl/

# Integration tests
python -m pytest tests/test_integration/
```

## 🏛️ Target Users

- **Patent Information Professionals**: Enhanced due diligence and FTO analysis
- **PATLIB Staff**: University patent portfolio intelligence  
- **Technology Transfer Offices**: Strategic partnership identification
- **Research Institutions**: Competitive analysis and collaboration opportunities
- **Patent Attorneys**: Comprehensive prior art and inventor network mapping

## 📈 Performance

- **Processing Speed**: ~2 patents/minute (EPO OPS rate limiting)
- **Success Rate**: 100% on validated datasets
- **Memory Efficient**: Processes universities individually
- **Scalable**: Handles 1-200 patents per analysis

## 🔗 Legacy Integration

All working code from the previous implementation is preserved in the `legacy/` directory:
- `legacy/scripts/` - Original analysis scripts
- `legacy/notebooks/` - Development notebooks
- `legacy/DTF_OPS_University_Analysis.ipynb` - Original interactive notebook

## 🤝 Contributing

This is a professional patent analytics platform. All contributions should maintain:
- Clean ETL architecture
- Comprehensive error handling
- EPO OPS compliance
- Patent data accuracy
- Documentation standards

## 📜 License

Professional patent analytics software for academic and research use.