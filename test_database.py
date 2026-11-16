
import database

# Initialize the database
database.init_db()

print("Database created successfully!")

# Save a sample email
draft_id = database.save_draft(
    task_type="Generate Email",
    subject="Sick Leave Request",
    body="I am feeling unwell and request one day of leave.",
    category="Work"
)

print("Draft saved successfully!")
print("Draft ID:", draft_id)

# Retrieve all saved drafts
drafts = database.get_all_drafts()

print("\nSaved Drafts:")

for draft in drafts:
    print(dict(draft))
