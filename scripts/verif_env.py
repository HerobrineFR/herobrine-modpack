import re
import json
from dotenv import load_dotenv
import os

def verifValue(value, regex):
    if re.match(regex, value):
        return True
    return False

def verifEnv():
    # Charger les fichiers .env et env_variables.json
    load_dotenv()
    with open('scripts/config/env_variables.json', 'r') as file:
        variables = json.load(file)
    
    # Vérifier chaque variable
    all_valid = True
    for var in variables:
        name = var['name']
        regex = var['regex']
        value = os.getenv(name)
        if not value or not verifValue(value, regex):
            all_valid = False
            print(f"{var['message']} Current value: {value if value else 'None'}.")
    
    if all_valid:
        print("All environment variables are valid.")
    return all_valid

if __name__ == "__main__":
    if verifEnv():
        print("Environment is valid.")
    else:
        print("Environment is not valid. Please check the error messages above.")