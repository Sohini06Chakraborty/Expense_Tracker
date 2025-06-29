"""
Expense Tracker Program
Allows users to add, edit, delete, view, and visualize expenses.
Data is stored persistently in a JSON file.
"""
from datetime import datetime
from collections import defaultdict
import json
import matplotlib.pyplot as plt

class Expense:
    """Represents a single expense with amount, category, and date."""
    def __init__(self, amount, category, date):
        self.amount = amount
        self.category = category
        self.date = date
    def __str__(self):
        return f"Category: {self.category}, Amount: {self.amount}, Date: {self.date}"
    def to_dict(self):
        return {
            'amount': self.amount,
            'category': self.category,
            'date': self.date
        }
    @staticmethod
    def from_dict(data):
        return Expense(data['amount'], data['category'], data['date'])

class ExpenseTracker:
    """Manages expenses with options to add, edit, delete, view summaries, and plot graphs."""
    def __init__(self):
        self.expenses = [] # List to store all expense objects
    def validate_date(self, date_str):
        """Validates if the provided date string is in YYYY-MM-DD format."""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    def add_expenses(self):
        """Adds a new expense entry after taking validated input from the user."""
        try:
            amount = float(input("Enter the amount of the expense: ").strip())
            category = input("Enter the category of the expense: ").strip()
            date = input("Enter date (YYYY-MM-DD) or press Enter for today: ").strip()
            if not date:
                date = datetime.now().strftime("%Y-%m-%d")
            if not self.validate_date(date):
                print("Invalid date format. Please use YYYY-MM-DD.")
                return
            expense = Expense(amount, category, date)
            self.expenses.append(expense) # Add expense to list
            print(f"Expense of amount {amount} added successfully in {category} category on {date}.")
            self.save_to_file()
        except ValueError:
            print("Invalid input, please enter a numeric amount.")
    def view_summary(self):
        """Provides options to view total spending by category, total, or over time."""
        if not self.expenses:
            print("No expenses recorded yet.")
            return
        try:
            choice = int(input(
                "\nEnter:\n"
                "1 for Total spending for a specific category\n"
                "2 for Total overall spending\n"
                "3 for Spending over time\n"
                "Your choice: ").strip())
        except ValueError:
            print("Invalid input, please enter a number.")
            return
        if choice == 1:
            # Total spending for a specific category
            category = input("Enter the category: ").strip()
            total = sum(exp.amount for exp in self.expenses if exp.category.lower() == category.lower())
            print(f"The total spending in '{category}' is: Rs {total:.2f}")
        elif choice == 2:
            # Total overall spending
            total = sum(exp.amount for exp in self.expenses)
            print(f"The total overall spending is: Rs {total:.2f}")
        elif choice == 3:
            # Spending over time: daily, monthly, weekly
            try:
                time_choice = int(input(
                    "Enter:\n"
                    "1 for Daily Summary\n"
                    "2 for Monthly Summary\n"
                    "3 for Weekly Summary\n"
                    "Your choice: ").strip())
            except ValueError:
                print("Invalid input, please enter a number.")
                return
            summary = defaultdict(float)
            for expense in self.expenses:
                if not self.validate_date(expense.date):
                    print(f"Skipping invalid date format: {expense.date}")
                    continue
                date_obj = datetime.strptime(expense.date, "%Y-%m-%d")
                if time_choice == 1:
                    key = expense.date
                elif time_choice == 2:
                    key = date_obj.strftime("%Y-%m")
                elif time_choice == 3:
                    year = date_obj.year
                    week = date_obj.isocalendar()[1]
                    key = f"{year}-W{week}"
                else:
                    print("Invalid choice")
                    return
                summary[key] += expense.amount
            print("\nSpending over time summary:")
            for period, amount in sorted(summary.items()):
                print(f"{period}: Rs {amount:.2f}")
        else:
            print("Please choose a valid option.")
    def save_to_file(self, filename="expenses.json"):
        """Saves all expenses to a JSON file for persistence."""
        with open(filename, 'w') as file:
            json.dump([exp.to_dict() for exp in self.expenses], file, indent=4)
    def load_from_file(self, filename="expenses.json"):
        """Loads expenses from a JSON file if it exists."""
        try:
            with open(filename, 'r') as file:
                data = json.load(file)
                self.expenses = [Expense.from_dict(item) for item in data]
            print(f"Loaded {len(self.expenses)} expenses from {filename}.")
        except FileNotFoundError:
            print("No previous data found. Starting fresh.")
        except json.JSONDecodeError:
            print("Data file is corrupt. Starting with an empty list.")
    def delete_expense(self):
        """Deletes an expense entry selected by the user."""
        if not self.expenses:
            print("No expenses to delete.")
            return
        for idx, exp in enumerate(self.expenses):
            print(f"{idx + 1}. {exp}")
        try:
            choice = int(input("Enter the number of the expense to delete: ").strip())
            if 1 <= choice <= len(self.expenses):
                removed = self.expenses.pop(choice - 1)
                print(f"Deleted: {removed}")
                self.save_to_file()
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input.")
    def edit_expense(self):
        """Edits an existing expense entry selected by the user."""
        if not self.expenses:
            print("No expenses to edit.")
            return
        for idx, exp in enumerate(self.expenses):
            print(f"{idx + 1}. {exp}")
        try:
            choice = int(input("Enter the number of the expense to edit: ").strip())
            if 1 <= choice <= len(self.expenses):
                expense = self.expenses[choice - 1]
                print(f"Editing: {expense}")
                new_amount = input("Enter new amount (or press Enter to keep current): ").strip()
                new_category = input("Enter new category (or press Enter to keep current): ").strip()
                new_date = input("Enter new date (YYYY-MM-DD) (or press Enter to keep current): ").strip()
                if new_amount:
                    try:
                        expense.amount = float(new_amount)
                    except ValueError:
                        print("Invalid amount. Keeping previous.")
                if new_category:
                    expense.category = new_category
                if new_date:
                    if self.validate_date(new_date):
                        expense.date = new_date
                    else:
                        print("Invalid date format. Keeping previous.")
                self.save_to_file()
                print("Expense updated successfully.")
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input.")
    def graphical_summary(self):
        """Displays a bar graph of total expenses by category."""
        if not self.expenses:
            print("No data for graphical summary.")
            return
        category_totals = defaultdict(float)
        for exp in self.expenses:
            category_totals[exp.category] += exp.amount
        categories = list(category_totals.keys())
        amounts = [category_totals[cat] for cat in categories]
        plt.figure(figsize=(10, 6))
        plt.bar(categories, amounts, color='green') # Bar graph
        plt.xlabel("Category")
        plt.ylabel("Total Expenses (Rs)")
        plt.title("Expense Distribution by Category")
        plt.xticks(rotation=45)
        plt.grid(axis='y')
        plt.tight_layout()
        plt.show()
"""Main interactive loop for the Expense Tracker."""
if __name__ == "__main__":
    tracker = ExpenseTracker()
    tracker.load_from_file()
    while True:
        print("\n================ Expense Tracker Menu ================")
        print("1. Add Expense")
        print("2. View Summary")
        print("3. Edit Expense")
        print("4. Delete Expense")
        print("5. Graphical Summary")
        print("6. Exit")
        choice = input("Enter your choice (1-6): ").strip()
        if choice == '1':
            tracker.add_expenses()
        elif choice == '2':
            tracker.view_summary()
        elif choice == '3':
            tracker.edit_expense()
        elif choice == '4':
            tracker.delete_expense()
        elif choice == '5':
            tracker.graphical_summary()
        elif choice == '6':
            print("Thank you for using Expense Tracker. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 6.")
