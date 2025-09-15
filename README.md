# Cluster Headache Pain Simulation

A research tool for modeling and analyzing cluster headache pain patterns across different patient populations, with comparative analysis against multiple sclerosis pain data.

**🚀 [Try the live app here](https://ch-burden.streamlit.app/)**

## Overview

This project simulates cluster headache attacks and pain intensity for various patient cohorts, providing insights into pain burden differences between treated/untreated and episodic/chronic cases. The simulation is based on clinical literature data and includes an interactive Streamlit web application for exploration and analysis.

## Features

- **Patient Population Modeling**: Four distinct cohorts (Episodic Treated/Untreated, Chronic Treated/Untreated)
- **Statistical Attack Generation**: Evidence-based attack frequency, duration, and intensity patterns
- **Pain Scale Transformation**: Multiple methods for intensity scale conversion (linear, piecewise linear, power, exponential)
- **Comparative Analysis**: Side-by-side comparison with multiple sclerosis pain data
- **Interactive Visualization**: Real-time parameter adjustment and results visualization
- **Sensitivity Analysis**: Parameter variation testing via Jupyter notebooks
- **Publication-Ready Figures**: Automated chart generation for research papers

## Installation

1. Clone the repository:
```bash
git clone https://github.com/aph-research/cluster-headache.git
cd cluster-headache
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Interactive Application

Launch the Streamlit web application:

```bash
streamlit run Cluster_headache_app.py
```

This opens an interactive interface where you can:
- Adjust population parameters (prevalence, treatment rates, chronic fraction)
- Select intensity transformation methods
- View real-time simulation results and visualizations
- Compare cluster headache pain burden with multiple sclerosis data

### Analysis Notebooks

The project includes Jupyter notebooks for detailed analysis:

- `ch_prevalence.ipynb`: Prevalence studies and population estimates
- `sensitivity_analyzer.ipynb`: Parameter sensitivity analysis and uncertainty quantification

### Long-Running Simulations

For extended simulations, use the keep-awake script to prevent system sleep:

```bash
python keep_awake_script.py
```

## Project Structure

- **`Cluster_headache_app.py`**: Main Streamlit application
- **`SimulationConfig.py`**: Configuration parameters and settings
- **`simulation.py`**: Core simulation engine
- **`models.py`**: Patient and attack data models
- **`stats_utils.py`**: Statistical distributions and utilities
- **`visualizer.py`**: Plotly-based visualization system
- **`figs.py`**: Figure export for publications
- **`csv/`**: Sensitivity analysis results
- **Notebooks**: Detailed analysis and parameter studies

## Methodology

The simulation uses clinical literature data to model:

- **Attack Frequency**: Based on multiple epidemiological studies
- **Pain Intensity**: Treatment-specific intensity distributions
- **Attack Duration**: Chronic vs. episodic duration patterns
- **Population Prevalence**: Global adult population estimates
- **Treatment Effects**: Evidence-based treatment efficacy data

## Key Parameters

- **Annual Prevalence**: 26-95 per 100,000 adults (default: 53)
- **Chronic Fraction**: 0-100% (default: 20%)
- **Treatment Rate**: 0-100% (default: 43%)
- **Population Simulation**: 0.01-0.1% of worldwide cases (default: 0.02%)

## Research Applications

This tool supports research in:
- Cluster headache burden quantification
- Treatment impact assessment
- Healthcare resource planning
- Comparative pain studies
- Clinical trial design

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## License

This project is part of ongoing research. Please contact the authors for usage permissions and citations.

## Contact

For questions about the research or methodology, please open an issue on this repository.