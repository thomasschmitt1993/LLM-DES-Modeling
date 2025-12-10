import os
from matplotlib import pyplot as plt
from openai import OpenAI
from processmining import eventlog, metrics
from agents.builder import ModelBuilder
from agents.optimizer import Modeloptimizer
from agents.adapter import Modeladaptor
from agents.evaluator import Evaluater
from agents.cpdagent import CPD
from agents.visualizer import Modelvisualizer
from helpers.other_helpers import save_model, remove_code_wrappers, retrieve_KPIs, visualize_results
from helpers.mermaid_renderer import render_mermaid_to_png
import pandas as pd
import time


api_key=""  #Your OpenAI API key here
client = OpenAI(api_key=api_key)
file_path_eventlog = r"/Users/thomas/Library/CloudStorage/OneDrive-ScaniaCV/workspace/1. Projects/Simulations using GenAI/Thomas/Case B - Thomas (revised)/workingtest.csv"
file_path_machine = r"/Users/thomas/Library/CloudStorage/OneDrive-ScaniaCV/workspace/1. Projects/Simulations using GenAI/Thomas/Case B - Thomas (revised)/workingtest.csv"
file_path_blueprintmodel_active = r"/Users/thomas/Library/CloudStorage/OneDrive-ScaniaCV/workspace/1. Projects/Simulations using GenAI/Thomas/Case B - Thomas (revised)/blueprints/blueprint active.py"
file_path_blueprintmodel_util = r"/Users/thomas/Library/CloudStorage/OneDrive-ScaniaCV/workspace/1. Projects/Simulations using GenAI/Thomas/Case B - Thomas (revised)/blueprints/blueprint utilization.py"
final_path = r"/Users/thomas/Library/CloudStorage/OneDrive-ScaniaCV/workspace/1. Projects/Simulations using GenAI/Thomas/Case B - Thomas (revised)/results_13"
buffers_info_specific = "PostLoadingBuffer(Capacity = 2, processtime = 10), PostConveyorBuffer(Capacity = 2, processtime = 10), PostWashingBuffer(Capacity = 2, processtime = 10), PrePress1Buffer(Capacity = 3, processtime = 32), PrePress2Buffer(Capacity = 3, processtime = 32), " \
"PostPress1&Press2Buffer(Capacity = 3, processtime = 32)"
defect_info = "Defect rate = 0.089, defect sink = defect,initiated at Qualitystation"
cpd_info ="1. The presses need to have a processtime of at least 60s. 2. All buffer capacities musst be kept at the same original level. "

def main() -> None:
    df_raw = eventlog.load(file_path_eventlog)
    df_clean = eventlog.preprocess(df_raw)
    stations_md = metrics.compute(df_clean).to_string(index=False)
    sequence_text = eventlog.to_sequence_text(df_clean)
    print(stations_md)
    print("")
    print(sequence_text)

    # read-in the blueprint
    manual_bottleneck = input("Do you want to work with the utilization for bottleneck analysis (type 1) or the active period (type 2)? Enter 1 or 2 ").strip().lower()
    if manual_bottleneck == '1':
        with open(file_path_blueprintmodel_util, "r", encoding="utf-8") as f:
            blueprint_code = f.read()
    elif manual_bottleneck == '2':
        with open(file_path_blueprintmodel_active, "r", encoding="utf-8") as f:
            blueprint_code = f.read()
    else:
        raise IndexError

    # Build initial model
    builder = ModelBuilder(client)
    model_code = builder.build(
        blueprint_code=blueprint_code,
        stations_table_md=stations_md,
        sequence_text=sequence_text,
        buffers=buffers_info_specific,  
        defects=defect_info,  
        manual_note="Production stops from friday 17.00 till saturday 07:00 and from saturday 17:00 till sunday 07:00.")

    clean_initial_model = remove_code_wrappers(model_code)
    save_model(clean_initial_model,final_path, "initial_model.py")
    init_model_path = os.path.join(final_path,"initial_model.py" )

    # Manual adaptation
    manual = input("Do you want to manually edit the initial model before proceeding? (y/n): ").strip().lower()
    if manual == 'y':
        print(f" Please open and edit:\n  {init_model_path}\n When you're done, save it and press Enter.")
        input()  # wait for user confirmation
        # reload their edits
        with open(init_model_path, 'r', encoding='utf-8') as f:
            clean_initial_model = f.read()
        print("Loaded your manually adapted model.")

    # Visualize initial model into flow chart
    visualizer = Modelvisualizer(client)
    mermaid_code = visualizer.visualize_agent(clean_initial_model)
    mmd_path = final_path + "/model_visualization.mmd"
    png_path = final_path + "/model_visualization.png"
    with open(mmd_path, "w", encoding="utf-8") as f:
        f.write(mermaid_code)
    render_mermaid_to_png(mmd_path, png_path)
    print(f"Flow chart saved to: {png_path}")

    kpi_original, bottleneck_original = retrieve_KPIs(clean_initial_model, "Original model")
    results = []
    results.append(kpi_original)
    print(kpi_original)
    print(bottleneck_original)

    optimizer = Modeloptimizer(client)
    suggestions = optimizer.optimize(
        model_code = clean_initial_model,
        bottlenecks= bottleneck_original
    )

    print(suggestions)

    if isinstance(suggestions, dict):
        step_list = suggestions.get("instructions", [])
    elif isinstance(suggestions, list):
        step_list = suggestions
    else:
        raise ValueError("Unexpected format from agent_bottleneck")
    
    human_input = input("Do you want to manually add one change to the model? If yes please answer with the change (leave blank to skip): ").strip().lower()
    if human_input:
        print("Added human input.")
        step_list.append(human_input)
    
    cpdexpert = CPD(client)
    print(cpdexpert.evaluatecpd(step_list, cpd_info))
    
    for idx, step in enumerate(step_list, start=1):
        adaptor = Modeladaptor(client)
        kpi_adapted_model, bottleneck_adapted_model = adaptor.adapter(original_code = clean_initial_model, instruction=step, final_path=final_path, multi_agent_setting= False, index_model= idx)
        print(kpi_adapted_model) # Append each adapted model's KPIs to results
        results.append(kpi_adapted_model)

    #print(results)
    # Evaluate all results
    evaluator = Evaluater(client)
    print(evaluator.evaluate(results))

    visualize_results(results, save_path=final_path)
    plt.show()

if __name__ == "__main__":
    start = time.time()
    main()
    end = time.time()
    print(f"\nTotal execution time: {end - start:.2f} seconds")