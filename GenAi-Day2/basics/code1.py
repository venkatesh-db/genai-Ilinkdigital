
# -----------------------
# Agent
# -----------------------
def agent(task):
    if "emails" in task:
        return ["fetch_emails", "filter_urgent", "summarize"]
    else:
        return ["search_web"]

# -----------------------
# Tools
# -----------------------
def fetch_emails():
    return ["Email1: meeting tomorrow", "Email2: invoice overdue", "Email3: lunch invite"]

def filter_urgent(emails):
    return [e for e in emails if "overdue" in e or "meeting" in e]

def summarize(emails):
    return " | ".join(emails)

# -----------------------
# Chain (sequence of steps)
# -----------------------
steps = agent("Summarize my 1000 emails and highlight urgent ones")
emails = fetch_emails()
urgent_emails = filter_urgent(emails)
summary = summarize(urgent_emails)

# -----------------------
# Memory / RAG
# -----------------------
previous_summary = []  # stores context for future requests
previous_summary.append(summary)

# -----------------------
# Output
# -----------------------
print("Summary of urgent emails:", summary)
print("Memory stored:", previous_summary)
