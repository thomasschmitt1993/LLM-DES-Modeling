import os
from helpers.runner import run_python_code
import re
import matplotlib.pyplot as plt
import numpy as np

def save_model(model_content, save_path, filename):
    full_path = os.path.join(save_path, filename)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(model_content)
    print(f"Model saved to {full_path}")
    return full_path

def retrieve_KPIs(code, modelinfo: str):
    original_output = run_python_code(code).splitlines()
    kpi_section = [f"----Results from model: {modelinfo}"]
    bottleneck_section = []
    in_bottleneck_block = False
    for line in original_output:
        if "=== Bottleneck Frequency over runs ===" in line:
            in_bottleneck_block = True
            bottleneck_section.append(line)
            continue
        if in_bottleneck_block:
            bottleneck_section.append(line)
            continue
        kpi_section.append(line)
    return kpi_section, bottleneck_section

def remove_code_wrappers(code):
    code = code.strip()
    if code.startswith("```python"):
        code = code[len("```python"):].strip()
    if code.endswith("```"):
        code = code[:-3].strip()
    return code

def visualize_results(results, save_path: str | None = None):
    # ---------- regex patterns ----------
    _RE_NAME   = re.compile(r'^----Results from model:\s*(.*)')
    _RE_TP     = re.compile(r'^Throughput\s*=\s*([\d.]+)')
    _RE_WIP    = re.compile(r'^WIP\s*=\s*([\d.]+)')
    _RE_ENERGY = re.compile(r'^Mean Energy Consumption per Part\s*=\s*([\d.]+)')

    def _extract_kpis(block):
        """Return (model_name, throughput, WIP, energy) from one text block."""
        name = tp = wip = energy = None
        for line in block:
            if (m := _RE_NAME.match(line)):
                name = m.group(1)
            elif (m := _RE_TP.match(line)):
                tp = float(m.group(1))
            elif (m := _RE_WIP.match(line)):
                wip = float(m.group(1))
            elif (m := _RE_ENERGY.match(line)):
                energy = float(m.group(1))
        if None in (name, tp, wip, energy):
            raise ValueError(f"Incomplete KPI set in block:\n{block}")
        return name, tp, wip, energy

    def _visualize_values_and_changes(blocks,
                                      *,
                                      baseline_index: int = 0,
                                      annotate: bool = True,
                                      figsize_per_bar: float = 1.6,
                                      font_size: int = 9,
                                      arrow: bool = True):
        # ----- extract KPIs --------------------------------------------------------
        names, tp, wip, en = zip(*(_extract_kpis(b) for b in blocks))
        tp = np.array(tp, dtype=float)
        wip = np.array(wip, dtype=float)
        en = np.array(en, dtype=float)

        n_models = len(names)
        width = max(6, n_models * figsize_per_bar)

        # ----- single figure with grouped bars ------------------------------------
        fig, ax = plt.subplots(figsize=(width, 7))

        x = np.arange(n_models)   # model positions
        bar_width = 0.25

        # positions for each KPI
        x_tp = x - bar_width
        x_wip = x
        x_en = x + bar_width

        # new colours + legend wording
        bars_tp = ax.bar(
            x_tp, tp,
            width=bar_width,
            label="TH (parts/hour)",
            color="#1F77B4"    # blue
        )
        bars_wip = ax.bar(
            x_wip, wip,
            width=bar_width,
            label="WIP (parts)",
            color="#2B7A0B"    # dark green
        )
        bars_en = ax.bar(
            x_en, en,
            width=bar_width,
            label="SEC (kWh/part)",
            color="#F28E2B"    # dark orange
        )

        # ----- annotation helper ---------------------------------------------------
        def annotate_group(bars, values, title):
            base = values[baseline_index]
            abs_delta = values - base
            pct_delta = abs_delta / base * 100.0

            for idx, (bar, val, d, p) in enumerate(zip(bars, values, abs_delta, pct_delta)):
                x_pos = bar.get_x() + bar.get_width() / 2
                y_pos = bar.get_height()

                if d > 0:
                    sign_arrow = "▲"
                elif d < 0:
                    sign_arrow = "▼"
                else:
                    sign_arrow = "-"

                # colour logic: green good, red bad, neutral for no change
                if title.startswith("TH"):  # higher TH is better
                    if d > 0:
                        colour = "#3cab5c"      # green
                    elif d < 0:
                        colour = "#c94c4c"      # red
                    else:
                        colour = "#2F4F4F"      # neutral dark slate for no change
                else:  # WIP or SEC: lower is better
                    if d > 0:
                        colour = "#c94c4c"      # red
                    elif d < 0:
                        colour = "#3cab5c"      # green
                    else:
                        colour = "#2F4F4F"      # neutral dark slate for no change

                # baseline model: only value
                if idx == baseline_index:
                    label = f"{val:.2f}"
                else:
                    # value, Δ, and % each on their own line
                    label = (
                        f"{val:.2f}\n"                        # value
                        f"{sign_arrow if arrow else ''}{d:+.2f}\n"  # delta
                        f"({p:+.1f}%)"                       # percentage
                    )

                ax.text(
                    x_pos, y_pos, label,
                    ha="center", va="bottom",
                    fontsize=font_size,
                    color=colour,
                    fontweight="bold",
                    linespacing=1.3
                )

        # ----- annotations & styling ----------------------------------------------
        if annotate:
            # headroom for labels
            max_val = max(tp.max(), wip.max(), en.max())
            ax.set_ylim(top=max_val * 1.25)

            annotate_group(bars_tp, tp,  "TH (parts/hour)")
            annotate_group(bars_wip, wip, "WIP (parts)")
            annotate_group(bars_en, en,  "SEC (kWh/part)")

        ax.set_title("KPIs per model – values and Δ vs baseline")
        ax.set_ylabel("Value")
        ax.set_xlabel("Model version")

        ax.set_xticks(x)
        ax.set_xticklabels(names)
        ax.tick_params(axis="x", rotation=45)
        for lbl in ax.get_xticklabels():
            lbl.set_ha("right")

        ax.legend()
        ax.margins(x=0.05)
        fig.tight_layout()

        return fig

    # create figure
    fig = _visualize_values_and_changes(results)

    # save if a path is provided
    if save_path is not None:
        full_path = os.path.join(save_path, "model_comparison_kpis.png")
        fig.savefig(full_path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        print(f"\nFigure saved to {full_path}")

    return fig