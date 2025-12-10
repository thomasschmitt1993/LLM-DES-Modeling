from openai import OpenAI
import json
from helpers.other_helpers import retrieve_KPIs, save_model, remove_code_wrappers

class Modeladaptor:
    def __init__(self, client: OpenAI):
        self.client = client

    def adapter(self, original_code, instruction, final_path, multi_agent_setting: bool, index_model = 0):
        print("\nAdapting process:")
        if not multi_agent_setting: 
            print(f"Step {index_model} Worker activated:")
            adapted_code = self._modify_code(original_code, instruction)

        if multi_agent_setting:
            print(f"Step {index_model} Instructor activated:")
            instructions = self._operator_analyze_instruction(instruction, original_code)
            steps = instructions.get("steps", [instruction])
            #Initially needs to be the original code and then constantly updated.
            current_code = original_code
            for step in steps:
                print("Worker activated:")
                current_code = self._modify_code(current_code, step)
            print("Inspector activated:")
            adapted_code = self._inspector(current_code)

        # Clean the modified code from wrappers.
        clean_code = remove_code_wrappers(adapted_code)

        # Save the final cleaned code.
        filename = f"adapted_model_step{index_model}.py"
        save_model(clean_code, final_path, filename)
        modelinfo = f"Adapted model version {index_model}"

        return retrieve_KPIs(clean_code, str(modelinfo))

    def _operator_analyze_instruction(self, instruction, original_code,
        model: str = "gpt-4o",
        response_format={"type": "json_object"}):
        prompt = (
            "You are an operator agent that analyzes a code modification task. "
            "Consider the following instruction and the provided Python code. "
            "Your goal is to decide if the instruction is compound (i.e., contains multiple distinct changes) "
            "and, if so, split it into sequential steps. Each step should still include the complete code!"
            "Only output valid JSON.\n\n"
            f"Here is my Python code:\n\n```python\n{original_code}\n```\n\n"
            f"Instruction: {instruction}")
        resp = self.client.chat.completions.create(model = model, messages=[{"role": "user", "content": prompt}], response_format = response_format)    
        operator_output = resp.choices[0].message.content.strip()
        try:
            # convert it to a python object
            instructions_json = json.loads(operator_output)
            return instructions_json
        except Exception as e:
            # If parsing fails, assume a single-step instruction.
            return {"steps": [instruction]}
    
    def _inspector(self, code,
        model: str = "gpt-5-mini"):
        prompt = (
            "Please evaluate if the following Python code is correct. "
            "If it is correct, do nothing. If it is incorrect, please adapt it so that it runs correctly. Only answer with the code.\n\n"
            f"```python\n{code}\n```")
        resp = self.client.chat.completions.create(
            model = model, messages=[{"role": "user", "content": prompt}])
        return resp.choices[0].message.content

    def _modify_code(self, original_code, instruction,
        model: str = "gpt-5-mini"):
        prompt = (
            f"Here is my Python code:\n\n```python\n{original_code}\n```\n\n"
            f"Modify it according to this instruction:\n\n{instruction}\n"
            "Only answer with the code.")
        resp = self.client.chat.completions.create( model = model, messages=[{"role": "user", "content": prompt}])
        return resp.choices[0].message.content