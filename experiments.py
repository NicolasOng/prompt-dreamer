from promptdreamerv2 import PromptDreamer
from datasets import load_aqua_dataset, load_mbpp_dataset

from openai_api import OpenAIAPI
openai = OpenAIAPI()

def test_qa_pair(qa, prompt):
    response = openai.chat_prompt(prompt + qa["question"])
    is_correct = qa["verifier"](response)
    return is_correct

def run_single_experiment(data):
    num_correct = 0
    num_total = 0
    correct_list = []
    prompt_list = []
    library = []
    for qa in data:
        # create the PD object with the single QA pair
        pdr = PromptDreamer([qa])
        # put the learned library in it
        pdr.library = library
        # do the search
        prompt = pdr.search()
        # save the prompt
        prompt_list.append(prompt)
        # update the library
        library = pdr.library
        # test the prompt:
        if test_qa_pair(qa, prompt):
            num_correct += 1
            correct_list.append(1)
        else:
            correct_list.append(0)
        num_total += 1
    # print the scores
    print(f"single search score: {num_correct}/{num_total}")
    print(f"single search over time: {correct_list}")
    # save the search history
    history = {
        "num_correct": num_correct,
        "num_total": num_total,
        "correct_list": correct_list,
        "prompt_list": prompt_list
    }
    with open("single_search_history.json", "w") as f:
            json.dump(history, f, indent=4)

def run_multi_experiment(train, test):
    # create the promptdreamer object with the given training data
    pdr = PromptDreamer(train)
    # find the prompt  
    prompt, fitness, history = pdr.search()
    # save the search history
    with open("multi_search_history.json", "w") as f:
        json.dump(history, f, indent=4)
    # evaluate the found prompt on the test set
    num_correct = 0
    num_total = 0
    for qa in test:
        if test_qa_pair(qa, prompt):
            num_correct += 1
        num_total += 1
    print(f"{num_correct}/{num_total}")
    

if __name__ == "__main__":
    import argparse
    import json

    # get the parameters for the experiment
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        "--single",
        action="store_true",
        help="Set to search for a prompt for a single QA pair.",
    )
    parser.add_argument(
        "-d",
        "--dataset",
        type=str,
        choices=['aqua', 'mbpp'],
        help="set the dataset"
    )
    args = parser.parse_args()

    # load the datasets to use
    aqua = load_aqua_dataset()
    mbpp = load_mbpp_dataset()
    if args.dataset == "aqua":
        data1 = aqua[:25]
        data2 = aqua[25:50]
    else:
        data1 = mbpp[:25]
        data2 = mbpp[25:50]

    # run the experiment
    if args.single:
        run_single_experiment(data1)
    else:
        run_multi_experiment(data1, data2)
