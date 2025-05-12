import os
import datetime

users_file = "users.txt"
accounts_file = "accounts.txt"
transactions_file = "transactions.txt"
last_acc_file = "last_account_number.txt"

def initialize_files():
    for file_name in [users_file, accounts_file, transactions_file]:
        if not os.path.exists(file_name):
            open(file_name, 'w').close()
    if not os.path.exists(last_acc_file):
        with open(last_acc_file, 'w') as f:
            f.write("1000")

def read_file(file_name):
    with open(file_name, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def write_file(file_name, lines):
    with open(file_name, 'w') as f:
        f.writelines([line + '\n' for line in lines])

def load_users():
    return [line.split(',') for line in read_file(users_file)]

def save_users(users):
    write_file(users_file, [','.join(u) for u in users])

def load_accounts():
    return [line.split(',') for line in read_file(accounts_file)]

def save_accounts(accounts):
    write_file(accounts_file, [','.join(a) for a in accounts])

def append_transaction(acc_no, t_type, amount):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(transactions_file, 'a') as f:
        f.write(f"{acc_no},{t_type},{amount},{now}\n")

def get_next_account_number():
    try:
        with open(last_acc_file, 'r') as f:
            last = int(f.read().strip() or 1000)
    except:
        last = 1000
    next_num = last + 1
    with open(last_acc_file, 'w') as f:
        f.write(str(next_num))
    return str(next_num)

def check_admin_user():
    if not any(u[2] == 'admin' for u in load_users()):
        print("No admin found. Creating new admin.")
        user = input("Enter new admin username: ")
        pw = input("Enter new admin password: ")
        save_users([[user, pw, "admin"]])

def login():
    while True:
        print("\n=== Banking System ===")
        print("1. Admin Login\n2. Customer Login\n3. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            if auth_login('admin'):
                admin_menu()
        elif choice == '2':
            user = auth_login('customer')
            if user:
                customer_menu(user)
        elif choice == '3':
            break
        else:
            print("Invalid choice.")

def auth_login(role):
    user = input("Enter your admin username: ") if role == 'admin' else input("Enter your username (National ID): ")
    pw = input("Enter your password: ")
    for u in load_users():
        if u[0] == user and u[1] == pw and u[2] == role:
            print("Login successful.")
            return u
    print("Invalid credentials.")
    return None

def admin_menu():
    while True:
        print("\nAdmin Menu:")
        print("1. Create new customer account")
        print("2. Delete customer account")
        print("3. View customer info and transactions")
        print("4. Logout")
        
        choice = input("Enter your choice: ")

        if choice == '1':
            print("You chose to create a new customer account.")  
            create_account()

        elif choice == '2':
            print("You chose to delete a customer account.")  
            delete_account()

        elif choice == '3':
            print("You chose to view customer info and transactions.")  
            view_account_info()

        elif choice == '4':
            print("Logging out. Thank you!")  
            break

        else:
            print("Invalid choice. Please enter a number between 1 and 4.")

def create_account():
    users = load_users()
    accs = load_accounts()
    while True:
        nid = input("Enter customer's National ID (will be used as username): ")
        if any(u[0] == nid for u in users):
            print("ID already exists. Please enter a different one.")
        else:
            break
    name = input("Enter customer's full name: ")
    phone = input("Enter customer's phone number: ")
    pw = input("Set password for the customer: ")
    while True:
        try:
            balance = float(input("Enter initial deposit amount: "))
            if balance < 0:
                raise ValueError
            break
        except:
            print("Invalid amount. Please enter a valid number.")
    acc_no = get_next_account_number()
    users.append([nid, pw, "customer"])
    accs.append([acc_no, nid, str(balance), nid, name, phone])
    save_users(users)
    save_accounts(accs)
    append_transaction(acc_no, "Initial Deposit", balance)
    print(f"Customer account created. Account Number: {acc_no}")

def delete_account():
    key = input("Enter customer's Account Number or National ID to delete: ")
    accs = load_accounts()
    users = load_users()
    acc = next((a for a in accs if a[0] == key or a[3] == key), None)
    if not acc:
        print("No such customer found.")
        return
    nid = acc[3]
    accs = [a for a in accs if a[3] != nid]
    users = [u for u in users if u[0] != nid]
    save_accounts(accs)
    save_users(users)
    print("Customer account deleted.")

def view_account_info():
    key = input("Enter account number or National ID: ")
    accs = load_accounts()
    for a in accs:
        if a[0] == key or a[3] == key:
            print("Customer Information:")
            print(f"Account Number: {a[0]}")
            print(f"Name: {a[4]}")
            print(f"National ID: {a[3]}")
            print(f"Phone: {a[5]}")
            print(f"Last Balance: {a[2]}")
            print("Transaction History:")
            for t in read_file(transactions_file):
                parts = t.split(',')
                if parts[0] == a[0]:
                    print(f"{parts[3]} - {parts[1]}: {parts[2]}")
            return
    print("Account not found.")

def customer_menu(user):
    while True:
        print("\nCustomer Menu:")
        print("1. View Balance\n2. Deposit Money\n3. Withdraw Money\n4. View Transaction History\n5. Logout")
        choice = input("Enter your choice: ")

        if choice == '1':
            print("You chose to view your balance.")
            view_balance(user[0])

        elif choice == '2':
            print("You chose to deposit money.")
            deposit(user[0])

        elif choice == '3':
            print("You chose to withdraw money.")
            withdraw(user[0])

        elif choice == '4':
            print("You chose to view your transaction history.")
            view_history(user[0])

        elif choice == '5':
            print("Logging out. Thank you!")
            break

        else:
            print("Invalid choice. Please enter a number between 1 and 5.")

def find_account(username):
    return next((a for a in load_accounts() if a[1] == username), None)

def view_balance(username):
    acc = find_account(username)
    if acc:
        print(f"Your current balance is: {acc[2]}")
    else:
        print("Account not found.")

def deposit(username):
    acc = find_account(username)
    if not acc:
        print("Account not found.")
        return
    try:
        amt = float(input("Enter amount to deposit: "))
        if amt <= 0:
            raise ValueError
        acc[2] = str(float(acc[2]) + amt)
        update_account(acc)
        append_transaction(acc[0], "Deposit", amt)
        print("Deposited successfully.")
    except:
        print("Invalid amount.")

def withdraw(username):
    acc = find_account(username)
    if not acc:
        print("Account not found.")
        return
    try:
        amt = float(input("Enter amount to withdraw: "))
        if amt <= 0 or amt > float(acc[2]):
            print("Invalid or insufficient.")
            return
        acc[2] = str(float(acc[2]) - amt)
        update_account(acc)
        append_transaction(acc[0], "Withdraw", amt)
        print("Withdrawn successfully.")
    except:
        print("Invalid amount.")

def view_history(username):
    acc = find_account(username)
    if acc:
        print("\nTransaction History:")
        for t in read_file(transactions_file):
            p = t.split(',')
            if p[0] == acc[0]:
                print(f"{p[3]} - {p[1]}: {p[2]}")
    else:
        print("Account not found.")

def update_account(updated):
    accs = load_accounts()
    for i, a in enumerate(accs):
        if a[0] == updated[0]:
            accs[i] = updated
            break
    save_accounts(accs)

if __name__ == "__main__":
    initialize_files()
    check_admin_user()
    login()
