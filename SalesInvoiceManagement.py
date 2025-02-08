# -*- coding: utf-8 -*-
"""
Created on Wed Feb  5 12:06:26 2025

@author: HP
"""

import sqlite3

# Function to create a database and table if it doesn't exist
def create_db():
    connection = sqlite3.connect('invoice_database.db')
    cursor = connection.cursor()
    
    # Drop the table if it already exists (to ensure schema is updated)
    cursor.execute("DROP TABLE IF EXISTS invoices")
    
    # Create a table for storing invoice data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER,
            company_name TEXT,
            company_address TEXT,
            company_phone TEXT,
            customer_name TEXT,
            item_name TEXT,
            quantity INTEGER,
            price REAL,
            total REAL
        )
    ''')
    
    connection.commit()
    connection.close()

# Function to save the invoice into the database
def save_invoice_to_db(company_name, company_address, company_phone, 
                       customer_name, items, total):
    connection = sqlite3.connect('invoice_database.db')
    cursor = connection.cursor()

    # Generate a unique invoice_id for the current invoice
    cursor.execute('SELECT MAX(invoice_id) FROM invoices')
    max_id = cursor.fetchone()[0]
    invoice_id = max_id + 1 if max_id else 1  # Start from 1 if no invoice exists yet

    # Insert company details and customer details with each item into the database
    for item in items:
        cursor.execute(''' 
            INSERT INTO invoices (invoice_id, company_name, company_address,
                                  company_phone, customer_name, item_name, 
                                  quantity, price, total)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (invoice_id, company_name, company_address, 
              company_phone, customer_name, 
              item['name'], item['quantity'],
              item['price'], item['quantity'] * item['price']))

    # Save the total amount in the database with a special row for the total
    cursor.execute(''' 
        INSERT INTO invoices (invoice_id, company_name, 
                              company_address, company_phone, customer_name, 
                              item_name, quantity, price, total)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (invoice_id, company_name, company_address, 
          company_phone, customer_name, 'Total', 1, 1, total))

    connection.commit()
    connection.close()

    return invoice_id  # Return the generated invoice ID

# Function to retrieve the entire invoice, excluding company details
def retrieve_invoice(invoice_id):
    connection = sqlite3.connect('invoice_database.db')
    cursor = connection.cursor()

    cursor.execute(''' 
        SELECT * FROM invoices WHERE invoice_id = ? 
    ''', (invoice_id,))
    invoice = cursor.fetchall()
    connection.close()

    if not invoice:
        return None  # If no invoice was found, return None

    # Group all items by invoice_id, excluding company details
    grouped_invoice = {
        "invoice_id": invoice_id,
        "customer_name": invoice[0][5],  # Customer name from first item
        "items": []
    }

    for row in invoice:
        if row[6] != 'Total':  # Ignore the row with 'Total' item_name
            grouped_invoice["items"].append({
                "name": row[6],
                "quantity": row[7],
                "price": row[8],
                "total": row[8] * row[7]
            })

    # Add total separately from the group of items
    total_row = next(row for row in invoice if row[6] == 'Total')
    grouped_invoice["total"] = total_row[9]

    return grouped_invoice

def generate_invoice():
    # Company details
    company_name = "Company XYZ Ltd"
    company_address = "Complex 5,GRA, Ilorin Kwara State Nigeria"
    company_phone = "+234(0)8077580631"

    # Get customer details
    customer_name = input("Enter customer's name: \n")

    # Get items and their details
    items = []
    while True:
        item_name = input("Enter the name of product purchased (or type 'done' to finish): \n")
        if item_name.lower() == 'done':
            break
        quantity = int(input(f"Enter quantity of product purchased for {item_name}: \n"))
        price = float(input(f"Enter the unit price for the product purchased {item_name}: \n"))
        items.append({'name': item_name, 'quantity': quantity, 'price': price})

    # Calculate total
    VAT = 1.35
    total = 0 + VAT
    print("\n--- Invoice ---")
    print(f"Company: {company_name}")
    print(f"Address: {company_address}")
    print(f"Phone: {company_phone}")
    print("\nCustomer Details:")
    print(f"Name: {customer_name}")
    print("\nItems Sold:")

    # Display item details
    for item in items:
        item_total = item['quantity'] * item['price']
        total += item_total
        print(f"Product Name: {item['name']} | Quantity: {item['quantity']} | "
              f"Price: N{item['price']:.2f} | Total amount: N{item_total:.2f}")

    print(f"\nTotal Amount of all products + VAT of N1.35: N{total:.2f}")
    print("\nThank you for your business!")

    # Save the invoice to the database and get the unique ID
    invoice_id = save_invoice_to_db(company_name, company_address, company_phone, customer_name, items, total)

    # Print the unique invoice ID
    print(f"Invoice ID is: {invoice_id}")

def test_retrieve_invoice():
    invoice_id = int(input("Enter the invoice ID to retrieve: "))
    invoice = retrieve_invoice(invoice_id)
    if invoice:
        print("\n--- Retrieved Invoice ---")
        print(f"Invoice ID: {invoice['invoice_id']}")
        print(f"Customer Name: {invoice['customer_name']}")
        print("\nItems Sold:")

        # Include customer name alongside product details
        for item in invoice["items"]:
            print(f"Customer: {invoice['customer_name']} | Product Name: {item['name']} | "
                  f"Quantity: {item['quantity']} | Price: N{item['price']:.2f} | "
                  f"Total amount: N{item['total']:.2f}")
        print(f"\nTotal Amount: N{invoice['total']:.2f}")
    else:
        print("Invoice not found.")

def main():
    # Create the database and table
    create_db()

    while True:
        print("\n--- Invoice Management System ---")
        print("1. Generate a new invoice")
        print("2. Retrieve an existing invoice")
        print("3. Exit")
        
        choice = input("Please select an operation ([1]| [2] |[3]): ")

        if choice == '1':
            # Call the function to generate an invoice
            generate_invoice()
        elif choice == '2':
            # Retrieve an invoice by its ID
            test_retrieve_invoice()
        elif choice == '3':
            print("Exiting the program...")
            break
        else:
            print("Invalid choice. Please try again.")

# Call the main function to start the program
if __name__ == "__main__":
    main()
