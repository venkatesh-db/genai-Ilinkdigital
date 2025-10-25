

'''
Flow of code 

1.  import time and functools modules    
2.  function design with func 
3.  function return another function as wrapper
4.  function arguments with *args and **kwargs
5.  try block call functions  result end time calculation
6.  class design with method init and  execute decorated with func
7.  class attributes order_type amount price status
8.  execute method with status check simulated execution
9.  execution of the code

-
'''


import time
import functools

# ------------------------------
# Decorator for logging
def transaction_logger(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        order = args[0] if args else None
        start_time = time.time()
        try:
            print(f"[LOG] Starting transaction for order: {order}")
            result = func(*args, **kwargs)
            end_time = time.time()
            print(f"[LOG] Transaction executed successfully in {end_time - start_time:.4f} seconds")
            return result
        except Exception as e:
            end_time = time.time()
            print(f"[ERROR] Transaction failed after {end_time - start_time:.4f} seconds")
            print(f"[ERROR] {e}")
            return None
    return wrapper

# ------------------------------
# Example usage with TradeOrder class
class TradeOrder:
    def __init__(self, order_type, amount, price):
        self.order_type = order_type.lower()
        self.amount = amount
        self.price = price
        self.status = "pending"

    @transaction_logger
    def execute(self):
        if self.status != "pending":
            raise Exception(f"Cannot execute order. Current status: {self.status}")
        # Simulate execution
        time.sleep(0.5)  # simulate processing time
        self.status = "executed"
        total_value = self.amount * self.price
        print(f"Executed {self.order_type} order for {self.amount} units at {self.price} each. Total = {total_value}")
        return total_value

    def __str__(self):
        return f"TradeOrder({self.order_type}, amount={self.amount}, price={self.price}, status={self.status})"


# ------------------------------
# Test
order1 = TradeOrder("buy", 100, 50.0)
order1.execute()

order2 = TradeOrder("sell", 50, 30.0)
order2.status = "executed"  # simulate already executed
order2.execute()  # will log an error
