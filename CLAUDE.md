# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a cluster headache pain simulation and analysis tool built with Python. The project models cluster headache attacks and pain intensity across different patient populations, comparing them with multiple sclerosis pain data. It features a Streamlit web application for interactive simulation and visualization.

## Development Commands

### Running the Application
```bash
streamlit run Cluster_headache_app.py
```

### Managing Dependencies
```bash
pip install -r requirements.txt
```

### Keeping System Awake (for long simulations)
```bash
python keep_awake_script.py
```

## Architecture

### Core Components

- **`Cluster_headache_app.py`**: Main Streamlit application entry point with UI controls and simulation orchestration
- **`SimulationConfig.py`**: Configuration dataclass containing simulation parameters, population data, and intensity transformation settings
- **`simulation.py`**: Core simulation engine (`Simulation` class) that generates patient populations and runs yearly simulations
- **`models.py`**: Patient and Attack data models with statistical profile generation
- **`stats_utils.py`**: Statistical utilities for generating attack patterns, intensities, and distributions based on clinical literature
- **`visualizer.py`**: Plotly-based visualization system for creating interactive charts and comparisons
- **`figs.py`**: Figure export functionality for research publications

### Data Flow

1. **Configuration**: `SimulationConfig` defines population parameters and intensity transformation methods
2. **Population Generation**: `Simulation` creates patient cohorts (Episodic/Chronic × Treated/Untreated)
3. **Attack Modeling**: Each `Patient` generates attacks using statistical distributions from `stats_utils`
4. **Visualization**: `Visualizer` creates comparative charts showing pain burden across groups
5. **Analysis**: Jupyter notebooks perform sensitivity analysis and prevalence studies

### Key Features

- **Patient Types**: Four cohorts (Episodic Treated/Untreated, Chronic Treated/Untreated)
- **Intensity Transformation**: Multiple methods (linear, piecewise linear, power, exponential) for pain scale conversion
- **Comparative Analysis**: Side-by-side comparison with multiple sclerosis pain data
- **Sensitivity Analysis**: Parameter variation testing via Jupyter notebooks
- **Publication Ready**: Automated figure generation for research papers

### Data Sources

The simulation uses clinical literature data for:
- Attack frequency distributions
- Pain intensity patterns  
- Treatment effectiveness
- Duration statistics
- Population prevalence rates

### File Organization

- **Core Logic**: `.py` files contain the simulation engine
- **Analysis**: `.ipynb` notebooks for sensitivity analysis and prevalence studies
- **Data Output**: `csv/` folder contains sensitivity analysis results
- **Configuration**: `.streamlit/config.toml` for theme settings