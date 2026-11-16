
from agent import run_agent

print("Testing Empty Input Validation...")

try:
    result = run_agent(
        task_type="Generate Email",
        user_input=""
    )

    print("Unexpected result:", result)

except ValueError as error:
    print("Validation Passed!")
    print("Error Message:", error)
