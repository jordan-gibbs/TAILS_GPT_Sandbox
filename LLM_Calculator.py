from openai import OpenAI
import json

client = OpenAI()


def add(a, b):
    """Returns the sum of a and b."""
    return a + b


def subtract(a, b):
    """Returns the result of a minus b."""
    return a - b


def multiply(a, b):
    """Returns the product of a and b."""
    return a * b


def divide(a, b):
    """Returns the result of a divided by b. Returns None if b is zero."""
    if b == 0:
        return None
    return a / b


def exponent(a, b):
    """Returns a raised to the power of b."""
    return a ** b


def root(a, b):
    """Returns the square root of a. The second parameter is ignored."""
    b = 1/b
    return a ** b


def modulus(a, b):
    """Returns the remainder of a divided by b."""
    return a % b


def fibonacci_sequence(n):
    """Generates the first n numbers of the Fibonacci sequence."""
    sequence = []
    a, b = 0, 1
    for _ in range(n):
        sequence.append(a)
        a, b = b, a + b
    return sequence


def is_prime(a):
    """Checks if a number is a prime number."""
    if a <= 1:
        return False
    for i in range(2, int(a**0.5) + 1):
        if a % i == 0:
            return False
    return True


def age_in_seconds(age):
    """Calculates a person's age in seconds based on their age in years."""
    age_seconds = age*31540000
    return age_seconds


def weight_on_planet(earth_weight, planet):
    """Calculates a person's weight on different planets."""
    # Gravity factors for different planets (relative to Earth's gravity)
    gravity_factors = {
        "Mercury": 0.38, "Venus": 0.91, "Earth": 1,
        "Mars": 0.38, "Jupiter": 2.34, "Saturn": 1.06,
        "Uranus": 0.92, "Neptune": 1.19
    }
    return earth_weight * gravity_factors.get(planet, 1)  # Default to Earth if planet not found


def random_number(min_value, max_value):
    """Generates a random number within a specified range."""
    from random import randint
    return randint(min_value, max_value)


def run_calculator(message):
    # Step 1: send the conversation and available functions to the model
    messages = [{"role": "user", "content": f"You are a calculator. You will use the functions available to you"
                                            f" to calculate the user's request. You will never do the math "
                                            f"yourself, you will always use the functions. {message}"}]
    tools = [
        {
            "type": "function",
            "function": {
                "name": "add",
                "description": "Adds two numbers together.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "number", "description": "The first number to add."},
                        "b": {"type": "number", "description": "The second number to add."},
                    },
                    "required": ["a", "b"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "subtract",
                "description": "Subtracts the second number from the first.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "number", "description": "The number to subtract from."},
                        "b": {"type": "number", "description": "The number to subtract."},
                    },
                    "required": ["a", "b"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "multiply",
                "description": "Multiplies two numbers.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "number", "description": "The first number to multiply."},
                        "b": {"type": "number", "description": "The second number to multiply."},
                    },
                    "required": ["a", "b"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "divide",
                "description": "Divides the first number by the second.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "number", "description": "The number to be divided."},
                        "b": {"type": "number", "description": "The number to divide by."},
                    },
                    "required": ["a", "b"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "exponent",
                "description": "Raises the first number to the power of the second.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "number", "description": "The base number."},
                        "b": {"type": "number", "description": "The exponent."},
                    },
                    "required": ["a", "b"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "root",
                "description": "Calculates the 'b' root of 'a'.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "number", "description": "The number to find the root of."},
                        "b": {"type": "number", "description": "The power of the root"},
                    },
                    "required": ["a", "b"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "modulus",
                "description": "Finds the remainder of division of the first number by the second.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "number", "description": "The dividend."},
                        "b": {"type": "number", "description": "The divisor."},
                    },
                    "required": ["a", "b"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "fibonacci_sequence",
                "description": "Generates the first n numbers of the Fibonacci sequence.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "n": {"type": "number", "description": "The number of Fibonacci numbers to generate."},
                    },
                    "required": ["n"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "is_prime",
                "description": "Checks if a number is a prime number.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "number", "description": "The number to check."},
                    },
                    "required": ["a"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "age_in_seconds",
                "description": "Calculates a person's age in seconds.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "age": {"type": "integer", "description": "The age is in years"},
                    },
                    "required": ["age"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "weight_on_planet",
                "description": "Calculates a person's weight on different planets.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "earth_weight": {"type": "number", "description": "Weight on Earth."},
                        "planet": {"type": "string", "description": "Name of the solar system planet."},
                    },
                    "required": ["earth_weight", "planet"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "random_number",
                "description": "Generates a random number within a specified range.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "min_value": {"type": "number", "description": "The minimum value of the range."},
                        "max_value": {"type": "number", "description": "The maximum value of the range."},
                    },
                    "required": ["min_value", "max_value"],
                },
            },
        },
    ]
    while True:
        response = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=messages,
            tools=tools,
            tool_choice="auto",  # auto is default, but we'll be explicit
        )
        response_message = response.choices[0].message
        print(response)
        tool_calls = response_message.tool_calls
        # Step 2: check if the model wanted to call a function

        if tool_calls:
            # Step 3: call the function
            available_functions = {
                "add": add,
                "subtract": subtract,
                "multiply": multiply,
                "divide": divide,
                "exponent": exponent,
                "root": root,
                "modulus": modulus,
                "fibonacci_sequence": fibonacci_sequence,
                "is_prime": is_prime,
                "age_in_seconds": age_in_seconds,
                "weight_on_planet": weight_on_planet,
                "random_number": random_number,
            }
            messages.append(response_message)  # extend conversation with assistant's reply

            # Step 4: send the info for each function call and function response to the model
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)

                # Handling function calls based on their specific argument requirements
                if function_name in ["add", "subtract", "multiply", "divide", "exponent", "root", "modulus"]:
                    # These functions expect two number arguments (a, b)
                    function_response = function_to_call(
                        a=function_args.get("a"),
                        b=function_args.get("b"),
                    )
                elif function_name in ["fibonacci_sequence", "is_prime", "random_number"]:
                    # These functions expect one number argument (a or n or age)
                    function_response = function_to_call(
                        a=function_args.get("a") or function_args.get("n")
                    )
                elif function_name in ["age_in_seconds"]:
                    # These functions expect multiple specific arguments
                    function_response = function_to_call(**function_args)

                elif function_name in ["weight_on_planet"]:
                    # These functions expect multiple specific arguments
                    function_response = function_to_call(**function_args)

                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": str(function_response),
                    }
                )  # extend conversation with function response
            messages.append({"role": "user", "content": "At the end of your message output 'break' if there are no "
                                                        "more calculation steps required. Only output break if you"
                                                        " have your absolute final answer for the whole problem."})
            second_response = client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=messages,
            )  # get a new response from the model where it can see the function response
            print(second_response.choices[0].message)

            if "break" in second_response.choices[0].message.content.lower():
                return second_response.choices[0].message
            else:
                messages.append(second_response.choices[0].message)


if __name__ == '__main__':
    input_message = input("Type your calculation request: ")
    run_calculator(input_message)
