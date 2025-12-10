from pathlib import Path
import pandas as pd
import pm4py

def load(path: Path):
    return pd.read_csv(path)

def preprocess(df: pd.DataFrame):
    for col in ("StartTime", "EndTime"):
        df[col] = pd.to_datetime(df[col])
    df = df.sort_values("EndTime")
    # Fix identical timestamps
    df["EndTime"] += pd.to_timedelta(
        df.groupby(["ID", "EndTime"]).cumcount(), unit="s")
    return df

def to_sequence_text(df: pd.DataFrame):
    #Return the follows / parallel text block.
    event_log = pm4py.format_dataframe(
        df, case_id="ID", activity_key="MachineName", timestamp_key="EndTime")
    from pm4py.algo.discovery.footprints import algorithm as fp
    fp_net = fp.apply(event_log)

    lines = ["Directly-follows relationships:"]
    lines += [f"{a} -> {b}" for a, b in fp_net["sequence"]]

    # drop pairs where the two activities are identical
    cleaned_parallel = [(a, b) for a, b in fp_net["parallel"] if a != b]

    lines += ["", "Parallel relationships:"]
    lines += [f"{a} || {b}" for a, b in cleaned_parallel]
    return "\n".join(lines)