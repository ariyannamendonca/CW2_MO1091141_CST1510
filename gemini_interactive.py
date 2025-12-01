from google import genai
from google.genai import types

#initalise client & conversation history
client = genai.Client(api_key="AIzaSyC1yOTdRM1jMbTjMuJhkpQotQmDqkjszQ8")

messages = [
    types.Content(
        role = "user",
        parts = [types.Part(text = "You are a helpful assistant.")]
    )
]

print("Gemini Console Chat (type 'quit' to exit)")
print("-" * 50)

while True:
    #Get user input
    user_input = input("You: ")

    #Exit condition
    if user_input == 'quit':
        print("Goodbye!")
        break

    messages.append(
        types.Content(
            role = "user",
            parts = [types.Part(text = user_input)]
            )
    )

    try:
        response = client.models.generate_content(
            model = "gemini-2.5-flash",
            contents = messages
        )

        assistant_message = response.text

        messages.append(
            types.Content(
                role="model",
                parts=[types.Part(text = assistant_message)]
            )
        )

        print(f"AI: {assistant_message}\n")

    except Exception as e:
        print(f"Error: {e}")
        break