from openai import OpenAI

client = OpenAI()  # Valid if you have saved your api key as an environment variable


def basic_completion_stream():
    # A basic completion, but the response streams in word by word
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        temperature=0.8,
        messages=[{"role": "system", "content": f"You are a helpful assistant."},
                  {"role": "user", "content": f"Tell me a brief, original parable."}],
        stream=True
    )
    answer_accumulator = ''
    for chunk in response:
        choice = chunk.choices[0]
        if choice.delta and choice.delta.content:
            answer = choice.delta.content
            answer_accumulator += answer
            print(answer, end='', flush=True)
    return answer_accumulator


if __name__ == '__main__':
    basic_completion_stream()
