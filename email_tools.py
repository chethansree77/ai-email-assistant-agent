import json

from langchain_ollama import ChatOllama

from prompts import (
    generate_email_prompt,
    reply_email_prompt,
    categorize_email_prompt,
    detect_email_intent,
    smart_history_search_prompt,
)


# ==========================================
# CONNECT TO LOCAL GEMMA MODEL
# ==========================================

llm = ChatOllama(
    model="gemma3:1b",
    temperature=0,
    format="json"
)



# ==========================================
# SEND PROMPT TO GEMMA AND READ JSON RESPONSE
# ==========================================

def get_ai_response(prompt):
    # Step 1: Connect to Ollama and get AI response
    try:
        response = llm.invoke(prompt)

    except Exception as exc:
        raise RuntimeError(
            "Unable to connect to Ollama. Please make sure "
            "Ollama is running and the gemma3:1b model is "
            "available. Then try again."
        ) from exc

    # Step 2: Read response content
    content = str(response.content).strip()

    content = content.replace("```json", "").replace("```", "").strip()

    # Step 3: Find JSON content
    start = content.find("{")
    end = content.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("AI did not return valid JSON.")

    # Step 4: Convert JSON string into Python dictionary
    try:
        data = json.loads(content[start:end + 1])

    except json.JSONDecodeError as exc:
        raise ValueError(
            "AI returned incorrectly formatted JSON."
        ) from exc

    # Step 5: Validate response
    if not isinstance(data, dict):
        raise ValueError("AI response must be a JSON object.")

    return data



# ==========================================
# 1. GENERATE A NEW EMAIL
# ==========================================

def generate_email(user_instruction):
    if not user_instruction or not user_instruction.strip():
        raise ValueError("Please enter an email instruction.")
    unclear_inputs = {"hello", "hi", "hey", "write an email", "generate an email", "create an email", "help me", "email"}
    cleaned_input = user_instruction.strip().lower().rstrip(" .!?")
    if cleaned_input in unclear_inputs:
        raise ValueError("Please describe the purpose of the email. For example: Write a leave request email.")
    result = get_ai_response(generate_email_prompt(user_instruction))
    if not isinstance(result.get("subject"), str) or not result["subject"].strip():
        raise ValueError("AI did not generate a valid subject.")
    if not isinstance(result.get("body"), str) or not result["body"].strip():
        raise ValueError("AI did not generate a valid email body.")
    return result


# ==========================================
# 2. SUGGEST A REPLY
# ==========================================

def suggest_reply(incoming_email):
    if not incoming_email or not incoming_email.strip():
        raise ValueError("Please paste an incoming email.")
    result = get_ai_response(reply_email_prompt(incoming_email))
    if not isinstance(result.get("subject"), str) or not result["subject"].strip():
        raise ValueError("AI did not generate a valid subject.")
    if not isinstance(result.get("body"), str) or not result["body"].strip():
        raise ValueError("AI did not generate a valid reply.")
    return result


# ==========================================
# 3. CATEGORIZE AN EMAIL
# ==========================================

def categorize_email(email_content):
    if not email_content or not email_content.strip():
        raise ValueError("Please enter an email to categorize.")
    email_text = " ".join(email_content.lower().split())
    urgent_keywords = [
        "server is down", "server down", "servers are down", "system outage",
        "service outage", "complete outage", "unable to access",
        "cannot access the application", "can't access the application",
        "business operations are affected", "business operations affected",
        "business operations are interrupted", "service disruption",
        "security breach", "data breach", "critical failure",
        "immediate attention", "resolve this issue immediately",
        "production system is down", "application is unavailable", "network is down"
    ]
    if any(keyword in email_text for keyword in urgent_keywords):
        return {"category": "Urgent", "reason": "The email describes a critical issue that may interrupt business operations and requires immediate attention."}
    personal_keywords = ["birthday invitation", "birthday party", "family function", "family gathering", "wedding invitation", "personal appointment", "holiday with family"]
    if any(keyword in email_text for keyword in personal_keywords):
        return {"category": "Personal", "reason": "The email discusses a personal or family-related event."}
    result = get_ai_response(categorize_email_prompt(email_content))
    if result.get("category") not in ["Work", "Personal", "Urgent"]:
        raise ValueError("AI returned an unsupported category.")
    if not isinstance(result.get("reason"), str) or not result["reason"].strip():
        raise ValueError("AI did not provide a valid reason.")
    return result


# ==========================================
# 4. SMART EMAIL INTENT DETECTION
# ==========================================

def detect_intent(user_input):
    if not user_input or not user_input.strip():
        raise ValueError("Please enter your instruction.")
    result = get_ai_response(detect_email_intent(user_input))
    allowed_tasks = ["Generate Email", "Suggest Reply", "Categorize Email"]
    task_type = result.get("task_type")
    if task_type not in allowed_tasks:
        raise ValueError("AI returned an invalid email action.")
    reason = result.get("reason")
    if not isinstance(reason, str) or not reason.strip():
        reason = f"The user requested: {task_type}."
    return {"task_type": task_type, "reason": reason}


# ==========================================
# 5. GEMMA-POWERED SMART HISTORY SEARCH
# ==========================================

def smart_search_saved_drafts(user_query, drafts):
    if not user_query or not user_query.strip():
        raise ValueError("Describe the email you want to find.")
    if not drafts:
        return {"matching_ids": [], "reason": "There are no saved drafts to search."}

    # Send only relevant database fields to the model. IDs are retained so
    # the model can point to real records; the app validates them afterwards.
    records = []
    valid_ids = set()
    for draft in drafts:
        record = {
            "id": int(draft["id"]),
            "subject": str(draft["subject"] or ""),
            "body": str(draft["body"] or "")[:2500],
            "category": str(draft["category"] or ""),
            "task_type": str(draft["task_type"] or ""),
            "created_at": str(draft["created_at"] or ""),
        }
        records.append(record)
        valid_ids.add(record["id"])

    result = get_ai_response(smart_history_search_prompt(user_query, json.dumps(records, ensure_ascii=False)))
    raw_ids = result.get("matching_ids", [])
    if not isinstance(raw_ids, list):
        raise ValueError("Gemma returned an invalid matching_ids list.")

    matching_ids = []
    for item in raw_ids:
        try:
            draft_id = int(item)
        except (TypeError, ValueError):
            continue
        if draft_id in valid_ids and draft_id not in matching_ids:
            matching_ids.append(draft_id)

    reason = result.get("reason", "Gemma searched the saved drafts for related emails.")
    if not isinstance(reason, str) or not reason.strip():
        reason = "Gemma searched the saved drafts for related emails."
    return {"matching_ids": matching_ids[:10], "reason": reason}
