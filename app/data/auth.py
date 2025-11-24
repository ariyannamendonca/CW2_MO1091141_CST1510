import bcrypt
import os

def hash_password(plain_text_pass):
    password_bytes = plain_text_pass.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    return hashed_password

def verify_password(plain_text_pass, hashed_password):
    password_bytes = plain_text_pass.encode('utf-8')
    hashed_pass_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_pass_bytes)

USER_DATA_FILE = "../../DATA/user.txt"

def register_user(username, password):
    open(USER_DATA_FILE, 'a').close()
    for line in open(USER_DATA_FILE, 'r'):
        existing_username = line.strip().split(',')[0]
        if existing_username == username:
            print("Error: Username already exists") #change it to username (name) alr exists
            return False

    hashed_password = hash_password(password).decode('utf-8')

    with open(USER_DATA_FILE, 'a') as file:
        file.write(f'{username},{hashed_password}\n')

    print(f'{username} registered successfully!')
    return True

def user_exists(username):
    with open(USER_DATA_FILE, 'r') as file:
        for line in file:
            stored_user = line.strip().split(",")[0]
            if stored_user == username:
                return True
    return False

def login_user(username, password):
    with open(USER_DATA_FILE, 'r') as file:
        for line in file:
            stored_user, stored_hash = line.strip().split(",")

            if stored_user == username:
                if verify_password(password, stored_hash):
                    print("Login successful.")
                    return True
                else:
                    print("Error: Invalid Password.")
                    return False
    print("Username not found")
    return False

def validate_username(username):
  if len(username) < 5:
      print ("Username too short.")
      return False
  if "_ , *" in username:
      print ("Username cant contain this.")
      return False
  return True, ""

def validate_password(password):
    if len(password) < 8:
        print ("Password too short, need at least 8 characters.")
        return False
    return True, ""

def display_menu():
    """Displays the main menu options."""
    print("\n" + "="*50)
    print("  MULTI-DOMAIN INTELLIGENCE PLATFORM")
    print("  Secure Authentication System")
    print("="*50)
    print("\n[1] Register a new user")
    print("[2] Login")
    print("[3] Exit")
    print("-"*50)

def main():
    """Main program loop."""
    print("\nWelcome to the Week 7 Authentication System!")

    while True:
        display_menu()
        choice = input("\nPlease select an option (1-3): ").strip()

        if choice == '1':
            #registration flow
            print("\n---USER REGISTRATION---")
            username = input("Enter a username: ").strip()

            #validate username
            is_valid, error_msg = validate_username(username)
            if not is_valid:
                print(f"Error: {error_msg}")
                continue

            password = input("Enter a password: ").strip()

            #Validate password
            is_valid, error_msg = validate_password(password)
            if not is_valid:
                print(f"Error: {error_msg}")
                continue

            #confirm password
            password_confirm = input("Confirm password:").strip()
            if password != password_confirm:
                print("ErrOr: Passwords do not match.")
                continue

            #register the user
            register_user(username, password)

        elif choice == '2':
            #Login flow
            print("\n--- USER LOGIN---")
            username = input("Enter a username: ").strip()
            password = input("Enter a password: ").strip()

            #Attempt login
            if login_user(username, password):
                input("\nPress enter to return to main menu...")

        elif choice == '3':
            #exit
            print("\n Thank you for using Week 7 Authentication System!")
            print("Exiting...")
            break
        else:
            print("\nERROR: Invalid choice. Please try again and select 1, 2 or 3.")

if __name__ == '__main__':
    main()