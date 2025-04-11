import json
import os

from openai_api import OpenAIAPI

openai = OpenAIAPI()

def RFM_score(freq, recency, decay=1.0):
    return freq / (1 + recency) ** decay

def exp_decay(freq, recency, decay=0.7):
    return decay**recency * freq

class PromptDreamer:
    def __init__(self, qas, size_lib=20):
        assert len(qas) > 0
        self.qas = qas
        self.single = True if len(qas) == 1 else False
        self.use_library = True
        self.library = []
        self.size_lib = size_lib
        # 添加迭代计数器用于追踪库的保存
        self.expansion_count = 0
        
        self.thinking_styles = [
            "analytical",
            "creative",
            "practical",
            "reflective",
            "critical",
        ]
        self.max_iterations = 5
        self.top_prompts_num = 3
        self.top_mutate_num = 2

    def search(self):
        print(self.single)
        if self.single:
            prompt = self.single_search()
            return prompt
        else:
            prompt, fitness, search_history = self.normal_search()
            return prompt, fitness, search_history

    def single_search(self):  
        print("single")
        qa = self.qas[0] if self.qas else None
        if not qa:
            print("no qa")
            return ""
        best_prompt = ""
        best_fitness = 0

        population = []
        for thinking_style in self.thinking_styles:
            # 1. give the question to the LLM to generate an initial prompt
            prompt = (
                f"Create a prompt that would help you answer the following question. Emphasize {thinking_style} thinking. \n"
                + qa["question"]
            )
            print(f"Creating the {thinking_style} prompt.")
            response = openai.chat_prompt(prompt)
            population.append(response)
        
        # for some iterations:
        for i in range(self.max_iterations):
            # 2. evaluate the prompt - if works, continue
            fitness = []
            for p_num, prompt in enumerate(population):
                print(f"Iteration {i}: Testing prompt #{p_num}.")
                response = openai.chat_prompt(prompt + "\n" + qa["question"])
                correct = qa["verifier"](response)
                prompt_fitness = 1 if correct else 0
                fitness.append(prompt_fitness)
                if prompt_fitness > best_fitness:
                    print(f"New best prompt found in iteration {i}.")
                    best_fitness = prompt_fitness
                    best_prompt = prompt
            
            print(f"Population fitness: {fitness}")
            
            if i >= self.max_iterations - 1 or best_fitness == 1:
                break
            
            # 2. perform library expansion
            if self.use_library:
                top_prompts = [
                    item for _, item in sorted(zip(fitness, population), reverse=True)[:self.top_prompts_num]
                ]
                self.library_expansion(top_prompts)
            
            # 3. mutate the prompt - give the LLM the prompt, the question, a "mutation prompt", and the library.
            top_prompts = [
                item for _, item in sorted(zip(fitness, population), reverse=True)[:self.top_mutate_num]
            ]
            print("Mutating a new prompt.")
            
            library_content = ""
            if self.use_library and self.library:
                sorted_lib = sorted(self.library, key=lambda x: RFM_score(x['counter'], x['age']), reverse=True)
                top_subprompts = [sp["content"] for sp in sorted_lib[:self.top_prompts_num]]
                library_content = "Here are some successful subprompts from the library:\n" + "\n".join(top_subprompts) + "\n\n"
            
            mutation_prompt = (
                f"{library_content}Combine these prompts to create an even better prompt for answering this question: {qa['question']}\n"
                + "\n".join(top_prompts)
            )
            mutated_prompt = openai.chat_prompt(mutation_prompt)
            
            min_index = fitness.index(min(fitness))
            population[min_index] = mutated_prompt
        
        if best_fitness == 0 and population:
            best_prompt = max(population, key=len)
        
        # Save the library
        self.save_library()
        
        # return only the final prompt for single search
        return best_prompt

    def normal_search(self):
        print("normal")
        search_history = {"population": [], "fitness": []}
        best_prompt = ""
        best_fitness = 0
        population = []
        
        for thinking_style in self.thinking_styles:
            example_questions = "\n".join(
                [item["question"] for item in self.qas[: min(len(self.qas), 3)]]
            )
            prompt = (
                f"Create a prompt that would help you answer questions similar to the given example questions. Emphasize {thinking_style}. \n"
                + example_questions
            )
            print(f"Creating the {thinking_style} prompt.")
            response = openai.chat_prompt(prompt)
            population.append(response)

        for i in range(self.max_iterations):
            fitness = []
            for p_num, prompt in enumerate(population):
                num_correct = 0
                for qa_num, qa in enumerate(self.qas):
                    print(f"Iteration {i}: Testing prompt #{p_num} on qa #{qa_num}.")
                    response = openai.chat_prompt(prompt + "\n" + qa["question"])
                    correct = qa["verifier"](response)
                    if correct:
                        num_correct += 1
                prompt_fitness = num_correct / len(self.qas)
                fitness.append(prompt_fitness)
                if prompt_fitness > best_fitness:
                    print(f"New best prompt found in iteration {i}.")
                    best_fitness = prompt_fitness
                    best_prompt = prompt

            print(f"Population fitness: {fitness}")
            search_history["population"].append(population)
            search_history["fitness"].append(fitness)

            if i >= self.max_iterations - 1:
                break

            top_prompts = [
                item for _, item in sorted(zip(fitness, population), reverse=True)[:self.top_prompts_num]
            ]
            if self.use_library:
                self.library_expansion(top_prompts)

            top_mutate_prompts = [
                item for _, item in sorted(zip(fitness, population), reverse=True)[:self.top_mutate_num]
            ]
            print("Mutating a new prompt from the top prompts.")
            
            library_content = ""
            if self.use_library and self.library:
                sorted_lib = sorted(self.library, key=lambda x: RFM_score(x['counter'], x['age']), reverse=True)
                top_subprompts = [sp["content"] for sp in sorted_lib[:self.top_prompts_num]]
                library_content = "Here are some successful subprompts from the library that you can use:\n" + "\n".join(top_subprompts) + "\n\n"
                
            mutation_prompt = (
                f"{library_content}Combine the following prompts to create an even better prompt.\n"
                + "\n".join(top_mutate_prompts)
            )
            mutated_prompt = openai.chat_prompt(mutation_prompt)

            min_index = fitness.index(min(fitness))
            population[min_index] = mutated_prompt
        
        # Save the library
        self.save_library()

        return best_prompt, best_fitness, search_history

    def library_expansion(self, prompts: str):
        print("Expanding library")
        for item in self.library:
            item["age"] += 1

        sub_prompts = []
        for prompt in prompts:
            sub_prompts += prompt.strip("\n").split(". ")

        for sub_prompt in sub_prompts:
            
            sim=self.sim(sub_prompt) if self.use_library else 0
            if sim in range(len(self.library)):
                self.library[sim-1]["counter"] += 1
            else:
                self.library.append({"content": sub_prompt, "counter": 1,'age':0})

        self.update_library()
        
        # 每次扩展库后保存当前库状态，使用扩展计数作为文件名
        self.save_library_iteration()
        self.expansion_count += 1

    def update_library(self):
        self.library.sort(
            key=lambda x: RFM_score(x['counter'],x['age']), reverse=True
        )

        if len(self.library) > self.size_lib:
            self.library = self.library[: self.size_lib]

    def sim(self,sub_prompt):
        prompt='Check if this candidate sentence is similar to the given library of sentences. If so, return only the index of the most similar sentence. If not, return only 0.\n'
        prompt += f"Candidate: {sub_prompt}\n"
        
        library_items = []
        for i, item in enumerate(self.library):
            library_items.append(f"{i+1} {item['content']}")
        prompt += f"Library: {chr(10).join(library_items)}\n"
        
        response=openai.chat_prompt(prompt)
        
        try:
            return int(response.strip())-1
        except:
            return -1
            
    def save_library(self):
        with open("prompt_library.json", "w") as f:
            json.dump(self.library, f, indent=4)
        print("Library saved to prompt_library.json")
    
    def save_library_iteration(self):
        os.makedirs("libraries", exist_ok=True)
        filename = f"libraries/library_{self.expansion_count}.json"
        with open(filename, "w") as f:
            json.dump(self.library, f, indent=4)
        print(f"Library expansion #{self.expansion_count} saved to {filename}")


