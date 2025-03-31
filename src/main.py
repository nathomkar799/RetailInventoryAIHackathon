# Retail Inventory Optimization - Multi-Agent System with Multi-Day Simulation
import ollama
import random

class DemandPredictionAgent:
    def __init__(self):
        self.model = "tinyllama"

    def predict_demand(self, sales_data):
        prompt = f"Given daily sales {sales_data} for Product A, predict the next day's sales as a number."
        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        # Extract a number from the response (basic parsing)
        text = response["message"]["content"]
        try:
            prediction = int(''.join(filter(str.isdigit, text.split()[0])))
        except (IndexError, ValueError):
            prediction = sum(sales_data) // len(sales_data)  # Fallback: average
        return prediction

class StoreAgent:
    def __init__(self, initial_stock):
        self.stock = initial_stock
        self.demand_agent = DemandPredictionAgent()
        self.holding_cost_per_unit = 1  # $1 per unit per day
        self.current_predicted_demand = 0  # Track the demand used for ordering

    def check_inventory(self, sales_data):
        self.current_predicted_demand = self.demand_agent.predict_demand(sales_data)
        print(f"Store: Predicted demand for tomorrow is {self.current_predicted_demand} units.")
        buffer = 2  # Add a buffer to avoid stockouts
        desired_stock = self.current_predicted_demand + buffer
        if self.stock < desired_stock:
            units_needed = desired_stock - self.stock
            print(f"Store: Stock ({self.stock}) is low. Requesting {units_needed} units.")
            return units_needed
        else:
            print(f"Store: Stock ({self.stock}) is sufficient.")
            return 0

    def receive_stock(self, units):
        self.stock += units
        print(f"Store: Received {units} units. New stock: {self.stock}")

    def process_day(self, actual_sales):
        self.stock = max(0, self.stock - actual_sales)
        print(f"Store: Sold {actual_sales} units. New stock: {self.stock}")

    def calculate_holding_cost(self):
        # Holding cost for all stock held overnight
        cost = self.stock * self.holding_cost_per_unit
        print(f"Store: Holding {self.stock} units overnight, holding cost: ${cost}")
        return cost

class WarehouseAgent:
    def __init__(self, initial_stock):
        self.stock = initial_stock

    def fulfill_request(self, units_needed):
        if self.stock >= units_needed:
            self.stock -= units_needed
            print(f"Warehouse: Sending {units_needed} units. Remaining stock: {self.stock}")
            return units_needed
        else:
            print(f"Warehouse: Insufficient stock ({self.stock}). Sending all available.")
            sent = self.stock
            self.stock = 0
            return sent

# Main simulation
if __name__ == "__main__":
    print("Starting Retail Inventory AI System...")
    
    # Hardcoded data (temporary)
    historical_sales = [10, 15, 12, 8]
    
    # Initialize agents
    store = StoreAgent(initial_stock=5)
    warehouse = WarehouseAgent(initial_stock=50)  # Increased stock to ensure availability
    
    # Simulate 5 days
    total_holding_cost = 0
    num_days = 5
    
    for day in range(1, num_days + 1):
        print(f"\n--- Day {day} ---")
        print(f"Historical sales: {historical_sales}")
        
        # Predict demand and check inventory
        units_needed = store.check_inventory(historical_sales)
        if units_needed > 0:
            units_sent = warehouse.fulfill_request(units_needed)
            store.receive_stock(units_sent)
        
        # Simulate actual sales (lower than predicted to create excess)
        actual_sales = max(1, store.current_predicted_demand + random.randint(-4, 0))
        store.process_day(actual_sales)
        
        # Calculate holding cost after sales
        holding_cost = store.calculate_holding_cost()
        total_holding_cost += holding_cost
        
        # Update historical sales (keep last 4 days)
        historical_sales.append(actual_sales)
        historical_sales = historical_sales[-4:]
    
    # Final summary
    print("\n--- Simulation Summary ---")
    print(f"Final store stock: {store.stock} units")
    print(f"Final warehouse stock: {warehouse.stock} units")
    print(f"Total holding cost: ${total_holding_cost}")
    print("Simulation complete.")