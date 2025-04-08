import json
from openai_api import OpenAIAPI

openai = OpenAIAPI()

#r = openai.chat_prompt("Hello, how are you?")
#print(openai.history)
#openai.print_costs()
#print(r)

'''
with open('data/multiarith/test.json', 'r') as file:
    data = json.load(file)

for question in data[5:15]:
    response = openai.chat_prompt("Answer with just a single number in arabic numerals. " + question['question'])
    print(f"Response: {response}")
    print(f"Answer: {question['final_ans']}")
    print()


openai.print_costs()
'''

def get_aqua_answer(question):
    options = question['options']
    correct = question['correct']
    pos_dict = {'A':0, 'B':1, 'C':2, 'D':3, 'E':4}
    cor_answer = options[pos_dict[correct]]
    number = cor_answer.lstrip("ABCDEFGHIJKLMNOPQRSTUVWXYZ)")  # strips letters and the ")"
    return number

data = []
with open('data/AQuA-RAT/train.json', 'r') as file:
    for line in file:
        data.append(json.loads(line))

for question in data[:5]:
    answer_string = ""
    for opt in question['options']:
        answer_string += opt + " "
    response = openai.chat_prompt("Choose the corrent answer. ONLY RESPOND WITH THE LETTER." + question['question'] + " " + answer_string)
    print(f"Response: {response}")
    print(f"Answer: {question['correct']}")

openai.print_costs()
