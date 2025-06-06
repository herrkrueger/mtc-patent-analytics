# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **comprehensive patent analytics toolkit** designed for patent information professionals, PATLIB staff, and patent office personnel. The repository contains multiple specialized modules for different aspects of patent data analysis, from interactive web applications to Jupyter-based analytical workflows. The toolkit demonstrates various approaches to patent data analysis using EPO data sources and modern visualization techniques.

## Key Technologies and Dependencies

### Python/Jupyter Stack
- **Python 3.8+** with Jupyter notebooks for interactive analysis
- **EPO Technology Intelligence Platform** via `epo.tipdata.patstat` client
- **PATSTAT Database** for patent data queries
- **SQLAlchemy ORM** for database interactions
- **Pandas** for data manipulation and analysis
- **Pygwalker** for Tableau-like interactive visualizations
- **lxml** for XML parsing of IPC/CPC classification schemes
- **GeoPandas** for geographical data handling
- **Matplotlib/Plotly** for visualization
- **EPO OPS API** for real-time patent data access

### Web Application Stack
- **SvelteKit 5.x** with modern runes syntax
- **TypeScript** for type safety
- **D3.js 7.x** for advanced data visualizations
- **Tailwind CSS** for responsive styling
- **Node.js 18+** and npm/pnpm for package management

## Repository Structure and Entry Points

### `/deeptechfinder/`
- German university patent data analysis from EPO Deep Tech Finder
- Entry: `DE Universities from DTF.ipynb`

### `/familytree/`
- Patent family visualization tools (Credit: Anonymous EPO Examiner)
- Entry: `Divitree.ipynb`
- Core modules: `patent_analysis/` directory

### `/funwithipc/`
- Interactive IPC exploration tools
- Entry: `ipcbrowser.ipynb`

### `/ipc-ops/`
- EPO OPS API integration for IPC querying
- Entry: `ipc_query_interactive_tutorial.ipynb`
- Core modules: `auth.py`, `ipc_query.py`

### `/ipc-patstat/`
- PATSTAT-based IPC subclass analysis
- Entry: `IPC_Subclass_Analysis.ipynb`

### `/ipc-tree-explorer/`
- **SvelteKit web application** for interactive IPC/CPC visualization (Credit: Matze)
- Entry: `src/routes/+page.svelte`
- Multiple visualization modes: radial tree, Sankey, circle packing
- Run with: `npm run dev` or `pnpm dev`

### `/regionalmappings/`
- German patent distribution analysis (EPO Patent Knowledge Forum 2024)
- Primary entries: `epo_pkf2024_piznet_final.ipynb`, `patentknowledgeforum2024.ipynb`
- Detailed tutorial: `notebooks/patstat_nuts_de_with_explanations.ipynb`

### `/training/`
- Comprehensive educational materials (Credit: EPO and WIPO)
- **PATSTAT training**: `patstat/` and `patstat in depth/`
- **Handbook**: `handbook-master/` - Complete patent analytics guide
- **EPAB**: `epab/` - EPO Analytics Bootcamp materials

## Architecture Overview

The toolkit follows multiple architectural patterns depending on the module:

### Python/Jupyter Workflows
1. **Database Connection**: Connect to PATSTAT or EPO OPS APIs
2. **Data Extraction**: SQL queries or API calls for patent data
3. **Data Processing**: Clean, transform, and enrich patent data
4. **Analysis & Visualization**: Interactive notebooks with various visualization libraries

### Web Application Architecture (ipc-tree-explorer)
1. **SvelteKit Frontend**: Component-based reactive UI
2. **D3.js Visualizations**: Professional data visualization engine
3. **Static Data Loading**: JSON-based IPC/CPC classification data
4. **Performance Optimization**: Progressive rendering for large datasets

### Core Components Across Modules

- **Patent Family Processing**: `familytree/patent_analysis/` modules
- **PATSTAT Integration**: Multiple entry points across training and analysis modules
- **OPS API Integration**: `ipc-ops/auth.py` and `ipc_query.py`
- **Classification Data**: IPC/CPC schemes in XML and JSON formats
- **Geographic Mappings**: NUTS regional data for geographic analysis
- **Interactive Visualizations**: Pygwalker, D3.js, and custom visualization components

## Working with Patent Data Sources

### PATSTAT Database Integration
The toolkit connects to EPO's PATSTAT database with environment selection:
- `PatstatClient(env="TEST")` for development with limited dataset
- `PatstatClient(env="PROD")` for full production dataset