def load_library(filename="prompt_library.json"):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading library: {e}, load emtpy file")
        return []


def convert_aqua_item_to_pdr(aqua_item):
    answer_string = ""
    for opt in aqua_item["options"]:
        answer_string += opt + " "
    question = (
        "Choose the corrent answer. ONLY RESPOND WITH THE LETTER."
        + aqua_item["question"]
        + " "
        + answer_string
    )

    def verifier(response):
        if not response:
            return False
        answer = response[0]
        is_correct = False
        if answer == aqua_item["correct"]:
            is_correct = True
        return is_correct

    pdr_item = {"question": question, "verifier": verifier}
    return pdr_item


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        "--single",
        action="store_true",
        help="Set to search for a prompt for a single QA pair.",
    )
    parser.add_argument(
        "-l",
        "--load-library",
        action="store_true",
        help="Load previously saved library.",
    )
    args = parser.parse_args()
    single = args.single
    load_lib = args.load_library


    aqua = []
    with open("data/AQuA-RAT/train.json", "r") as file:
        for line in file:
            aqua.append(json.loads(line))

    test_pdr_item = convert_aqua_item_to_pdr(aqua[0])
    print(test_pdr_item["verifier"]("E")) 
    print(test_pdr_item["verifier"]("A"))  

    initial_library = []
    if load_lib:
        initial_library = load_library()
        print(f"Loaded library with {len(initial_library)} subprompts")

    if single:
        qa = [convert_aqua_item_to_pdr(aqua[0])]
        pdr = PromptDreamer(qa)
        if load_lib:
            pdr.library = initial_library
        
        prompt = pdr.search()
        print("Final prompt:")
        print(prompt)
        
    else:
        qas = list(map(convert_aqua_item_to_pdr, aqua[:25]))
        pdr = PromptDreamer(qas)
        if load_lib:
            pdr.library = initial_library
            
        prompt, fitness, history = pdr.search()
        print("Final prompt:")
        print(prompt)
        print(f"Final fitness: {fitness}")
        with open("search_history.json", "w") as f:
            json.dump(history, f, indent=4)