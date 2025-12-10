from openai import OpenAI
import json
from helpers.runner import run_python_code

class Modeloptimizer:
    def __init__(self, client: OpenAI):
        self.client = client

    def optimize(self, model_code: str, bottlenecks: list[str]):
        print("\nOptimizer activated:")
        print("\nUsing provided bottlenecks:")
        print("\n".join(bottlenecks))
        #bottlenecks = self._extract_bottlenecks(model_code)
        #print(f"\nBottlenecks: {bottlenecks}")
        print("\nLooking for solutions:")
        suggestions = self._suggest_improvements(model_code, "\n".join(bottlenecks))
        return suggestions

    def _suggest_improvements(self, model_code, results_bottleneck,
        model = "gpt-4o",
        response_format={"type": "json_object"}):
        prompt = (
                "Please name 3 specific implementable instructions to improve the system. "
                "These should be short and concise statements, e.g. Increase the buffer size of X to 40. "
                "They should be easily implementable with the existing model. "
                f"Here is my Python code:\n\n```python\n {model_code}\n```\n\n"
                f"Here are the results of the bottleneck analysis:\n\n {results_bottleneck}\n"
                "Only answer with the instructions in a json format.")
        resp = self.client.chat.completions.create(
            model=model,response_format = response_format, messages=[{"role": "user", "content": prompt}])
        try:
            operator_output = resp.choices[0].message.content.strip()
            instructions_json = json.loads(operator_output)
            return instructions_json
        except Exception as e:
            raise
    
    def _extract_bottlenecks(self, model_code): #not used anymore
        output_bottleneck = run_python_code(model_code)
        all_output = output_bottleneck.splitlines()
        start_collecting = False
        filtered_output = []
        for line in all_output:
            if start_collecting:
                filtered_output.append(line)
            if "=== Bottleneck Frequency over runs ===" in line:
                start_collecting = True  # start collecting subsequent lines
                continue
        return filtered_output