import secrets

# Generate a secure random secret key
secret_key = secrets.token_urlsafe(32)
print(f'SECRET_KEY={secret_key}')

# Create a .env file
# with open('.env', 'w') as f:
#     f.write(f'SECRET_KEY={secret_key}')

# then you will update secrets with the new key
# import os
# from dotenv import load_dotenv
# load_dotenv()
# SECRET_KEY = os.getenv('SECRET_KEY')