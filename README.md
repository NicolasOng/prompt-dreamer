# Environment
```bash
pip install openai
```

# Datasets
Organize your folders like this:

- data
  - AQuA-RAT
    - train.json
  - mbpp
    - mbpp.jsonl

## MultiArith
This one is too easy.

https://huggingface.co/datasets/ChilleD/MultiArith/tree/main

```json
{
    "question": " Paige had 11 songs on her mp3 player. If she deleted 9 old songs from it and then added 8 new songs, how many songs does she have on her mp3 player? ",
    "final_ans": "10"
}
```

## AQuA-RAT
https://github.com/google-deepmind/AQuA

```json
{
    "question": "John found that the average of 15 numbers is 40. If 10 is added to each number then the mean of number is?",
    "options": ["A)50", "B)45", "C)65", "D)78", "E)64"],
    "rationale": "(x+x1+...x14)/15 = 40\n50\nOption A",
    "correct": "A"
}
```

## mbpp
https://github.com/google-research/google-research/tree/master/mbpp

```json
{
    "text": "Write a python function to find the volume of a triangular prism.",
    "code": "def find_Volume(l,b,h) : \r\n    return ((l * b * h) / 2) ",
    "task_id": 14,
    "test_setup_code": "",
    "test_list": [
        "assert find_Volume(10,8,6) == 240",
        "assert find_Volume(3,2,2) == 6",
        "assert find_Volume(1,2,1) == 1"],
    "challenge_test_list": []
}
```
# LLM API
To use OpenAI's API:
```sh
export OPENAI_API_KEY="key here"
python3 use_openai_script.py
```

`use_openai_script.py`:
```python
from openai_api import OpenAIAPI
openai = OpenAIAPI()
print(openai.chat_prompt("Hello."))
openai.print_costs()
```

Using my `OpenAIAPI` script, a file `token_useage.json` is created that keeps track of how many tokens we've used.
```json
{
    "gpt-4o-mini-2024-07-18": {
        "output_tokens": 77188,
        "input_tokens": 328098
    }
}
```

Use `gpt-4o-mini` for all experiments.
