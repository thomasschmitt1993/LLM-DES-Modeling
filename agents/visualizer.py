from openai import OpenAI

class Modelvisualizer:
    def __init__(self, client: OpenAI):
        self.client = client

    def visualize_agent(self, model_source: str) -> str:
        print("\nVisualizer activated:")
        return self._visualize_agent(model_source)

    def _visualize_agent(
        self,
        model_source: str,
        model: str = "gpt-5-mini",
    ) -> str:
        prompt = (
            "You get Python code for a discrete-event simulation model.\n"
            "Create a Mermaid flowchart that shows the main material/part flow.\n\n"
            "HARD REQUIREMENTS:\n"
            "1) Output ONLY Mermaid code: no markdown fences, no ```python blocks, no explanations.\n"
            "2) The first non-empty line MUST be exactly: flowchart TD\n"
            "3) Immediately after that, define these classes and use them consistently:\n"
            "   classDef buffer fill:#ffffff,stroke:#333333,stroke-width:1px,stroke-dasharray:3 3,color:#000;\n"
            "   classDef machine fill:#d2e7ff,stroke:#004a99,stroke-width:1px,color:#000;\n"
            "   classDef store fill:#ffe08a,stroke:#b87a00,stroke-width:1px,color:#000;\n"
            "   classDef sink fill:#ffb3b3,stroke:#990000,stroke-width:1px,color:#000;\n"
            "   classDef defect fill:#ff9999,stroke:#660000,stroke-width:1px,color:#000;\n"
            "   classDef helper fill:#e0e0e0,stroke:#666666,stroke-width:1px,color:#000;\n\n"
            "Mapping:\n"
            "- Raw material inputs / Stores / warehouses => class 'store'.\n"
            "- Finished-good sinks => class 'sink'.\n"
            "- Defect / scrap sinks => class 'defect'.\n"
            "- Machines, robots, presses, cells => class 'machine'.\n"
            "- Buffers, queues, delay buffers => class 'buffer'.\n"
            "- Splitters, mergers, routers, helper logic => class 'helper'.\n\n"
            "Label format:\n"
            "- Use valid identifiers (letters, digits, underscore) for node IDs.\n"
            "- ALL node labels must use real line breaks inside the brackets.\n"
            "- Never output '\\n' or '\\\\n' anywhere in any label (including stores and sinks).\n"
            "- The first line of every label must be the node name written in **bold**, using Markdown syntax.\n"
            "  Example:\n"
            "      node_id[\"**Label**\n"
            "      CT=12s\n"
            "      AVB=90%\n"
            "      MTTR=68s\"]:::machine\n"
            "Edges:\n"
            "- Use '-->' to show material flow, top to bottom.\n"
            "- Add short edge labels where routing is important (optional).\n\n"
            "Here is the Python model:\n\n"
            f"{model_source}\n\n"
            "Now output only the Mermaid flowchart that follows these rules."
        )
        resp = self.client.chat.completions.create(
            model=model,messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content

        # If the model accidentally wraps output in ``` fences, strip them.
        # if mmd.startswith("```"):
        #    parts = mmd.split("```")
        #    Pick the longest part that contains 'flowchart'
        #    candidates = [p for p in parts if "flowchart" in p]
        #    if candidates:
        #        mmd = max(candidates, key=len).strip()

        # Ensure it starts with flowchart TD; if not, prepend it with the classDefs.
        # if not mmd.lstrip().startswith("flowchart TD"):
        #    Prepend the desired style block (in case the model forgot).
        #    style_block = (
        #        "flowchart TD\n"
        #        "    classDef buffer fill:#ffffff,stroke:#333333,stroke-width:1px,stroke-dasharray:3 3,color:#000;\n"
        #        "    classDef machine fill:#d2e7ff,stroke:#004a99,stroke-width:1px,color:#000;\n"
        #        "    classDef store fill:#ffe08a,stroke:#b87a00,stroke-width:1px,color:#000;\n"
        #        "    classDef sink fill:#ffb3b3,stroke:#990000,stroke-width:1px,color:#000;\n"
        #        "    classDef defect fill:#ff9999,stroke:#660000,stroke-width:1px,color:#000;\n"
        #        "    classDef helper fill:#e0e0e0,stroke:#666666,stroke-width:1px,color:#000;\n"
        #     )
        #     mmd = style_block + "\n" + mmd.lstrip()

        # return mmd