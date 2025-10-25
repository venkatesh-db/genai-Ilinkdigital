
from abc import ABC, abstractmethod

# --- Base Runnable Interface ---
class Runnable(ABC):
    @abstractmethod
    def invoke(self, input_data):
        pass


# --- Polymorphic Classes ---
class SquareRunnable(Runnable):
    def invoke(self, input_data):
        try:
            number = float(input_data)
            return number ** 2
        except ValueError:
            return f"[SquareRunnable] Can't square non-numeric input: '{input_data}'"


class LangChainRunnable(Runnable):
    def invoke(self, input_data):
        # Simulating LangChain-style text processing
        return f"[LangChainRunnable] Processed '{input_data}' with AI reasoning chain"


# --- Function to Execute All Runnables ---
def execute_runnables(runnables, input_data):
    for r in runnables:
        print(f"{r.__class__.__name__} → {r.invoke(input_data)}")


# --- Polymorphism in Action ---
if __name__ == "__main__":
    runnables = [SquareRunnable(), LangChainRunnable()]

    print("Case 1: Numeric Input")
    execute_runnables(runnables, 5)

    print("\nCase 2: Text Input")
    execute_runnables(runnables, "ai agent")
