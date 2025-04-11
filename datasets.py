import json

def convert_aqua_item_to_pdr(aqua_item):
    # create the question for the LLM to answer
    answer_string = ""
    for opt in aqua_item["options"]:
        answer_string += opt + " "
    question = (
        "Choose the corrent answer. ONLY RESPOND WITH THE LETTER."
        + aqua_item["question"]
        + " "
        + answer_string
    )

    # returns true if the first character of the LLM's response is the correct letter
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

def replace_function_name(test_list):
    new_list = []
    for line in test_list:
        start = line.find("assert ") + len("assert ")
        end = line.find("(", start)
        new_line = "assert function" + line[end:]
        new_list.append(new_line)
    return new_list

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

def convert_mbpp_item_to_pdr(mbpp_item):
    # create the question string for the LLM to answer
    # replace the function name in the list of test cases so LLM doesn't use that as a hint.
    test_cases = replace_function_name(mbpp_item["test_list"])
    new_test_case = replace_function_name([mbpp_item["new_test"]])
    test_cases_str = "\n".join(test_cases)
    new_test_case_str = "\n".join(new_test_case)
    prompt = "Write a python function satisfying the following test cases:\n" + test_cases_str + "Don't add any explanations or additional text. You response will be written to a file and run."
    
    # returns true if the code runs without errors (would error if one of the test cases doesn't pass).
    def verifier(response):
        response_code = clean_code_block(response)
        code_to_run = response_code + "\n" + test_cases_str + "\n" + new_test_case_str
        outcome = safe_exec(code_to_run)
        return outcome
    
    pdr_item = {"question": prompt, "verifier": verifier}
    return pdr_item

def load_aqua_dataset():
    # load the aqua dataset
    aqua = []
    with open('data/AQuA-RAT/train.json', 'r') as file:
        for line in file:
            aqua.append(json.loads(line))
    # convert all the items to pdr format
    aqua = list(map(convert_aqua_item_to_pdr, aqua))
    return aqua

def load_mbpp_dataset():
    # load mbpp dataset, but altered to have new validation IO pairs.
    with open('data/mbpp/new_trimmed_mbpp.json', 'r') as file:
        mbpp = json.load(file)
    # convert everything into pbr format
    mbpp = list(map(convert_mbpp_item_to_pdr, mbpp))
    return mbpp

if __name__ == "__main__":
    import time
    from openai_api import OpenAIAPI
    openai = OpenAIAPI()

    test_amount = 100
    aqua = load_aqua_dataset()[:test_amount]
    mbpp = load_mbpp_dataset()[:test_amount]

    # evaluate the llm on the aqua dataset (no prompts)
    num_correct = 0
    start_time = time.time()
    for i, aq in enumerate(aqua):
        print(f"Answering AQuA Q #{i}...")
        response = openai.chat_prompt(aq["question"])
        is_correct = aq["verifier"](response)
        if is_correct: num_correct += 1
    end_time = time.time()
    print(f"AQuA: {num_correct}/{test_amount} correct.")
    print(f"Elapsed time: {end_time - start_time:.2f} seconds")

    # evaluate the llm on the mbpp dataset (no prompts)
    num_correct = 0
    start_time = time.time()
    for i, mq in enumerate(mbpp):
        print(f"Answering mbpp Q #{i}...")
        response = openai.chat_prompt(mq["question"])
        is_correct = mq["verifier"](response)
        if is_correct: num_correct += 1
    end_time = time.time()
    print(f"mbpp: {num_correct}/{test_amount} correct.")
    print(f"Elapsed time: {end_time - start_time:.2f} seconds")
