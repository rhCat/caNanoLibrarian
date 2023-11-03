import configparser
import os
import openai
import tiktoken
import os.path


config_dir = os.path.dirname(__file__)
config = configparser.ConfigParser()
config.read(os.path.join(config_dir, 'gpt_local_config.cfg'))

openai.api_key = config.get('token', 'GPT_TOKEN')
model_for_chat = config.get('model', 'model_for_chat')


# https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
def num_tokens_from_string(string: str, model="gpt-3.5-turbo") -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model(model)
    num_tokens = len(encoding.encode(string))

    return num_tokens


def quick_ask(prompt,
              model_num=1,
              max_tokens=500):

    model = ["gpt-4-0314",
             "gpt-3.5-turbo",
             "gpt-4-32k",
             "gpt-3.5-turbo-16k"]

    response = openai.ChatCompletion.create(
            model=model[model_num],
            messages=[{"role": "user",
                       "content": prompt}],
            temperature=0,
            max_tokens=max_tokens
            )

    return response.choices[0]['message']['content']
