from openai import OpenAI
from helpers.other_helpers import retrieve_KPIs

class Evaluater:
    def __init__(self, client: OpenAI):
        self.client = client

    def evaluate(self, results):
        print("\nEvaluator activated:")
        # Need to flatten the nested list
        flat = [line for sub in results for line in sub]
        return self._evaluator(flat)

    def _evaluator(self, results,
        model = "gpt-5-mini"): 
        prompt = (
            f"Here are the results of the original code and the modified code execution:\n\n```\n{results}\n```\n\n"
            "Please go through the different configurations and summarize the best one.")
        resp = self.client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": prompt}])
        return resp.choices[0].message.content