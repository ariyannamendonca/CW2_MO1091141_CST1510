import bcrypt
import os

USER_DATA_FILE = "../../DATA/user.txt"

class User:
    """
    Stores user information and does authentication
    """

    def __init__(self, username=None, password_hash=None, role='user'):
        self.username = username
        self.password_hash = password_hash
        self.role = role

    def hash_password(self, plain_text_pass):
        """hash password using bcrypt"""
        password_bytes = plain_text_pass.encode('utf-8')  # converts plain text pass into bytes so it gets hashed
        salt = bcrypt.gensalt()  # combines with pass before hashing so hashed results are different
        hashed_password = bcrypt.hashpw(password_bytes, salt)
        return hashed_password.decode('utf-8')

    def verify_password(self, plain_text_pass):
        """verify users password"""
        if self.password_hash:
            return User.verify_hash_password(plain_text_pass, self.password_hash)
        return False

    def verify_hash_password(self, plain_text_pass, hashed_password):
        """verify user entered password against the hashed password"""
        password_bytes = plain_text_pass.encode('utf-8') #encodes what user entered to byte
        if isinstance(hashed_password, str):
            hashed_pass_bytes = hashed_password.encode('utf-8') #stored hash converted to bytes
        else:
            hashed_pass_bytes = hashed_password

        return bcrypt.checkpw(password_bytes, hashed_pass_bytes) #salt rehashes password_bytes, compares both hashes

    def get_role(self):
        """Return user role"""
        return self.role

    def user_exists(self,username):
        """checks if username exists in user.txt file"""
        try:
            with open(USER_DATA_FILE, 'r') as file:
                for line in file:
                    stored_user = line.strip().split(",")[0]
                    if stored_user == username:
                        return True
        except FileNotFoundError:
            pass
        return False

    def register_user(self,username, password):
        """register new user"""
        if self.user_exists(username):
            print("Error: Username already exists")
            return False

        hashed_password = self.hash_password(password)
        if not os.path.exists(USER_DATA_FILE):
            open (USER_DATA_FILE, 'a').close()

        with open(USER_DATA_FILE, 'a') as file:
            file.write(f"{username},{hashed_password},user\n")

        print(f"{username} successfully registered")
        return True

    def login(self, username, password):
        """user login, user object is returned if successful"""
        try:
            with open(USER_DATA_FILE, 'r') as file:
                for line in file:
                    parts = line.strip().split(",")

                    if len(parts) < 2:
                        continue

                    stored_user = parts[0]
                    stored_hash = parts[1]
                    stored_role = parts[2] if len(parts) > 2 else 'user'

                    if stored_user == username:
                        if self.verify_hash_password(password, stored_hash):
                            return User(username, stored_hash, stored_role)
                        else:
                            print("Error: Invalid Password")
                            return None
        except FileNotFoundError:
            print("Error: File not found, please register")
            return None

        print("Username not found")
        return None

def validate_username(username):
    if len(username) < 2:
        return False, "This username is too short"
    if any(char in username for char in "- * ,"):
        return False, "Username cant contain '-', '*', or ','"
    return True, ""

def validate_password(password):
    if len(password) < 8:
        return False, "This password is too short, need 8 or more characters"
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
            user = User()
            user.register_user(username, password)

        elif choice == '2':
            #Login flow
            print("\n--- USER LOGIN---")
            username = input("Enter a username: ").strip()
            password = input("Enter a password: ").strip()

            #Attempt login
            user = User()
            logged_in_user = user.login(username, password)

            if logged_in_user:
                print(f"Logged in successfully. Welcome, {logged_in_user.username}!")
                print(f"Your role is: {logged_in_user.get_role()}")

                input("\nPress enter to return to main menu...")

        elif choice == '3':
            #exit
            print("\n Thank you for using the Authentication System!")
            print("Exiting...")
            break
        else:
            print("\nERROR: Invalid choice. Please try again and select 1, 2 or 3.")

if __name__ == '__main__':
    main()