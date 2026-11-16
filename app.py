import re
import html as html_lib
import streamlit as st
from agent import run_agent, run_agent_auto, run_smart_history_search
import database
# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="AI Email Assistant Agent",
    page_icon="📧",
    layout="wide"
)
# ==========================================
# 2. INITIALIZE DATABASE AND CSS
# ==========================================
database.init_db()
with open("assets/style.css", "r", encoding="utf-8") as css_file:
    st.markdown(
        f"<style>{css_file.read()}</style>",
        unsafe_allow_html=True
    )
st.markdown(
    """
    <style>
    .history-section-heading {
        background: #f5f5f5;
        color: #4c1d95;
        font-size: 27px;
        font-weight: 750;
        padding: 14px 18px;
        border-radius: 10px 10px 0 0;
        margin: 12px 0 0 0;
    }
    .history-section-description {
        background: #f5f5f5;
        color: #64748b;
        font-size: 15px;
        padding: 10px 18px 14px 18px;
        border-radius: 0 0 10px 10px;
        margin: 0 0 16px 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================
# 3. APPLICATION HEADING
# ==========================================
st.markdown("""
<div class="hero-banner">
    <h1>📧 AI Email Assistant Agent</h1>
    <p>Write smarter emails, generate intelligent replies,
    and organize your inbox with AI.</p>
</div>
""", unsafe_allow_html=True)
# ==========================================
# 4. DASHBOARD STATISTICS
# ==========================================
drafts = database.get_all_drafts()
total_drafts = len(drafts)
generated_emails = sum(
    1 for draft in drafts
    if draft["task_type"] == "Generate Email"
)
generated_replies = sum(
    1 for draft in drafts
    if draft["task_type"] == "Suggest Reply"
)
categorized_emails = sum(
    1 for draft in drafts
    if draft["task_type"] == "Categorize Email"
)
urgent_emails = sum(
    1 for draft in drafts
    if draft["category"] == "Urgent"
)
work_emails = sum(
    1 for draft in drafts
    if draft["category"] == "Work"
)
personal_emails = sum(
    1 for draft in drafts
    if draft["category"] == "Personal"
)
st.divider()
st.subheader("📊 Dashboard Overview")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📧 Total Drafts", total_drafts)
with col2:
    st.metric("✍️ Generated Emails", generated_emails)
with col3:
    st.metric("↩️ Generated Replies", generated_replies)
with col4:
    st.metric("📂 Categorized Emails", categorized_emails)
# Category statistics
st.markdown("### 📌 Email Category Statistics")
cat1, cat2, cat3 = st.columns(3)
with cat1:
    st.metric("🚨 Urgent", urgent_emails)
with cat2:
    st.metric("💼 Work", work_emails)
with cat3:
    st.metric("💜 Personal", personal_emails)
st.divider()
# ==========================================
# 5. SELECT EMAIL ACTION
# ==========================================
st.markdown(
    '<div class="history-section-heading">✨ What would you like to do?</div>',
    unsafe_allow_html=True
)
selection_mode = st.radio(
    "Choose Selection Mode",
    ["Manual Selection", "AI Auto Detection"],
    horizontal=True,
    key="selection_mode"
)
if selection_mode == "Manual Selection":
    task_type = st.radio(
        "Choose an action",
        [
            "Generate Email",
            "Suggest Reply",
            "Categorize Email"
        ],
        horizontal=True,
        key="email_action"
    )
else:
    task_type = "AI Auto Detection"
# ==========================================
# 6. USER INPUT
# ==========================================
if selection_mode == "AI Auto Detection":
    input_label = "Describe what you want the AI Email Assistant to do"
    input_placeholder = (
        "Example: Write a leave request email, "
        "reply to a meeting invitation, or categorize an email..."
    )
elif task_type == "Generate Email":
    input_label = "Describe the email you want to write"
    input_placeholder = (
        "Example: Write a professional leave request "
        "for two days next week..."
    )
elif task_type == "Suggest Reply":
    input_label = "Paste the incoming email"
    input_placeholder = (
        "Paste the complete email here, including "
        "the subject and message..."
    )
else:
    input_label = "Paste the email you want to categorize"
    input_placeholder = (
        "Paste an email to identify whether it is "
        "Work, Personal, or Urgent..."
    )
user_input = st.text_area(
    input_label,
    placeholder=input_placeholder,
    height=180,
    key="email_user_input"
)
# ==========================================
# 7. GENERATE BUTTON
# ==========================================
if st.button("✨ Generate", use_container_width=True):
    if not user_input.strip():
        st.warning("Please enter an instruction or email.")
    else:
        try:
            with st.spinner("Gemma is processing your request..."):
                if selection_mode == "AI Auto Detection":
                    auto_result = run_agent_auto(user_input)
                    selected_task = auto_result["task_type"]
                    result = auto_result["result"]
                    st.info(
                        f"🤖 AI detected action: {selected_task}"
                    )
                    st.write(
                        f"**Reason:** {auto_result['reason']}"
                    )
                else:
                    selected_task = task_type
                    result = run_agent(
                        selected_task,
                        user_input
                    )
            if not isinstance(result, dict):
                raise ValueError("AI returned an invalid result.")
            st.session_state["result"] = result
            st.session_state["task_type"] = selected_task
            st.session_state["source_email"] = user_input
            # Reset save status for new result
            st.session_state["categorized_saved"] = False
            if selected_task in [
                "Generate Email",
                "Suggest Reply"
            ]:
                st.session_state["edited_subject"] = result["subject"]
                st.session_state["edited_body"] = result["body"]
            st.success("AI response generated successfully!")
        except Exception as error:
            st.session_state.pop("result", None)
            st.session_state.pop("task_type", None)
            st.session_state.pop("categorized_saved", None)
            st.error(f"Something went wrong: {error}")
# ==========================================
# 8. DISPLAY AI GENERATED RESULT
# ==========================================
if "result" in st.session_state:
    result = st.session_state["result"]
    selected_task = st.session_state["task_type"]
    source_email = st.session_state.get(
        "source_email",
        user_input
    )
    st.divider()
    st.subheader("✨ AI Generated Result")
    # --------------------------------------
    # GENERATE EMAIL / SUGGEST REPLY
    # --------------------------------------
    if selected_task in ["Generate Email", "Suggest Reply"]:
        recipient = st.text_input(
            "Recipient Email Address",
            placeholder="example@gmail.com",
            key="recipient_email"
        )
        # Email validation
        email_pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        recipient_valid = bool(
            re.fullmatch(email_pattern, recipient.strip())
        )
        if recipient.strip():
            if recipient_valid:
                st.success("Email address format looks valid.")
            else:
                st.warning("Please enter a valid email address.")
        # Editable subject
        subject = st.text_input(
            "Email Subject",
            key="edited_subject"
        )
        # Editable body
        body = st.text_area(
            "Email Body",
            height=250,
            key="edited_body"
        )
        st.divider()
        # Save draft - prevent saving the same email more than once
        if st.button("💾 Save Draft"):
            clean_subject = subject.strip()
            clean_body = body.strip()
            if not clean_subject or not clean_body:
                st.warning("Subject and body cannot be empty.")
            elif database.draft_exists(
                task_type=selected_task,
                subject=clean_subject,
                body=clean_body,
                category=None
            ):
                st.warning(
                    "This exact email draft is already saved. It was not saved again."
                )
            else:
                database.save_draft(
                    task_type=selected_task,
                    subject=clean_subject,
                    body=clean_body
                )
                st.success("Your draft has been saved successfully!")
                st.rerun()
    # --------------------------------------
    # CATEGORIZE EMAIL
    # --------------------------------------
    elif selected_task == "Categorize Email":
        category = result.get("category", "Unknown")
        reason = result.get(
            "reason",
            "No explanation provided."
        )
        if category == "Urgent":
            st.error(f"🚨 Category: {category}")
        elif category == "Work":
            st.info(f"💼 Category: {category}")
        elif category == "Personal":
            st.success(f"💜 Category: {category}")
        else:
            st.warning(f"Category: {category}")
        st.write("**Reason:**")
        st.write(reason)
        st.divider()
        # Save categorized email
        if st.session_state.get("categorized_saved", False):
            st.success(
                "✅ This categorized email is already saved!"
            )
        else:
            if st.button(
                "💾 Save Categorized Email",
                use_container_width=True
            ):
                email_subject = "Categorized Email"
                # Extract email subject
                for line in source_email.splitlines():
                    if line.strip().lower().startswith("subject:"):
                        email_subject = line.split(":", 1)[1].strip()
                        break
                try:
                    database.save_draft(
                        task_type="Categorize Email",
                        subject=email_subject,
                        body=source_email.strip(),
                        category=category
                    )
                    st.session_state["categorized_saved"] = True
                    st.success(
                        "Categorized email saved successfully!"
                    )
                    st.rerun()
                except Exception as error:
                    st.error(
                        f"Unable to save categorized email: {error}"
                    )
# ==========================================
# 9. SMART EMAIL HISTORY
# ==========================================
st.markdown(
    """
    <div class="history-section-heading">📂 Smart Email History</div>
    <div class="history-section-description">Find saved emails using words you remember, browse recent emails, and filter by category.</div>
    """,
    unsafe_allow_html=True
)

drafts = database.get_all_drafts()
total_drafts = len(drafts)
st.metric("📂 Total Saved Drafts", total_drafts)
if not drafts:
    st.info("You haven't saved any emails yet. Generate and save an email to see it here.")
else:
    # Recent emails - explicit HTML cards provide reliable solid backgrounds.
    st.subheader("🕒 Recent Emails")
    recent_drafts = database.get_recent_drafts(limit=5)
    if recent_drafts:
        recent_columns = st.columns(min(3, len(recent_drafts)))
        for index, draft in enumerate(recent_drafts):
            with recent_columns[index % len(recent_columns)]:
                subject_text = html_lib.escape(str(draft["subject"] or "Untitled email"))
                task_text = html_lib.escape(str(draft["task_type"] or "Email"))
                created_text = html_lib.escape(str(draft["created_at"] or ""))
                category_text = html_lib.escape(str(draft["category"] or ""))
                preview_text = " ".join(str(draft["body"] or "").split())
                preview_text = html_lib.escape(
                    preview_text[:150] + ("…" if len(preview_text) > 150 else "")
                )
                category_html = (
                    f'<div class="recent-email-category">Category: {category_text}</div>'
                    if category_text else ""
                )
                card_html = (
                    '<div class="recent-email-card">'
                    f'<div class="recent-email-subject">{subject_text}</div>'
                    f'<div class="recent-email-meta">Draft #{int(draft["id"])} · {task_text} · {created_text}</div>'
                    f'{category_html}'
                    f'<div class="recent-email-preview">{preview_text}</div>'
                    '</div>'
                )
                st.markdown(card_html, unsafe_allow_html=True)
    st.divider()
    st.markdown(
        """
            <div class="history-section-heading">✨ Find an Email with Gemma AI</div>
            <div class="history-section-description">Describe what you remember. You do not need the exact subject or wording.</div>
            """,
            unsafe_allow_html=True
        )

    with st.form("gemma_smart_history_form"):
        ai_history_query = st.text_input(
            "What email are you trying to find?",
            placeholder="Example: Find the email where I requested leave from college...",
            key="gemma_history_query"
        )
        ai_search_clicked = st.form_submit_button("🧠 Search with Gemma", use_container_width=True)
    if ai_search_clicked:
        if not ai_history_query.strip():
            st.warning("Please describe the email you want to find.")
        else:
            try:
                with st.spinner("Gemma is understanding your description and searching saved emails..."):
                    ai_result = run_smart_history_search(ai_history_query, drafts)
                st.session_state["gemma_history_match_ids"] = ai_result["matching_ids"]
                st.session_state["gemma_history_reason"] = ai_result["reason"]
                st.session_state["gemma_history_query_used"] = ai_history_query
            except Exception as error:
                st.error(f"Gemma Smart Search could not complete: {error}")
                st.info("You can still use the regular keyword search below.")
    if "gemma_history_match_ids" in st.session_state:
        st.markdown("#### 🤖 Gemma Search Results")
        st.caption(st.session_state.get("gemma_history_reason", ""))
        draft_lookup = {int(item["id"]): item for item in drafts}
        ai_matches = [
            draft_lookup[item_id]
            for item_id in st.session_state["gemma_history_match_ids"]
            if item_id in draft_lookup
        ]
        if ai_matches:
            st.success(f"Gemma found {len(ai_matches)} possible matching email(s).")
            for match in ai_matches:
                with st.expander(f"📧 {match['subject']} | Draft #{match['id']}"):
                    st.caption(f"{match['task_type']} · {match['category'] or 'Uncategorized'} · {match['created_at']}")
                    st.write(match["body"])
                    st.caption("To edit or delete this email, find its full entry in the history list below.")
        else:
            st.info("No confident match found. Try another description or use the keyword search below.")
    st.divider()
    st.markdown(
        '<div class="history-section-heading">🔎 Search and Filter Emails</div>',
        unsafe_allow_html=True
    )
    st.caption(
        "Use keyword search and filters as a fallback, or use Gemma above to search "
        "by describing the email's purpose even when you do not remember exact wording."
    )
    search_query = st.text_input(
        "🔎 What do you remember about the email?",
        placeholder="Example: Python job application, leave request, HR, meeting...",
        key="smart_history_search"
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        type_options = ["All Types"] + sorted({
            draft["task_type"] for draft in drafts if draft["task_type"]
        })
        type_filter = st.selectbox("Email Type", type_options, key="smart_history_type")
    with col2:
        category_values = sorted({
            draft["category"] for draft in drafts if draft["category"]
        })
        category_filter = st.selectbox(
            "Category",
            ["All Categories"] + category_values,
            key="smart_history_category"
        )
    with col3:
        sort_option = st.selectbox(
            "Sort By",
            ["Newest First", "Oldest First", "Subject A–Z"],
            key="smart_history_sort"
        )
    if st.button("↩️ Clear Search and Filters", key="clear_history_filters"):
        for key in (
            "smart_history_search",
            "smart_history_type",
            "smart_history_category",
            "smart_history_sort"
        ):
            st.session_state.pop(key, None)
        st.rerun()
    if search_query.strip():
        try:
            filtered_drafts = database.search_drafts(search_query.strip())
        except Exception as error:
            st.error(f"Search failed: {error}")
            filtered_drafts = []
    else:
        filtered_drafts = drafts.copy()
    if type_filter != "All Types":
        filtered_drafts = [
            draft for draft in filtered_drafts if draft["task_type"] == type_filter
        ]
    if category_filter != "All Categories":
        filtered_drafts = [
            draft for draft in filtered_drafts if draft["category"] == category_filter
        ]
    if sort_option == "Oldest First":
        filtered_drafts = sorted(filtered_drafts, key=lambda item: item["id"])
    elif sort_option == "Subject A–Z":
        filtered_drafts = sorted(
            filtered_drafts, key=lambda item: (item["subject"] or "").lower()
        )
    else:
        filtered_drafts = sorted(
            filtered_drafts, key=lambda item: item["id"], reverse=True
        )
    st.caption(f"Showing {len(filtered_drafts)} of {total_drafts} saved emails.")
    if not filtered_drafts:
        st.info("No matching emails found. Try another word or clear the filters.")
    else:
        for draft in filtered_drafts:
            draft_id = draft["id"]
            subject = draft["subject"]
            body = draft["body"]
            task_type = draft["task_type"]
            created_at = draft["created_at"]
            category = draft["category"]
            if task_type == "Generate Email":
                task_label = "✉️ Generated Email"
            elif task_type == "Suggest Reply":
                task_label = "↩️ Email Reply"
            elif task_type == "Categorize Email":
                task_label = "📂 Categorized Email"
            else:
                task_label = f"📁 {task_type}"
            with st.expander(
                f"✉️ {subject} | Draft #{draft_id}",
                expanded=st.session_state.get(f"confirm_delete_{draft_id}", False)
            ):
                st.markdown(
                    f"""
                    <div style="
                        background:linear-gradient(120deg,#ede9fe,#f3e8ff);
                        border:1px solid #c4b5fd;
                        border-left:5px solid #7c3aed;
                        padding:14px 18px;border-radius:10px;margin:12px 0;
                        color:#4c1d95;font-size:14px;font-weight:600;line-height:2;">
                        {task_label} &nbsp; | &nbsp; Draft ID: {draft_id}<br>
                        🕒 Saved: {created_at}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                if category:
                    st.info(f"📌 Category: {category}")
                st.markdown("### 📝 Saved Email")
                st.text_input(
                    "Saved Subject", value=subject, disabled=True,
                    key=f"history_subject_{draft_id}", label_visibility="collapsed"
                )
                st.text_area(
                    "Saved Email Body", value=body, height=150, disabled=True,
                    key=f"history_body_{draft_id}", label_visibility="collapsed"
                )
                st.divider()
                st.markdown("### ✏️ Edit Existing Draft")
                edited_subject = st.text_input(
                    "Edit Email Subject", value=subject, key=f"edit_subject_{draft_id}"
                )
                edited_body = st.text_area(
                    "Edit Email Body", value=body, height=200,
                    key=f"edit_body_{draft_id}"
                )
                if st.button(
                    "💾 Update Draft", key=f"update_draft_{draft_id}",
                    use_container_width=True
                ):
                    if not edited_subject.strip() or not edited_body.strip():
                        st.warning("Subject and body cannot be empty.")
                    else:
                        try:
                            updated_rows = database.update_draft(
                                draft_id=draft_id,
                                subject=edited_subject.strip(),
                                body=edited_body.strip()
                            )
                            if updated_rows > 0:
                                st.success("Draft updated successfully!")
                                st.rerun()
                            else:
                                st.error("Draft could not be updated.")
                        except Exception as error:
                            st.error(f"Unable to update draft: {error}")
                st.divider()
                if st.button(
                    "🗑️ Delete Draft", key=f"delete_draft_{draft_id}",
                    use_container_width=True
                ):
                    st.session_state[f"confirm_delete_{draft_id}"] = True
                    st.rerun()
                if st.session_state.get(f"confirm_delete_{draft_id}", False):
                    st.warning(f"Are you sure you want to delete Draft #{draft_id}?")
                    confirm_col, cancel_col = st.columns(2)
                    with confirm_col:
                        if st.button(
                            "✅ Yes, Delete", key=f"confirm_yes_{draft_id}",
                            use_container_width=True
                        ):
                            try:
                                deleted_rows = database.delete_draft(draft_id)
                                if deleted_rows > 0:
                                    st.session_state.pop(f"confirm_delete_{draft_id}", None)
                                    st.success("Draft deleted successfully!")
                                    st.rerun()
                                else:
                                    st.error("Draft could not be deleted.")
                            except Exception as error:
                                st.error(f"Unable to delete draft: {error}")
                    with cancel_col:
                        if st.button(
                            "❌ Cancel", key=f"confirm_cancel_{draft_id}",
                            use_container_width=True
                        ):
                            st.session_state.pop(f"confirm_delete_{draft_id}", None)
                            st.rerun()
                st.caption(f"Draft #{draft_id} is stored in your SQLite database.")
# ==========================================
# 12. FOOTER
# ==========================================
st.divider()
st.divider()
st.caption(
    "📧 AI Email Assistant Agent | Powered by Python, Streamlit and Gemma"
)
