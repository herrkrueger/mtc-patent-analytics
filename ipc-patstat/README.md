# PATSTAT IPC Subclass Analysis

This directory contains tools for comprehensive analysis of patent counts across all ~646 IPC (International Patent Classification) subclasses using the PATSTAT database.

## 🎯 Purpose

Overcome the 10,000 result limitation of the EPO OPS API by accessing the complete PATSTAT database directly to get accurate patent counts for all IPC subclasses.

## 📊 What This Analysis Provides

- **Complete IPC Coverage**: Analysis of all ~646 IPC subclasses (4-character codes like A61K, H01L, etc.)
- **Detailed Statistics**: Total patents, granted patents, unique families, grant rates, and citation averages
- **Historical Data**: Filing year ranges and time span analysis
- **Section Breakdown**: Aggregated statistics by the 8 main IPC sections (A-H)
- **Export Capabilities**: CSV outputs for further analysis
- **Visualizations**: Charts and graphs for data exploration

## 🚀 Quick Start

### Prerequisites

1. **PATSTAT Access**: Ensure you have access to EPO TIP Data PATSTAT environment
2. **Python Environment**: Required packages should be available in the TIP environment

### Usage

1. Open the Jupyter notebook:
   ```
   IPC_Subclass_Analysis.ipynb
   ```

2. **Environment Selection**:
   - Use `'TEST'` for quick testing (limited dataset, ~10K publications)
   - Use `'PROD'` for complete analysis (full dataset, 140M+ publications)

3. **Run the Analysis**:
   - Execute cells sequentially
   - The main query may take several minutes in PROD environment
   - Results will be displayed and exported automatically

## 📁 Files

- **`IPC_Subclass_Analysis.ipynb`** - Main analysis notebook
- **`README.md`** - This documentation file

## 🔍 Key Features

### 1. Comprehensive Database Query
```python
# Main query structure
comprehensive_query = db.query(
    func.substr(TLS209_APPLN_IPC.ipc_class_symbol, 1, 4).label('ipc_subclass'),
    func.count(TLS201_APPLN.appln_id).label('total_patents'),
    func.sum(func.case([(TLS201_APPLN.granted == 'Y', 1)], else_=0)).label('granted_patents'),
    func.count(func.distinct(TLS201_APPLN.docdb_family_id)).label('unique_families'),
    # ... additional metrics
)
```

### 2. Data Processing
- IPC section mapping (A=Human Necessities, B=Performing Operations, etc.)
- Grant rate calculations
- Time span analysis
- Citation statistics

### 3. Multiple Output Formats
- Interactive notebook display
- CSV exports (detailed, summary, section-level)
- Visualization charts
- Statistical summaries

## 📊 Expected Results

Based on PATSTAT data structure, you can expect:

- **~646 IPC subclasses** covering all technology areas
- **Millions of patents** across all classifications
- **Detailed breakdowns** by IPC section showing technology focus areas
- **Grant rates** varying by technology field
- **Historical coverage** spanning decades of patent data

## 🔧 Technical Details

### Database Tables Used
- **TLS209_APPLN_IPC**: IPC classification assignments
- **TLS201_APPLN**: Application details and metadata

### Key Filters Applied
- `appln_id < 900000000`: Excludes artificial applications
- `ipc_class_level == 'A'`: Uses full IPC classifications
- `length(ipc_subclass) == 4`: Ensures valid subclass format

### Performance Considerations
- TEST environment: Fast execution, limited data
- PROD environment: Complete data, longer execution time
- Results are cached and can be exported for reuse

## 🆚 Comparison with OPS API

| Feature | OPS API | PATSTAT Direct |
|---------|---------|----------------|
| Result Limit | 10,000 max | Complete dataset |
| Speed | Fast (seconds) | Slower (minutes) |
| Data Coverage | Recent/published | Complete historical |
| Use Case | Real-time queries | Comprehensive analysis |
| Access | Public API | TIP environment only |

## 🎯 Use Cases

1. **Technology Landscape Analysis**: Identify active vs. niche technology areas
2. **Patent Strategy**: Understand filing patterns and grant rates by technology
3. **Research Planning**: Find less crowded IPC areas for innovation
4. **Competitive Intelligence**: Analyze technology focus areas
5. **Academic Research**: Comprehensive patent statistics for studies

## 🔄 Next Steps

The notebook provides templates for extending the analysis:

- **Temporal trends**: Track IPC activity over time
- **Authority analysis**: Compare filing patterns by patent office
- **Citation analysis**: Identify high-impact technology areas
- **Applicant mapping**: Connect IPC data to company strategies

## 💡 Tips

1. **Start with TEST**: Use TEST environment to familiarize yourself with the analysis
2. **Filter by Date**: Add temporal filters for focused analysis
3. **Export Results**: Save CSV files for use in external tools
4. **Compare Sections**: Use section-level analysis to identify trends
5. **Validate Results**: Cross-check with known patent statistics

## 🆘 Troubleshooting

- **Connection Issues**: Verify PATSTAT environment access
- **Long Execution Times**: Normal for PROD environment; consider date filtering
- **Memory Issues**: Use TEST environment or add result limits
- **Missing Results**: Check filter conditions and database connectivity

This analysis provides the most comprehensive view of IPC subclass patent distribution available, overcoming the limitations of public APIs and giving you complete access to patent landscape statistics.