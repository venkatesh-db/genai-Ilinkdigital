
import functools
from datetime import datetime

# Basic decorator
def log_transaction(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[{datetime.now()}] Transaction started: {func.__name__}")
        result = func(*args, **kwargs)
        print(f"[{datetime.now()}] Transaction completed: {func.__name__}")
        return result
    return wrapper

# Example usage
@log_transaction
def transfer(amount, sender, receiver):
    print(f"Transferring ${amount} from {sender} to {receiver}")
    return f"${amount} transferred"

# Run
transfer(500, "smiles", "hero")
