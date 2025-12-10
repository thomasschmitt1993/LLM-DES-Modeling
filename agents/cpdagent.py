from openai import OpenAI

class CPD:
    def __init__(self, client: OpenAI):
        self.client = client

    def evaluatecpd(self, listofchanges, cpd_info):
        print("\nSafety Inspector activated:")
        return self._evaluatorcpd(listofchanges, cpd_info)

    def _evaluatorcpd(self, listofchanges, cpd_info,
        model = "gpt-5-mini"): 
        prompt = (
            f"Here is a list of changes:\n\n```\n{listofchanges}\n```\n\n"
            f"And here is a list of critical processes that one should look out for:\n\n```\n{cpd_info}\n```\n\n"
            "Please check if any of the suggested changes are part of the critical processes."
            "If this is the case, return the number of the change (e.g. the 2nd) and the change itself."
            "Explain why it is critical. If none of the changes are critical, simply answer with 'No critical changes found.")
        resp = self.client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": prompt}]
        )
        return resp.choices[0].message.content