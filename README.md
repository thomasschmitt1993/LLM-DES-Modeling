# LLM-DES-Modeling

Code and resources for automating discrete-event simulation (DES) modeling with large language models (LLMs), including:
- event log preprocessing and process mining
- LLM-assisted DES model generation
- KPI extraction and model comparison
- bottleneck-informed adaptation workflows

This repository accompanies a published study in the *Journal of Manufacturing Systems*.

## Repository structure

- `main.py`: end-to-end workflow entry point
- `agents/`: LLM agents for model building, optimization, adaptation, evaluation, and visualization
- `processmining/`: event log loading, preprocessing, and metric computation
- `helpers/`: execution and visualization helper utilities
- `blueprint/`: DES blueprint model(s)
- `data/`: input event log(s)
- `results/`: generated models and figures

## Requirements

- Python 3.10 or newer (3.11 recommended)
- Node.js 18+ (required for Mermaid rendering via `npx`)
- OpenAI API key

Python dependencies are listed in `requirements.txt`.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Mermaid CLI is invoked through `npx` at runtime, so a separate global install is not required if Node.js is installed.

## Configuration

Set your OpenAI API key:

```bash
export OPENAI_API_KEY="your_key_here"
```

`main.py` reads this variable at runtime and exits with an explicit error if it is missing.

## Input data contract

The main pipeline expects a CSV event log (default: `data/workingtest.csv`) with at least the following columns:

| Column | Type | Description |
|---|---|---|
| `ID` | string/int | Case or part identifier |
| `MachineName` | string | Activity/resource name |
| `StartTime` | datetime | Activity start timestamp |
| `EndTime` | datetime | Activity end timestamp |
| `ReasonCode` | string | Machine state label (for example `Working`, `Idle`, `Warning`, `Stopped`) |
| `EnergyConsumption` | float | Energy consumed in the event window |

Notes:
- `StartTime` and `EndTime` are parsed with `pandas.to_datetime`.
- `EndTime` ties are disambiguated per `ID`.

## Run

```bash
python main.py
```

The workflow is interactive and may prompt for:
- manual edits to generated model code
- optional human-provided adaptation instruction

## Outputs

Main artifacts are written to `results/`, including:
- `initial_model.py`: first generated DES model
- `model_visualization.mmd`: Mermaid source graph
- `model_visualization.png`: rendered flow chart
- `model_comparison_kpis.png`: KPI comparison chart across model variants

## Reproducibility notes

- LLM-generated outputs are probabilistic; exact generated code can vary by run and model version.
- For publication workflows, archive:
  - input data files
  - exact dependency versions
  - prompts/manual constraints used in each run
  - generated model scripts and output figures

## License

This project is licensed under GNU GPL v3.0. See `LICENSE` for full terms.

## Dataset license

Dataset files in `data/` are licensed separately from code. See `DATA_LICENSE.md` for terms and provenance notes.

## Citation

If you use this repository in academic work, please cite:
- the associated journal article: DOI `10.1016/j.jmsy.2026.02.015`
  URL: `https://www.sciencedirect.com/science/article/pii/S0278612526000427`
- this code repository (persistent URL): `https://github.com/thomasschmitt1993/LLM-DES-Modeling`

Machine-readable citation metadata is provided in `CITATION.cff`.

For dataset reuse terms and provenance, see `DATA_LICENSE.md`.
