from email_tools import (
    generate_email,
    suggest_reply,
    categorize_email,
    detect_intent,
    smart_search_saved_drafts,
)


def run_agent(task_type, user_input):
    if not user_input or not user_input.strip():
        raise ValueError("Please enter an instruction or email.")
    if task_type == "Generate Email":
        result = generate_email(user_input)
    elif task_type == "Suggest Reply":
        result = suggest_reply(user_input)
    elif task_type == "Categorize Email":
        result = categorize_email(user_input)
    else:
        raise ValueError("Please select a valid task.")
    return result


def run_agent_auto(user_input):
    if not user_input or not user_input.strip():
        raise ValueError("Please enter an instruction or email.")
    intent_result = detect_intent(user_input)
    task_type = intent_result["task_type"]
    result = run_agent(task_type, user_input)
    return {"task_type": task_type, "reason": intent_result["reason"], "result": result}


def run_smart_history_search(user_query, drafts):
    """Find saved drafts using the user's natural-language description."""
    return smart_search_saved_drafts(user_query, drafts)
