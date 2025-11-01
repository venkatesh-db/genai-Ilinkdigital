
# -----------------------
# Agent
# -----------------------
def agent(task):
    if "KYC" in task or "AML" in task:
        return ["fetch_bank_rules", "summarize_rules"]
    else:
        return ["search_web"]

# -----------------------
# Tools
# -----------------------
def fetch_bank_rules():
    return ["KYC: verify identity to prevent fraud.", 
            "AML: monitor transactions for suspicious activity."]

def summarize_rules(rules):
    return " ".join(rules)

# -----------------------
# Chain
# -----------------------
steps = agent("Explain KYC and AML for new customers")
rules = fetch_bank_rules()
summary = summarize_rules(rules)

# -----------------------
# Memory / RAG
# -----------------------
previous_queries = []  # context storage
previous_queries.append(summary)

# -----------------------
# Output
# -----------------------
print("Summary:", summary)
print("Memory stored:", previous_queries)
