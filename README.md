# MTC Patent Analytics Toolkit

A comprehensive collection of Jupyter notebooks and Python tools for patent information analysis, designed for patent information professionals, PATLIB staff, and patent office personnel. This repository provides practical examples and reusable code for working with EPO data sources and patent analytics workflows.

## Overview

This toolkit demonstrates various approaches to patent data analysis using Python, focusing on EPO data sources and modern visualization techniques. Each module addresses common use cases in patent information work, from family visualization to geographic distribution analysis.

## Repository Structure

### `/deeptechfinder/`
Analysis and visualization of German university patent data from the EPO Deep Tech Finder. Contains:
- Jupyter notebook for data exploration and analysis
- CSV dataset of top 100 German universities from Deep Tech Finder
- Visualization examples for university patent portfolios

### `/familytree/`
Patent family visualization tools developed in collaboration with EPO patent examiners. Features:
- Interactive patent family tree generation
- Jupyter notebooks for family relationship analysis
- Python modules for patent family processing
- Visual examples of complex patent family structures

### `/funwithipc/`
Interactive tools for exploring IPC (International Patent Classification) data:
- Browser-based IPC exploration notebooks
- Classification analysis and visualization tools

### `/ops_ipc/`
Tools for querying and analyzing IPC data using the EPO Open Patent Services (OPS):
- Authentication utilities for OPS API access
- Interactive tutorial for IPC querying
- Python modules for automated IPC analysis

### `/patstat_ipc/`
PATSTAT-based IPC subclass analysis tools:
- Comprehensive IPC subclass statistical analysis
- Jupyter notebooks for classification trend analysis
- Documentation for PATSTAT IPC workflows

### `/piznet/`
Geographic patent distribution analysis at district and federal state level in Germany. Presented at the EPO Patent Knowledge Forum (November 2024):
- Interactive maps using pygwalker
- NUTS (Nomenclature of Territorial Units for Statistics) integration
- District-level patent filing analysis
- Federal state comparison tools
- Custom visualization configurations

### `/training/`
Comprehensive training materials and educational resources:
- **EPAB**: EPO Patent Analytics Bootcamp materials
- **Handbook**: Complete patent analytics handbook with R/Python examples
- **OEPM**: Spanish Patent Office gender analysis examples
- **PATSTAT**: In-depth PATSTAT training modules covering all major tables
- **TIP Introduction**: Technology Intelligence Platform tutorials

## Target Audience

- **Patent Information Experts**: Advanced analytics and visualization tools
- **PATLIB Staff**: Educational materials and practical examples
- **Patent Office Personnel**: Workflow automation and analysis templates
- **Researchers**: Academic examples and methodological approaches
- **Data Analysts**: Technical implementation patterns for patent data

## Key Features

- **Multi-source Integration**: Works with EPO OPS, PATSTAT, Deep Tech Finder, and other patent databases
- **Interactive Visualizations**: Modern web-based charts, maps, and family trees
- **Geographic Analysis**: NUTS-compliant regional patent statistics
- **Classification Tools**: IPC analysis and browsing utilities
- **Educational Content**: Step-by-step tutorials and exercises
- **Production-Ready Code**: Modular Python implementations for reuse

## Getting Started

Each directory contains its own README.md with specific setup instructions. Most notebooks require:
- Python 3.8+
- Jupyter Lab/Notebook
- Common data science libraries (pandas, matplotlib, plotly)
- For OPS access: EPO developer account and API credentials

## Contributing

This toolkit represents ongoing work in patent analytics education and tool development. Contributions, suggestions, and use case examples are welcome from the patent information community.

## License

Please refer to individual directories for specific licensing information. Training materials may have separate license terms from the EPO. 
