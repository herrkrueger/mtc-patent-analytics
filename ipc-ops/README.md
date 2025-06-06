# EPO OPS IPC Query Tool

A user-friendly tool for Patent Information Experts to search patents by IPC classification using the EPO Open Patent Services (OPS) API.

## 🚀 Quick Start - For Non-Programmers

**Recommended: Use the Interactive Jupyter Notebook**

The easiest way to use this tool is through the **interactive Jupyter notebook**:
- Open `ipc_query_interactive_tutorial.ipynb`
- Follow the step-by-step guided tutorial
- No programming knowledge required - just run the cells and follow instructions
- Interactive interface with clear explanations

## What This Tool Does

- **Search patents by IPC class** (e.g., `A61K*` for pharmaceuticals)
- **Get instant results**: Total number of patents found
- **View sample patents**: First 10 patent numbers from your search
- **Fast response times**: See how quickly the EPO API responds
- **Professional authentication**: Secure OAuth connection to EPO OPS API

## Prerequisites

1. **EPO OPS API Credentials**
   - Register at: https://developers.epo.org/user/register
   - Get your OPS_KEY and OPS_SECRET
   - Add them to a `.env` file in this directory

2. **Python Environment** (if not using Jupyter)
   - Python 3.10 or higher
   - Install required packages: `pip install python-dotenv requests python-epo-ops-client`

## How to Use

### Option 1: Interactive Jupyter Notebook (Recommended)
1. Open `ipc_query_interactive_tutorial.ipynb`
2. Run each cell step by step
3. Follow the guided tutorial with explanations

### Option 2: Command Line (Advanced Users)
1. Run `python ipc_query.py`
2. Enter an IPC code when prompted (e.g., `A61K*`)
3. View results

## Example Output
```
Authentifizierung erfolgreich
Sende Anfrage für IPC: IC=A61K*
Treffer insgesamt: 1,234
Antwortzeit: 1.73 Sekunden

Erste Treffer (max. 10):
 • EP1234567
 • EP2345678
 • EP3356789
 • EP2345678
 • EP3451789
```

## IPC Code Examples for Patent Professionals

- `A61K*` - Pharmaceuticals, medicinal preparations
- `H04L*` - Transmission of digital information
- `G06F*` - Electric digital data processing
- `C07D*` - Heterocyclic compounds (organic chemistry)
- `B60L*` - Electric propulsion of vehicles

## Files Overview

- **`ipc_query_interactive_tutorial.ipynb`** - Interactive tutorial notebook (START HERE!)
- **`ipc_query.py`** - Main search script
- **`auth.py`** - Handles EPO API authentication
- **`.env`** - Your API credentials (create this file)

## Important Notes

- The EPO OPS API returns maximum 10,000 results per query to prevent server overload
- Response times vary based on query complexity and server load
- Large result sets may take longer to process

## Support

For Patent Information Experts: The interactive Jupyter notebook provides the most user-friendly experience with detailed explanations of each step.