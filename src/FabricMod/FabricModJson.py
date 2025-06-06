import json
import os

class FabricModJson:
    def __init__(self, json_path: str):
        if not os.path.isfile(json_path):
            raise FileNotFoundError(f"Le fichier '{json_path}' n'existe pas.")
        with open(json_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"Erreur de parsing JSON dans '{json_path}': {e}")
        self._id = data.get('id', None)
        self._name = data.get('name', None)
        self._description = data.get('description', None)
        self._version = data.get('version', None)
        missing = [k for k, v in {'id': self._id, 'name': self._name, 'description': self._description, 'version': self._version}.items() if v is None]
        if missing:
            raise ValueError(f"Les propriétés suivantes sont manquantes dans '{json_path}': {', '.join(missing)}")

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def version(self) -> str:
        return self._version 