
#Multi-Agent Orchestration

class ResearchAgent:
    def run(self, topic):
        return f"Collected recent insights on {topic}."

class AnalysisAgent:
    def run(self, data):
        return f"Analyzed data: {data}. Found 3 major trends."

class ReportAgent:
    def run(self, summary):
        return f"Generated report based on: {summary}"

# Orchestration
research = ResearchAgent().run("solar energy usage in India")
analysis = AnalysisAgent().run(research)
report = ReportAgent().run(analysis)

print(report)
