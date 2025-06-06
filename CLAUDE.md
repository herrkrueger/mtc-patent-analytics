# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **patent data science project** that demonstrates patent analysis using the European Patent Office's Technology Intelligence Platform. The project analyzes German patent data (PATSTAT) to create interactive visualizations of patent applicant and technology distributions across German NUTS Level 3 regions (Landkreise).

## Key Technologies and Dependencies

- **Python** with Jupyter notebooks for interactive analysis
- **EPO Technology Intelligence Platform** via `epo.tipdata.patstat` client
- **PATSTAT Database** for patent data queries
- **SQLAlchemy ORM** for database interactions
- **Pandas** for data manipulation
- **Pygwalker** for Tableau-like interactive visualizations
- **lxml** for XML parsing of IPC/CPC classification schemes
- **GeoPandas** for geographical data handling

## Main Entry Points

- `epo_pkf2024_piznet_final.ipynb` - Primary presentation notebook for Patent Knowledge Forum 2024
- `patentknowledgeforum2024.ipynb` - Alternative implementation
- `notebooks/patstat_nuts_de_with_explanations.ipynb` - Detailed tutorial version
- `notebooks/ipcbrowser.ipynb` - IPC classification XML parsing experiments

## Architecture

The project follows a data analysis pipeline:

1. **Database Connection**: Connect to PATSTAT using EPO's PatstatClient
2. **Data Extraction**: SQL queries joining multiple PATSTAT tables (TLS201_APPLN, TLS206_PERSON, TLS207_PERS_APPLN, TLS224_APPLN_CPC)
3. **Data Enrichment**: Map NUTS codes to region names and CPC codes to technology titles
4. **Visualization**: Interactive choropleth maps using Pygwalker

### Core Components

- **PatentDataProcessor Class**: Modular Python class encapsulating the entire workflow
- **NUTS Mappings**: Regional code mappings from EUROSTAT data in `mappings/nuts_mapping.csv`
- **IPC/CPC Schemes**: Technology classification mappings from XML files in `mappings/`
- **Output Data**: Processed datasets saved to `output/` directory

## Working with PATSTAT Data

The project connects to EPO's PATSTAT database with environment selection:
- `PatstatClient(env="TEST")` for development with limited dataset
- `PatstatClient(env="PROD")` for full production dataset

Key PATSTAT tables used:
- `TLS201_APPLN` - Application data
- `TLS206_PERSON` - Person/applicant data with NUTS codes
- `TLS207_PERS_APPLN` - Person-application relationships
- `TLS224_APPLN_CPC` - CPC classification codes

## Data Processing Workflow

1. Query German patent applications filtered by NUTS Level 3 regions
2. Group by applicant, region, filing year, and technology field
3. Map NUTS codes to federal state and district names
4. Map CPC subclass codes to technology titles using IPC XML scheme
5. Generate interactive visualizations with geographic mapping

## File Structure

- `mappings/` - External data for enrichment (NUTS codes, IPC schemes, geographic boundaries)
- `output/` - Generated CSV datasets for analysis
- `images/` - Screenshots and presentation materials
- `notebooks/` - Additional analysis notebooks and experiments

## Visualization Configuration

The project uses Pygwalker for interactive data exploration with configuration stored in `pygwalker_config.json`. To create choropleth maps:
- Load NUTS geographic boundaries (GeoJSON from EUROSTAT)
- Configure geographic coordinate system
- Map NUTS_ID to geometry and data fields