import json
from dotenv import load_dotenv
from verif_env import verifValue
from verif_env import verifEnv
import os

def setup():
    # Charger les fichiers .env et env_variables.json
    load_dotenv()
    with open('scripts/config/env_variables.json', 'r') as file:
        variables = json.load(file)

    # Récupérer les valeurs actuelles de l'environnement
    env_path = '.env'
    env_vars = {}
    for var in variables:
        name = var['name']
        current_value = os.getenv(name, '')
        example = var.get('example', '')
        while True:
            input_value = input(f"Enter value for {name} ({var['description']}) [Current: {current_value}] [Example: {example}]: ")
            if input_value.strip() == "":
                input_value = current_value
            if input_value == "" or verifValue(input_value, var['regex']):
                break
            else:
                print(var['message'])
        env_vars[name] = input_value

    # Mettre à jour le fichier .env
    with open(env_path, 'w') as file:
        for key, value in env_vars.items():
            file.write(f"{key}={value}\n")
    verifEnv()

if __name__ == "__main__":
    setup()