Key PATSTAT tables used across modules:
- `TLS201_APPLN` - Application data
- `TLS206_PERSON` - Person/applicant data with NUTS codes
- `TLS207_PERS_APPLN` - Person-application relationships
- `TLS224_APPLN_CPC` - CPC classification codes
- Full table documentation available in `training/patstat in depth/`

### EPO OPS API Integration
- Authentication via `ipc-ops/auth.py`
- IPC querying via `ipc-ops/ipc_query.py`
- Interactive tutorials in `ipc-ops/ipc_query_interactive_tutorial.ipynb`

### Deep Tech Finder Data
- CSV exports from EPO Deep Tech Finder
- University patent portfolio analysis
- Located in `deeptechfinder/`

## Common Data Processing Workflows

### Regional Patent Analysis (regionalmappings/)
1. Query German patent applications filtered by NUTS Level 3 regions
2. Group by applicant, region, filing year, and technology field
3. Map NUTS codes to federal state and district names
4. Map CPC subclass codes to technology titles using IPC XML scheme
5. Generate interactive visualizations with geographic mapping

### Patent Family Analysis (familytree/)
1. Extract patent family relationships from PATSTAT
2. Build family tree structures using custom algorithms
3. Generate interactive family visualizations
4. Export tree diagrams and family statistics

### Classification Analysis (ipc-*/ directories)
1. Parse IPC/CPC classification schemes from XML/JSON
2. Build hierarchical classification trees
3. Create interactive classification browsers
4. Generate classification statistics and trends

### University Patent Analysis (deeptechfinder/)
1. Import CSV data from EPO Deep Tech Finder
2. Analyze university patent portfolios
3. Create comparative visualizations
4. Generate university ranking reports

## Key File Locations by Module

### Regional Mappings (`regionalmappings/`)
- `mappings/` - External data for enrichment (NUTS codes, IPC schemes, geographic boundaries)
- `output/` - Generated CSV datasets for analysis
- `images/` - Screenshots and presentation materials
- `notebooks/` - Additional analysis notebooks and experiments

### IPC Tree Explorer (`ipc-tree-explorer/`)
- `src/routes/` - SvelteKit page components
- `src/component/` - Reusable UI components
- `static/ipccpc/` - IPC/CPC classification data in JSON format
- `package.json` - Node.js dependencies and scripts

### Family Tree (`familytree/`)
- `patent_analysis/` - Core Python modules for family processing
- `images/` - Example family tree visualizations
- `Divitree.ipynb` - Main analysis notebook

### Training Materials (`training/`)
- `patstat/` - Basic PATSTAT training notebooks
- `patstat in depth/` - Comprehensive table-by-table documentation
- `handbook-master/` - Complete R/Python patent analytics handbook
- `epab/` - EPO Analytics Bootcamp materials

## Visualization Configuration

### Pygwalker Configuration (regionalmappings/)
The regional analysis uses Pygwalker for interactive data exploration with configuration stored in `pygwalker_config.json`. To create choropleth maps:
- Load NUTS geographic boundaries (GeoJSON from EUROSTAT)
- Configure geographic coordinate system
- Map NUTS_ID to geometry and data fields

### D3.js Configuration (ipc-tree-explorer/)
The web application uses D3.js with custom configurations:
- Radial tree layouts with intelligent spacing algorithms
- Sankey flow diagrams for classification relationships
- Circle packing for hierarchical data representation
- Performance optimizations for large datasets (15,000+ nodes)

### Interactive Notebook Visualizations
- **Matplotlib/Plotly**: Standard scientific plotting across modules
- **Family tree diagrams**: Custom visualization in familytree module
- **Classification browsers**: Interactive widgets in IPC analysis notebooks

## Development Guidelines

### For Python/Jupyter Development
- Use virtual environments for dependency management
- Follow existing code patterns in each module
- Test with PATSTAT TEST environment before PROD
- Document new analysis workflows in notebooks

### For Web Application Development (ipc-tree-explorer/)
- Use TypeScript for new components
- Follow SvelteKit 5.x patterns with runes syntax
- Optimize for performance with large datasets
- Maintain responsive design for mobile compatibility

### For Training Materials
- Keep educational content separate from analysis code
- Document data sources and methodology clearly
- Provide step-by-step explanations for complex workflows
- Include practical exercises where appropriate