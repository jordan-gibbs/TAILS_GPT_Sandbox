from openai import OpenAI

client = OpenAI()  # Valid if you have saved your api key as an environment variable
# client = OpenAI(api_key = 'Your API Key here')


def basic_completion():
    # The most basic GPT interaction; a system prompt and a user prompt creates an AI output.
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        temperature=0.8,
        # seed=45735737357357,  # Seed only works with gpt-4 preview model
        messages=[{"role": "system", "content": f"You are a helpful assistant."},
                  {"role": "user", "content": f"Output a random vegetable."}]
    )
    return response.choices[0].message.content


if __name__ == '__main__':
    print(basic_completion())
