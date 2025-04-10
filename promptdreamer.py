import json

from openai_api import OpenAIAPI
openai = OpenAIAPI()

class PromptDreamer():
    def __init__(self, qas):
        assert(len(qas) > 0)
        self.qas = qas
        self.single = True if len(qas) == 1 else False
        self.use_library = True
        self.library = []
    
    def search(self):
        print(self.single)
        if self.single:
            prompt = self.single_search()
        else:
            prompt = self.normal_search()
        return prompt

    def single_search_batch(self):
        for qa in self.qas:
            if True:
                self.single_search(qa)
            else:
                self.single_search(qa)
    
    def single_search(self):
        # 1. give the question to the LLM to generate an initial prompt

        # for some iterations:

            # 2. perform library expansion

            # 2. evaluate the prompt - if works, return. if not, continue

            # 3. mutate the prompt - give the LLM the prompt, the question, a "mutation prompt", and the library.

        # 4. return the final prompt
        pass

    def library_expansion(self, prompts):
        # as in class, more sub-programs is good as it shortens the length of the programs, but too many too choose from is bad as well.
        # we should only keep the most useful sub-prompts in the library.

        # 1. check if any of the current sub-prompts are in the given prompts. If so, increment their counters.

        # 2. extract some sub-prompts from the current set of prompts. increment their counters and add the best n to the library.

        # 3. kick out hte lowest n from the library (if full)
        pass

    def normal_search(self):
        search_history = {
            "population": [],
            "fitness": []
        }
        best_prompt = ""
        best_fitness = 0
        iterations = 5
        # 1. generate initial population of prompts (~5) by giving the LLM:
        # problem description, thinking style
        thinking_styles = [
            "analytical", "creative", "practical", "reflective", "critical"
        ]
        population = []
        for thinking_style in thinking_styles:
            example_questions = "\n".join([item["question"] for item in self.qas[:min(len(self.qas), 3)]])
            prompt = f"Create a prompt that would help you answer questions similar to the given example questions. Emphasize {thinking_style}. \n" + example_questions
            print(f"Creating the {thinking_style} prompt.")
            response = openai.chat_prompt(prompt)
            population.append(response)

        # for some iterations:
        for i in range(iterations):
            # 2. evaluate their fitness - run on all the given qas. score is percentage correct. LLM(P + Q) = A
            fitness = []
            for p_num, prompt in enumerate(population):
                num_correct = 0
                for qa_num, qa in enumerate(self.qas):
                    print(f'Iteration {i}: Testing prompt #{p_num} on qa #{qa_num}.')
                    response = openai.chat_prompt(prompt + "\n" + qa["question"])
                    correct = qa["verifier"](response)
                    if correct: num_correct += 1
                prompt_fitness = num_correct / len(self.qas)
                fitness.append(prompt_fitness)
                if prompt_fitness > best_fitness:
                    print(f'New best prompt found in iteration {i}.')
                    best_fitness = prompt_fitness
                    best_prompt = prompt
            
            print(f'Population fitness: {fitness}')
            search_history["population"].append(population)
            search_history["fitness"].append(fitness)
            
            if i >= iterations - 1: break

            # 3. Perform library expansion with the top ~3 prompts
            top_3_prompts = [item for _, item in sorted(zip(fitness, population), reverse=True)[:3]]
            self.library_expansion(top_3_prompts)

            # 4. Mutate the best 2 with mutation prompts. eg
            # - one parent: "reword this prompt"
            # - multi parents: "continue this list of prompts"
            # also give the library as inspiration.
            top_2_prompts = [item for _, item in sorted(zip(fitness, population), reverse=True)[:2]]
            print("Mutating a new prompt from the top 2 prompts.")
            mutation_prompt = "Combine the two given prompts to create an even better prompt.\n" + "\n".join(top_2_prompts)
            mutated_prompt = openai.chat_prompt(mutation_prompt)

            # 5. Replace the bottom with this mutation
            min_index = fitness.index(min(fitness))
            population[min_index] = mutated_prompt
        
        # 6. return the prompt with the best results
        return best_prompt, best_fitness, search_history

def convert_aqua_item_to_pdr(aqua_item):
    answer_string = ""
    for opt in aqua_item['options']:
        answer_string += opt + " "
    question = "Choose the corrent answer. ONLY RESPOND WITH THE LETTER." + aqua_item['question'] + " " + answer_string
    def verifier(response):
        answer = response[0]
        is_correct = False
        if answer == aqua_item['correct']:
            is_correct = True
        return is_correct
    pdr_item = {
        "question": question,
        "verifier": verifier
    }
    return pdr_item

if __name__ == '__main__':
    import argparse
    import json
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--single", action="store_true", help="Set to search for a prompt for a single QA pair.")
    args = parser.parse_args()
    single = args.single

    single = False

    aqua = []
    with open('data/AQuA-RAT/train.json', 'r') as file:
        for line in file:
            aqua.append(json.loads(line))

    test_pdr_item = convert_aqua_item_to_pdr(aqua[0])
    print(test_pdr_item["verifier"]("E")) # correct
    print(test_pdr_item["verifier"]("A")) # incorrect
    
    if single:
        qa = [convert_aqua_item_to_pdr(aqua[0])]
        pdr = PromptDreamer(qa)
    else:
        qas = list(map(convert_aqua_item_to_pdr, aqua[:25]))
        pdr = PromptDreamer(qas)

    prompt, fitness, history = pdr.search()
    print(prompt)
    print(fitness)
    with open("search_history.json", "w") as f:
        json.dump(history, f, indent=4)
