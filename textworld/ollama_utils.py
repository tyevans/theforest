import json
import re
from ollama import Client

json_pattern = r"(\{.*\})"
json_extract_regex = re.compile(json_pattern, re.MULTILINE | re.DOTALL)


class OllamaClient:

    def __init__(self, base_url, model):
        self._client = Client(host=base_url)
        self.model = model

    def generate(self, prompt, system):
        response = self._client.generate(
            model=self.model,
            prompt=prompt,
            system=system,
            keep_alive=300.
        )
        model_output = response["response"]
        match = json_extract_regex.search(model_output)
        if match:
            try:
                return json.loads(match.group(1))
            except json.decoder.JSONDecodeError:
                return None

    def embedding(self, content):
        response = self._client.embeddings(
            model=self.model,
            prompt=content
        )
        return response
