
from agent import run_agent

print("Testing Work Email Categorization...")

email_content = """
Subject: Project Meeting

Dear Team,

We have scheduled a project review meeting
for Monday at 10 AM.

Please prepare your progress updates
before the meeting.

Regards,
Project Manager
"""

try:
    result = run_agent("Categorize Email", email_content)

    print("\nCategory:")
    print(result["category"])

    print("\nReason:")
    print(result["reason"])

except Exception as error:
    print("\nError:", error)
