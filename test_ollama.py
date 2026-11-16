
from langchain_ollama import ChatOllama

# Connect to our local Gemma model
llm = ChatOllama(
    model="gemma3:1b",
    temperature=0.3
)

# Send a test message
response = llm.invoke(
    "Write one short professional sentence thanking a manager."
)

# Display the AI response
print("Gemma Response:")
print(response.content)
