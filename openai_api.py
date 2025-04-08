# pip install openai
# export OPENAI_API_KEY="your_api_key_here"

import os
import json
from datetime import datetime

from openai import OpenAI
import openai

client = OpenAI()

class OpenAIAPI:
    def __init__(self):
        self.api = "OpenAI"
        self.models = {}
        self.history = []
        self.filename = os.environ.get("OPENAI_HIST_FN")
    
    def add_tokens(self, model, token_type, tokens):
        if (model not in self.models): self.models[model] = {}
        if (token_type not in self.models[model]): self.models[model][token_type] = 0
        self.models[model][token_type] += tokens
    
    def chat_prompt_full(self, prompt):
        '''
        sends a prompt to OpenAI and records it.
        '''
        response = client.responses.create(
            model="gpt-4o-mini",
            input=prompt
        )
        self.add_tokens(response.model, "output_tokens", response.usage.output_tokens)
        self.add_tokens(response.model, "input_tokens", response.usage.input_tokens)
        self.history.append({"model": response.model, "prompt": prompt, "response": response})
        return response
    
    def chat_prompt(self, prompt):
        response = self.chat_prompt_full(prompt)
        return response.output[0].content[0].text

    def write_history(self):
        '''
        creates a json file with the API history from this session.
        '''
        now = datetime.now()
        date_time = now.strftime("%m-%d-%Y_%H%M%S")
        costs = self.get_costs()
        with open(self.filename + date_time + '.json', 'w') as convert_file:
            convert_file.write(json.dumps({"costs": costs, "token usage": self.models, "prompt history": self.history}))
    
    def get_costs(self):
        cost_dict = {}
        for model in self.models:
            cost_dict[model] = 0
        for model in self.models:
            model_total = 0
            for tt in self.models[model]:
                model_total += self.models[model][tt]
            if ("gpt-4o-mini" in model):
                cost = (model_total / 1000000) * 0.15
                cost_dict[model] += cost
        return cost_dict
    
    def print_costs(self):
        costs = self.get_costs()
        for model in costs:
            cost = costs[model]
            print(f"{model}: ${cost}")

if __name__ == "__main__":
    openai_api = OpenAIAPI()
    e = openai_api.full_embedding(["Hello, world!", "Goodbye, world!"])
    #print(e)
    openai_api.print_costs()
