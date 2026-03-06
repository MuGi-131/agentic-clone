import os
import argparse
import config
from dotenv import load_dotenv
from google import genai
from google.genai import types
from prompts import system_prompt
from call_function import available_functions, call_function


def main():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    model = "gemini-2.5-flash"

    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User Prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]

    response = client.models.generate_content(
        model=model,
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions], system_instruction=system_prompt, temperature=0
        ),
    )

    if response.usage_metadata is None:
        prompt_token = 0
        response_token = 0
        raise RuntimeError("err my guy")
    else:
        prompt_token = response.usage_metadata.prompt_token_count
        response_token = response.usage_metadata.thoughts_token_count

    if args.verbose:
        print(f"User prompt: {args.user_prompt}")
        print(f"Prompt tokens: {prompt_token}")
        print(f"Response tokens: {response_token}")
        print("Response:")

    if not response.function_calls:
        print(response.text)
    else:
        function_results = []
        for function_call in response.function_calls:
            function_call_result = call_function(function_call, args.verbose)
            if not function_call_result.parts:
                Exception(f"Error: returned empty parts")
            response = function_call_result.parts[0].function_response.response
            if not response:
                Exception(f"Error: reponse empty")

            if args.verbose:
                print(f"-> {function_call_result.parts[0].function_response.response}")

            function_results.append(function_call_result.parts[0])


if __name__ == "__main__":
    main()
