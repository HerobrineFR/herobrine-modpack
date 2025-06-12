import json
import os
from .MrPackIndexMod import MrPackIndexMod

class MrPackIndex:
    def __init__(self, json_path: str):
        self._json_path = json_path
        if not os.path.isfile(json_path):
            raise FileNotFoundError(f"Le fichier '{json_path}' n'existe pas.")
        with open(json_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"Erreur de parsing JSON dans '{json_path}': {e}")
        required_keys = ['files', 'name', 'versionId', 'dependencies', 'summary']
        missing = [k for k in required_keys if k not in data or data[k] is None]
        if missing:
            raise ValueError(f"Clé(s) manquante(s) dans '{json_path}': {', '.join(missing)}")
        self._files = data['files']
        self._name = data['name']
        self._version = data['versionId']
        self._dependencies = data['dependencies']
        self._summary = data['summary']
        
        # Charger la liste des mods à ignorer
        skip_path = os.path.join('memory', 'mod_skip.json')
        skip_list = []
        if os.path.isfile(skip_path):
            with open(skip_path, 'r', encoding='utf-8') as f:
                try:
                    skip_list = json.load(f)
                except json.JSONDecodeError:
                    skip_list = []
        
        # Filtrer les mods à ignorer
        self._mods = []
        for file_entry in self._files:
            downloads = file_entry.get('downloads', [])
            if not any(skip in url for url in downloads for skip in skip_list):
                self._mods.append(MrPackIndexMod(file_entry))

    def get_verified_files(self):
        with open('memory/dev_mods.json', 'r', encoding='utf-8') as f:
            dev_mods = json.load(f)
        for mod in self._mods:
            if mod.id in dev_mods:
                self._mods.remove(mod)
        return [mod.mod_map for mod in self._mods]

    def rewrite_updated_file(self):
        # Relire le JSON d'origine
        with open(self._json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Remplacer la clé files par la liste vérifiée
        data['files'] = self.get_verified_files()
        # Réécrire le fichier
        with open(self._json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @property
    def name(self):
        return self._name

    @property
    def version(self):
        return self._version

    @property
    def summary(self):
        return self._summary

    @property
    def mods(self):
        return self._mods 