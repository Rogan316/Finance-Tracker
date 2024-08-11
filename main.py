import pandas as pd
import csv
from datetime import datetime
from data_entry import get_date, get_amount, get_category, get_description, date_format
from matplotlib import pyplot as plt
class CSV:

    CSV_FILE = "finance_data.csv"
    COLUMNS = ["Date", "Amount", "Category", "Description"]
    
    

    @classmethod
    def initialize_csv(cls):
        try:
            pd.read_csv(cls.CSV_FILE)
        except FileNotFoundError:
            df = pd.DataFrame(columns=cls.COLUMNS)
            df.to_csv(cls.CSV_FILE, index=False)


    @classmethod
    def standardize_dates(cls):
        """Ensure all dates in the CSV are in the %d-%m-%Y format without overwriting correct dates."""
        df = pd.read_csv(cls.CSV_FILE)
    
        def parse_date(date_str):
            try:
                # Try parsing with the expected format first
                parsed_date = datetime.strptime(date_str, "%d-%m-%Y")
            except ValueError:
                # If it fails, try parsing with the alternative format
                parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
            # Return the date in the desired format
            return parsed_date.strftime(date_format)
    
        df["Date"] = df["Date"].apply(lambda x: parse_date(x) if pd.notna(x) else x)

        df.to_csv(cls.CSV_FILE, index=False)
        print(f"Dates in {cls.CSV_FILE} standardized to {date_format} format.")


    @classmethod
    def add_entry(cls, date, amount, category, description):
        new_entry = {
            "Date": date,
            "Amount": amount,
            "Category": category,
            "Description": description
        }
    
        with open(cls.CSV_FILE, mode="a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=cls.COLUMNS)
            writer.writerow(new_entry)
        print("Entry added successfully!")

    @classmethod
    def get_transactions(cls, start_date, end_date):
        cls.standardize_dates()
        df = pd.read_csv(cls.CSV_FILE)
        df["Date"] = pd.to_datetime(df["Date"], format=date_format)
        start_date = datetime.strptime(start_date, date_format)
        end_date = datetime.strptime(end_date, date_format)
        mask = (df["Date"] >= start_date) & (df["Date"] <= end_date)
        filtered_df = df.loc[mask]

        if filtered_df.empty:
            print("No transactions found for the given date range.")
            
        else:
            print(f"Transactions from {start_date.strftime(date_format)} to {end_date.strftime(date_format)}:")
            print(filtered_df.to_string(index=False, formatters={"Date": lambda x: x.strftime(date_format)}))

            total_income = filtered_df[filtered_df["Category"] == "Income"]["Amount"].sum()
            total_expense = filtered_df[filtered_df["Category"] == "Expense"]["Amount"].sum()
            print("\nSummary:")
            print(f"Total Income: R{total_income:.2f}")
            print(f"Total Expense: R{total_expense:.2f}")
            print(f"Net Income: R{(total_income - total_expense):.2f}")
            print("")

        return filtered_df

   

def add():
    CSV.initialize_csv()
    date = get_date("Enter the date of the transaction (dd-mm-yyyy) or hit enter for today's date: ",
                    allow_default=True,
    )
    amount = get_amount()
    category = get_category()
    description = get_description()
    CSV.add_entry(date,amount,category,description)

def plot_transactions(df):
    df.set_index("Date", inplace=True)

    income_df = (
        df[df["Category"] == "Income"]
        .resample("D")
        .sum()
        .reindex(df.index, fill_value=0)
    )

    expense_df = (
        df[df["Category"] == "Expense"]
        .resample("D")
        .sum()
        .reindex(df.index, fill_value=0)
    )
                 
    plt.figure(figsize=(10,5))
    plt.plot(income_df.index, income_df["Amount"], label="Income", color="g")
    plt.plot(expense_df.index, expense_df["Amount"], label="Expense", color="r")
    plt.xlabel("Date")
    plt.ylabel("Amount")
    plt.title("Income and Expenses over time")
    plt.legend()
    plt.grid(True)
    plt.show()



def main():
    while True:
        print("\n1. Add a transaction")
        print("2. View transactions and summary within a date range")
        print("3. Exit")
        choice = input("Enter your choice(1-3): ")

        if choice == "1":
            add()   
        elif choice == "2":
            start_date = get_date("Enter the start date (dd-mm-yyyy): ")
            end_date = get_date("Enter the end date (dd-mm-yyyy): ")
            CSV.get_transactions(start_date, end_date)
            df = CSV.get_transactions(start_date, end_date)
            if input ("Would you like to plot the transactions? (y/n): ").lower() == "y":
                plot_transactions(df)
        elif choice == "3":
            print("Exiting the program...")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 3.")

if __name__ == "__main__":
    main()
    
