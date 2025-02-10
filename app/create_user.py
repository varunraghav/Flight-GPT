import sys
from auth_utils import hash_password
from db_utils import create_user

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python create_user.py <username> <password>")
        sys.exit(1)
    
    username = sys.argv[1]
    password = hash_password(sys.argv[2])
    
    if create_user(username, password):
        print(f"User {username} created successfully!")
    else:
        print(f"User {username} already exists!")