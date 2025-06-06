import os
import re
import requests
import uuid
import json
import copy
from src.FabricMod.FabricMod import FabricMod

REQUIRED = "required"
OPTIONAL = "optional"
VALID_CLIENT_ENVS = {REQUIRED, OPTIONAL}

class MrPackIndexMod:
    def __init__(self, mod_map: dict):
        self._mod_map = copy.deepcopy(mod_map)
        downloads = mod_map.get('downloads')
        if not isinstance(downloads, list) or not downloads:
            raise ValueError("Le champ 'downloads' doit être une liste non vide.")
        jar_url = None
        pattern = re.compile(r"https://cdn\.modrinth\.com/data/(.*)/versions/.*/.*\.jar")
        for url in downloads:
            m = pattern.match(url)
            if m:
                jar_url = url
                break
        if not jar_url:
            raise ValueError("Aucune URL valide de jar trouvée dans 'downloads'.")
        # Lecture et validation de env.client
        env = mod_map.get('env', {})
        client_env = env.get('client', None)
        if not isinstance(client_env, str):
            raise ValueError("env.client doit être une chaîne de caractères.")
        client_env_norm = client_env.strip().lower()
        if client_env_norm not in VALID_CLIENT_ENVS:
            raise ValueError(f"env.client doit être 'required' ou 'optional', trouvé : {client_env}")
        self._client_env = client_env_norm

        # Téléchargement et analyse du mod
        temp_dir = os.path.join('temp')
        os.makedirs(temp_dir, exist_ok=True)
        temp_jar_path = os.path.join(temp_dir, f"mod_{uuid.uuid4().hex}.jar")
        try:
            with requests.get(jar_url, stream=True) as r:
                r.raise_for_status()
                with open(temp_jar_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            self._fabric_mod = FabricMod(temp_jar_path)
            
            # Gestion de la mémoire
            mod_memory_path = os.path.join('memory', 'mod_memory.json')
            dev_mods_path = os.path.join('memory', 'dev_mods.json')
            
            # Charger la mémoire des mods
            if os.path.isfile(mod_memory_path):
                with open(mod_memory_path, 'r', encoding='utf-8') as f:
                    try:
                        mod_memory = json.load(f)
                    except json.JSONDecodeError:
                        mod_memory = {}
            else:
                mod_memory = {}
                
            # Charger la liste des mods de dev
            if os.path.isfile(dev_mods_path):
                with open(dev_mods_path, 'r', encoding='utf-8') as f:
                    try:
                        dev_mods = json.load(f)
                    except json.JSONDecodeError:
                        dev_mods = []
            else:
                dev_mods = []
                
            mod_id = self._fabric_mod.id
            
            # Prompt pour client_env
            if mod_id in mod_memory:
                mem_client_env = mod_memory[mod_id]['client_env'].strip().lower()
                if mem_client_env != self._client_env:
                    print(f"Mod '{self._fabric_mod.name}' : env.client diffère entre la mémoire ('{mem_client_env}') et la map ('{self._client_env}').")
                    print("Garder (R) pour required ou (O) pour optional : ", end="")
                    while True:
                        resp = input().strip().lower()
                        if resp == 'r':
                            chosen = REQUIRED
                            break
                        elif resp == 'o':
                            chosen = OPTIONAL
                            break
                        else:
                            print("Réponse invalide. Tapez R ou O : ", end="")
                    self._client_env = chosen
            else:
                self._client_env = client_env_norm
            
            # Prompt pour dev mod
            if mod_id not in dev_mods and mod_id not in mod_memory:
                print(f"Mod '{self._fabric_mod.name}' : Est-ce un mod de développement ? (O/N) : ", end="")
                while True:
                    resp = input().strip().upper()
                    if resp == 'O':
                        dev_mods.append(mod_id)
                        break
                    elif resp == 'N':
                        break
                    else:
                        print("Réponse invalide. Tapez O ou N : ", end="")
            
            # Mise à jour de la mémoire
            mod_memory[mod_id] = {
                'id': self._fabric_mod.id,
                'name': self._fabric_mod.name,
                'description': self._fabric_mod.description,
                'version': self._fabric_mod.version,
                'client_env': self._client_env
            }
            
            # Sauvegarde des mémoires
            os.makedirs(os.path.dirname(mod_memory_path), exist_ok=True)
            with open(mod_memory_path, 'w', encoding='utf-8') as f:
                json.dump(mod_memory, f, ensure_ascii=False, indent=2)
            with open(dev_mods_path, 'w', encoding='utf-8') as f:
                json.dump(dev_mods, f, ensure_ascii=False, indent=2)
                
            self._mod_map.setdefault('env', {})['client'] = self._client_env
            
        finally:
            if os.path.exists(temp_jar_path):
                os.remove(temp_jar_path)

    @property
    def id(self) -> str:
        return self._fabric_mod.id

    @property
    def name(self) -> str:
        return self._fabric_mod.name

    @property
    def description(self) -> str:
        return self._fabric_mod.description

    @property
    def version(self) -> str:
        return self._fabric_mod.version

    @property
    def client_env(self) -> str:
        return self._client_env

    @property
    def mod_map(self):
        return self._mod_map 