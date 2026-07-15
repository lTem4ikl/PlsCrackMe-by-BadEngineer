import random
import string

def generate_password():
    upper = ''.join(random.choices(string.ascii_uppercase, k=3))
    lower = ''.join(random.choices(string.ascii_lowercase, k=4))
    digits = ''.join(random.choices(string.digits, k=3))
    specials = ''.join(random.choices("!@#$%^&*()_+-=[]{}|;:,.<>?", k=3))
    
    pwd = upper + lower + digits + specials
    
    pwd_list = list(pwd)
    random.shuffle(pwd_list)
    return ''.join(pwd_list)

print(generate_password())