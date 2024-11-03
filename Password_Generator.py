
import random
import string

def generate_password(length=16):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

def generate_pin(length):
    characters = string.digits
    return ''.join(random.choice(characters) for _ in range(length))

password = generate_password()

pin = generate_pin(6)
print(password)