# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains DiviTree (Divitree), a patent family tree visualization tool built for the Technology Intelligence Platform (TIP). It visualizes European Patent Office (EPO) divisional patents and their relationships using data from OPS (Open Patent Services).

## Key Architecture

The application consists of several main components:

### Core Classes
- **FamilyRecord** (`patent_analysis/family_record.py`): Manages patent family data retrieval from EPO's OPS API, handles XML parsing, and creates pandas DataFrames with patent relationships
- **PatentProcessor** (`patent_analysis/patent_processor.py`): Main interactive interface providing Jupyter widgets for user input and orchestrating the data processing workflow
- **TreeCreation** (`patent_analysis/tree_creation.py`): Converts patent data into hierarchical tree structures with parent-child relationships
- **TreeProcessor** (`patent_analysis/tree_processor.py`): Processes tree structures and generates output files for visualization

### Key Workflows
1. User inputs patent reference (application/publication) via Jupyter widgets
2. FamilyRecord fetches XML data from OPS API and parses family relationships
3. TreeCreation builds hierarchical structure from priority numbers and divisional relationships
4. Data is visualized using Plotly sunburst charts showing patent family hierarchies

## Environment Setup

This project requires:
- EPO OPS API credentials (OPS_KEY and OPS_SECRET) stored in `.env` file
- The `epo-tipdata-ops` library for OPS API access
- Jupyter notebook environment with plotly, pandas, and ipywidgets

## Common Commands

Since this is primarily a Jupyter notebook-based project, most operations are performed within the notebook interface. The main entry point is `Divitree.ipynb`.

To run the application:
1. Ensure `.env` file contains valid OPS credentials
2. Open and run `Divitree.ipynb`
3. Use the interactive widgets to input patent numbers
4. Process results to generate sunburst visualizations

## Data Processing Flow

The system processes patent data through these stages:
1. **API Retrieval**: Fetch XML family data from OPS
2. **XML Parsing**: Extract application numbers, priority claims, publication data, and legal events
3. **Tree Building**: Create nested dictionary structures representing family relationships
4. **Visualization**: Generate interactive sunburst charts showing divisional patent hierarchies

## File Structure Notes

- `patent_analysis/` contains all core Python modules
- `images/` stores sample patent family visualizations
- The main notebook demonstrates the complete workflow from data input to visualization