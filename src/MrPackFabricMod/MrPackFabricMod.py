import os
import json
from src.FabricMod.FabricMod import FabricMod

REQUIRED = "required"
OPTIONAL = "optional"
VALID_CLIENT_ENVS = {REQUIRED, OPTIONAL}

class MrPackFabricMod:
    def __init__(self, jar_path: str):
        self._jar_path = jar_path
        self._is_disabled = jar_path.endswith('.disabled')
        if not os.path.isfile(jar_path):
            raise FileNotFoundError(f"Le fichier '{jar_path}' n'existe pas.")
        self._fabric_mod = FabricMod(self._jar_path)
        self._client_env = OPTIONAL if self._is_disabled else REQUIRED
        mod_memory_path = os.path.join('memory', 'mod_memory.json')
        dev_mods_path = os.path.join('memory', 'dev_mods.json')
        self._from_memory = False
        # Charger la mémoire
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
        if mod_id in mod_memory:
            mem_obj = mod_memory[mod_id]
            missing = [k for k in ('id', 'name', 'description', 'client_env') if k not in mem_obj or mem_obj[k] is None]
            if missing:
                raise ValueError(f"Clé(s) manquante(s) dans la mémoire pour '{mod_id}': {', '.join(missing)}")
            mem_client_env = mem_obj['client_env'].strip().lower()
            if mem_client_env != self._client_env:
                print(f"Attention : env.client diffère entre la mémoire ('{mem_client_env}') et le mod ('{self._client_env}').")
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
                mem_obj['client_env'] = chosen
                self._client_env = chosen
                with open(mod_memory_path, 'w', encoding='utf-8') as f:
                    json.dump(mod_memory, f, ensure_ascii=False, indent=2)
            else:
                self._client_env = mem_client_env
            self._from_memory = True
        if not self._from_memory:
            # Ajout dans la mémoire
            try:
                if os.path.isfile(mod_memory_path):
                    with open(mod_memory_path, 'r', encoding='utf-8') as f:
                        try:
                            mod_memory = json.load(f)
                        except json.JSONDecodeError:
                            mod_memory = {}
                else:
                    mod_memory = {}
                print(f"Ajouter à la mémoire : {self._fabric_mod.name} (client_env: {self._client_env}). Appuyez sur Entrée pour confirmer.")
                input()
                
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
                    os.makedirs(os.path.dirname(dev_mods_path), exist_ok=True)
                    with open(dev_mods_path, 'w', encoding='utf-8') as f:
                        json.dump(dev_mods, f, ensure_ascii=False, indent=2)
                
                mod_memory[mod_id] = {
                    'id': self._fabric_mod.id,
                    'name': self._fabric_mod.name,
                    'description': self._fabric_mod.description,
                    'client_env': self._client_env
                }
                os.makedirs(os.path.dirname(mod_memory_path), exist_ok=True)
                with open(mod_memory_path, 'w', encoding='utf-8') as f:
                    json.dump(mod_memory, f, ensure_ascii=False, indent=2)
                    
            except Exception as e:
                pass

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
    def client_env(self) -> str:
        return self._client_env

    def change_file_extension_with_updated_status(self) -> None:
        file_path = self._jar_path
        if not (file_path.endswith('.jar') or file_path.endswith('.jar.disabled')):
            raise ValueError("Le fichier doit se terminer par .jar ou .jar.disabled")
        new_path = file_path
        if self._client_env == "optional":
            if file_path.endswith('.jar'):
                new_path = file_path + '.disabled'
        elif self._client_env == "required":
            if file_path.endswith('.jar.disabled'):
                new_path = file_path[:-9]
        if new_path != file_path:
            os.rename(file_path, new_path)
            self._jar_path = new_path 