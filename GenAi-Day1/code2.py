
'''
Flow of code 

1.  class design  
2.   4 methods: __init__, execute, cancel, __str__
3.   class has attributes: order_type, amount, price, status
4.   updating the status based on pending   executed  cancelled
5.    execution of the code 
6.   
7. 

-
'''



class TradeOrder:
    def __init__(self, order_type, amount, price):
        """
        Initialize a TradeOrder object.
        order_type: "buy" or "sell"
        amount: number of shares or units
        price: price per unit
        """
        self.order_type = order_type.lower()
        self.amount = amount
        self.price = price
        self.status = "pending"  # pending, executed, cancelled

    def execute(self):
        """
        Execute the trade order.
        """
        if self.status != "pending":
            print(f"Order cannot be executed. Current status: {self.status}")
            return
        
        # Simulate execution
        self.status = "executed"
        total_value = self.amount * self.price
        print(f"Executed {self.order_type} order for {self.amount} units at {self.price} each. Total = {total_value}")
        return total_value

    def cancel(self):
        """
        Cancel the trade order.
        """
        if self.status == "pending":
            self.status = "cancelled"
            print("Order cancelled.")
        else:
            print(f"Order cannot be cancelled. Current status: {self.status}")

    def __str__(self):
        return f"TradeOrder({self.order_type}, amount={self.amount}, price={self.price}, status={self.status})"


# ------------------------------
# Example usage
order1 = TradeOrder("buy", 100, 50.0)
print(order1)
order1.execute()
print(order1)
order1.cancel()  # cannot cancel after execution
