import json
import os
from openai_api import OpenAIAPI

openai = OpenAIAPI()

def test_multiarith():
    with open('data/multiarith/test.json', 'r') as file:
        data = json.load(file)

    for question in data[5:15]:
        response = openai.chat_prompt("Answer with just a single number in arabic numerals. " + question['question'])
        print(f"Response: {response}")
        print(f"Answer: {question['final_ans']}")
        print()

    openai.print_costs()

def get_aqua_answer(question):
    options = question['options']
    correct = question['correct']
    pos_dict = {'A':0, 'B':1, 'C':2, 'D':3, 'E':4}
    cor_answer = options[pos_dict[correct]]
    number = cor_answer.lstrip("ABCDEFGHIJKLMNOPQRSTUVWXYZ)")  # strips letters and the ")"
    return number

def test_aqua(no_thinking=True):
    data = []
    with open('data/AQuA-RAT/train.json', 'r') as file:
        for line in file:
            data.append(json.loads(line))

    print(len(data))
    num_correct = 0
    num_to_test = 100
    for question in data[:num_to_test]:
        answer_string = ""
        for opt in question['options']:
            answer_string += opt + " "
        if no_thinking:
            response = openai.chat_prompt("Choose the corrent answer. ONLY RESPOND WITH THE LETTER." + question['question'] + " " + answer_string)
            llm_guess = response[0]
        else:
            response = openai.chat_prompt("Choose the corrent answer. At the end of your response, give only the letter (A, B, C, or D) of the correct answer on a separate line, with no punctuation, brackets, or formatting — just the letter." + question['question'] + " " + answer_string)
            llm_guess = response.strip().splitlines()[-1]
        if llm_guess == question['correct']:
            num_correct += 1
        print(response)
        print(f"Guess: {llm_guess}, Truth: {question['correct']}")
        print("---")

    print(f"number correct: {num_correct}/{num_to_test}")

    openai.print_costs()

def replace_function_name(test_list):
    new_list = []
    for line in test_list:
        start = line.find("assert ") + len("assert ")
        end = line.find("(", start)
        new_line = "assert function" + line[end:]
        new_list.append(new_line)
    return new_list

def rank_mbpp_qs():
    # load mbpp dataset
    data = []
    with open('data/mbpp/mbpp.jsonl', 'r') as file:
        for line in file:
            data.append(json.loads(line))
    # load difficulty file
    difficulty_file = "difficulty.json"
    diff_dict = {"easy": [], "hard": []}
    if os.path.exists(difficulty_file):
        with open(difficulty_file, 'r', encoding='utf-8') as f:
            diff_dict = json.load(f)
    cur_i = max(diff_dict["easy"][-1], diff_dict["hard"][-1]) + 1
    # go through each question
    for i in range(cur_i, len(data)):
        print(i)
        print(data[i]["text"])
        print(json.dumps(replace_function_name(data[i]["test_list"]), indent=4))
        print("---")
        choice = input("Choose 'a' or 'd': ").strip().lower()
        if choice == 'a':
            diff_dict["easy"].append(i)
        if choice == 'd':
            diff_dict["hard"].append(i)
        with open(difficulty_file, 'w', encoding='utf-8') as f:
            json.dump(diff_dict, f, indent=4)

def clean_code_block(code_str):
    lines = code_str.strip().splitlines()

    # Remove opening line if it's a markdown-style code block (e.g., ``` or ```python)
    if lines and lines[0].strip().startswith("```"):
        lines = lines[1:]

    # Remove closing line if it's a backtick block
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]

    # Return the cleaned code
    return "\n".join(lines).strip()

def safe_exec(code):
    try:
        exec(code)  # Use globals() if the code defines functions or variables you want to access later
        return True
    except Exception as e:
        print("Error during execution:", e)
        return False

def test_mbpp():
    # load mbpp dataset
    data = []
    with open('data/mbpp/mbpp.jsonl', 'r') as file:
        for line in file:
            data.append(json.loads(line))
    # go through each question
    for q in data[:5]:
        test_cases = replace_function_name(q["test_list"])
        print(q["text"])
        print(json.dumps(test_cases, indent=4))
        print("---")
        prompt = "Write a python function satisfying the following test cases:\n" + "\n".join(test_cases) + "Don't add any explanations or additional text. You response will be written to a file and run."
        response = openai.chat_prompt(prompt)
        response_code = clean_code_block(response)
        print(response_code)
        code_to_run = response_code + "\n" + "\n".join(test_cases)
        outcome = safe_exec(code_to_run)
        print(outcome)
        choice = input("")

def get_function_name(test_list):
    line = test_list[0]
    start = line.find("assert ") + len("assert ")
    end = line.find("(", start)
    return line[start:end]

def create_test_case(code_str, func_name, new_args_str):
    # Step 1: Clean and execute the code safely
    try:
        exec(code_str, globals())  # Use globals so the function becomes available
    except Exception as e:
        print("Error in code:", e)
        return None
    
    try:
        exec(new_args_str, globals())  # Use globals so the function becomes available
    except Exception as e:
        print("Error in code:", e)
        return None

    # Step 2: Dynamically call the function with new_args
    try:
        func = globals()[func_name]
        result = func(*new_args)
    except Exception as e:
        print("Error running test case:", e)
        return None

    # Step 3: Format it as an assert string
    print(new_args)
    test_case_str = f"assert {func_name}{new_args} == {result}"
    return test_case_str

def mbpp_make_extra_test_case(human=False):
    # load mbpp dataset
    with open('new_mbpp.json', 'r') as file:
        data = json.load(file)
    '''
    data = []
    with open('data/mbpp/mbpp.jsonl', 'r') as file:
        for line in file:
            data.append(json.loads(line))
    '''
    num_errors = 0
    # go through each question
    for i, q in enumerate(data):
        if q["new_test"] is not None: continue
        num_errors += 1
        print(i)
        question_code = q["code"]
        test_cases = q["test_list"]
        #continue
        print(test_cases)
        if not human:
            prompt = "Give me a new set of arguments to put into the function based on what was given.\nSome examples:\nFor 'assert count_ways(2) == 3', you know the function takes in a single integer, so respond with eg new_args = (3).\nassert max_len_sub([2, 5, 6, 3, 7, 6, 5, 8]) == 5, respond with new_args = ([3, 6, 4],).\nassert str_func('str one') == ['str', 'one'], new_args = ('new str', )\nDon't be creative - just replicate one of the inputs and swap a number or letter.\nYour response will be put into the described function to get its output. Do not add anything else." + "\n".join(test_cases)
            response = openai.chat_prompt(prompt)
            new_input = clean_code_block(response)
            #print(response)
        else:
            new_input = input("")
        new_test_case = create_test_case(question_code, get_function_name(test_cases), new_input)
        if new_test_case is None:
            print("Error!")
        #print(question_code)
        print(new_input)
        print(new_test_case)
        data[i]["new_test"] = new_test_case
        with open("new_mbpp.json", 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    print(num_errors)

def prune_new_mbpp():
    # load the new mbpp dataset
    with open('new_mbpp.json', 'r') as file:
        data = json.load(file)

    num_new_tests = 0
    new_data = []
    # go through each question
    for i, q in enumerate(data):
        if q["new_test"] is None: continue
        num_new_tests += 1
        new_data.append(q)
        print(i)
        with open("new_trimmed_mbpp.json", 'w', encoding='utf-8') as f:
            json.dump(new_data, f, indent=4)
    print(f"{num_new_tests}/{len(data)}")

openai.print_costs()

prune_new_mbpp()
