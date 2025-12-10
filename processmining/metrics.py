import pandas as pd

def compute(df: pd.DataFrame):
    df = df.copy()

    df["ProcessTime"] = df["EndTime"] - df["StartTime"]
    produced_parts = df["ID"].nunique()

    # Running times & average cycle time
    running = df[df["ReasonCode"].isin(["Working", "Warning"])]
    running_sec = running.groupby("MachineName")["ProcessTime"].sum().dt.total_seconds()
    avg_time_per_part = (running_sec/produced_parts).rename("Avg_Time_per_part_s")

    # Availability
    grouped = (df.groupby(["MachineName", "ReasonCode"])["ProcessTime"].sum().unstack(fill_value=pd.Timedelta(0)))
    # convert timedeltas to seconds
    for col in grouped.columns:
        grouped[col] = grouped[col].dt.total_seconds()

    available = grouped.get("Working", 0) + grouped.get("Idle", 0) + grouped.get("Warning", 0)
    grouped["Availability_%"] = available / grouped.sum(axis=1) * 100
    availability_pct = grouped["Availability_%"]

    # MTTR
    stopped = df[df["ReasonCode"] == "Stopped"]
    mttr = (stopped.groupby("MachineName")["ProcessTime"].mean().dt.total_seconds().reindex(grouped.index)).rename("MTTR_s")

    # if a machine never stopped but is 100% available, assign an MTTR of 1 s
    mttr[mttr.isna() & (availability_pct == 100)] = 1.0

    # Energy rates (kJ per second)
    keep = df[df["ReasonCode"].isin(["Working", "Idle", "Idle for Deviation", "Warning"])].copy()
    keep["Category"] = keep["ReasonCode"].map(lambda x: "EnergyWorking" if x in ("Working", "Warning") else "EnergyIdling")
    energy = (keep.groupby(["MachineName", "Category"]).agg({"EnergyConsumption": "sum", "ProcessTime": "sum"}))
    energy["s"] = energy["ProcessTime"].dt.total_seconds()
    energy["kJ_per_s"] = energy["EnergyConsumption"] / energy["s"]
    energy = energy["kJ_per_s"].unstack(fill_value=0)

    # Merge & round
    final = (pd.concat([avg_time_per_part, grouped["Availability_%"], mttr, energy], axis=1).reset_index().rename(columns={"index": "MachineName"}))

    # round all numeric columns to two decimal places
    numeric_cols = final.select_dtypes(include="number").columns
    final[numeric_cols] = final[numeric_cols].round(2)
    return final