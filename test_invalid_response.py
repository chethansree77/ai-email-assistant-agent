
import email_tools
from types import SimpleNamespace

# Save the original Ollama connection
original_llm = email_tools.llm

# Simulate an AI response that is not valid JSON
email_tools.llm = SimpleNamespace(
    invoke=lambda prompt: SimpleNamespace(
        content="This is not a valid JSON response"
    )
)

try:
    email_tools.get_ai_response("Test prompt")

except ValueError as error:
    print("TEST PASSED!")
    print("Invalid response handled correctly:")
    print(error)

except Exception as error:
    print("TEST FAILED!")
    print(error)

else:
    print("TEST FAILED! Invalid response was accepted.")

finally:
    # Restore the original Ollama connection
    email_tools.llm = original_llm
