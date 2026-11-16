
from agent import run_agent

print("Testing Unclear Input...")

try:
    result = run_agent(
        task_type="Generate Email",
        user_input="hello"
    )

    print("\nAI Response:")
    print(result)

except Exception as error:
    print("\nError:", error)
