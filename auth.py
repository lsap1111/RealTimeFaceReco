# auth.py

# In a real app, use a database and hashed passwords.
# This example uses a hardcoded user for simplicity.

users = {
    "admin": "password123",  # username: password
}

def authenticate_user(username, password):
    """
    Check if the provided username and password are correct.
    Returns True if valid, False otherwise.
    """
    if username in users and users[username] == password:
        return True
    return False

def logout_user():
    """
    Any logout cleanup can be done here.
    For now, this function is a placeholder.
    """
    pass
