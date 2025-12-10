from openai import OpenAI

class ModelBuilder:
    def __init__(self, client: OpenAI):
        self.client = client

    def build(self, blueprint_code, stations_table_md, sequence_text, buffers, defects, manual_note = "", sim_time=8*24*3600, warmup_seconds=24*3600, replications = 10):
        print("\nBuilder activated:")
        initial_model = self._builder(blueprint_code, stations_table_md, sequence_text, buffers, defects, manual_note, sim_time, warmup_seconds, replications)
        print("\nInspector activated:")
        checked_initial_model = self._inspector(initial_model, stations_table_md, sequence_text, buffers, defects, manual_note)
        return checked_initial_model

    def _builder(self, blueprint_code, stations_table_md, sequence_text, buffers, defects, manual_note, sim_time, warmup_seconds, replications,
        model = "gpt-5.1"):
        prompt = (
            "Please adapt the Python code to represent the following production line. "
            "Parallel processes split the stream of objects evenly. "
            "Ensure that the capacities of the buffers (raw and normal) match the input, and that all (helper) buffers have a defined capacity.\n\n"
            f"```python\n{blueprint_code}\n```\n\n"
            f"Stations table:\n\n{stations_table_md}\n\n"
            f"Buffer list with their capacity and process time:\n\n{buffers}\n\n"
            f"Direct-follow relationships:\n\n{sequence_text}\n\n"
            f"Defects:\n\n{defects}\n\n"
            f"{manual_note}\n\n"
            f"Simulation time: {sim_time}\n\n"
            f"Warm-up period: {warmup_seconds}\n\n"
            f"Replications: {replications}\n\n"
            "Only answer with the code.")
        resp = self.client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": prompt}])
        try:
            return resp.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"No completion was returned: {e}")

    def _inspector(self, initial_code, stations_table_md, sequence_text, buffers, defects, manual_note,
        model: str = "gpt-5.1"):
        prompt = (
            "Please check that the following Python code represents the following production line. "
            "Please check that handoff channels or other storage elements have defined capacity values, except for sinks or sources."
            "Parallel processes split the stream of objects evenly.\n\n"
            f"```python\n{initial_code}\n```\n\n"
            f"Stations table:\n\n{stations_table_md}\n\n"
            f"Buffer list with their capacity and process time:\n\n{buffers}\n\n"
            f"Direct-follow relationships:\n\n{sequence_text}\n\n"
            f"Defects:\n\n{defects}\n\n"
            f"{manual_note}\n\n"
            "If it is correct, do nothing. If it is incorrect, please adapt it so that it runs correctly. Only answer with the code.\n\n")
        resp = self.client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": prompt}])
        try:
            return resp.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"No completion was returned: {e}")