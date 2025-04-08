from openai_api import OpenAIAPI

openai = OpenAIAPI()

r = openai.chat_prompt("Hello, how are you?")
#print(openai.history)
#openai.print_costs()
print(r)
