class PromptDreamer():
    def __init__(self, qas, problem_description):
        assert(len(qas) > 0)
        self.qas = qas
        self.single = True if len(qas) == 1 else False
    
    def search(self):
        if single:
            prompt = self.single_search()
        else:
            prompt = self.normal_search()
        return prompt
    
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
        # 1. generate initial population of prompts (~5) by giving the LLM:
        # problem description, thinking style

        # for some iterations:
        
            # 2. evaluate their fitness - run on all the given qas. score is percentage correct. LLM(P + Q) = A

            # 3. Mutate the best 2 with mutation prompts. eg
            # - one parent: "reword this prompt"
            # - multi parents: "continue this list of prompts"

            # 4. Replace the bottom 2 with these mutations

            # 5. Perform library expansion with the top ~3 prompts
        
        # 6. return the prompt with the best results
        pass

def convert_aqua_item_to_pdr(aqua_item):
    answer_string = ""
    for opt in aqua_item['options']:
        answer_string += opt + " "
    question = "Choose the corrent answer. ONLY RESPOND WITH THE LETTER." + aqua_item['question'] + " " + answer_string
    def verifier(response):
        answer = response[0]
        if answer == aqua_item['correct']:
            num_correct += 1
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

    aqua = []
    with open('data/AQuA-RAT/train.json', 'r') as file:
        for line in file:
            aqua.append(json.loads(line))
    
    if single:
        qa = [convert_aqua_item_to_pdr(aqua[0])]
        pdr = PromptDreamer(qa)
    else:
        qas = map(convert_aqua_item_to_pdr, aqua[:100])
        pdr = PromptDreamer(qas)

    prompt = pdr.search()
