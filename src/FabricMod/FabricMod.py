import os
import zipfile
from src.FabricMod.FabricModJson import FabricModJson

class FabricMod:
    def __init__(self, jar_path: str):
        if not os.path.isfile(jar_path):
            raise FileNotFoundError(f"Le fichier '{jar_path}' n'existe pas.")
        temp_dir = os.path.join('temp')
        os.makedirs(temp_dir, exist_ok=True)
        temp_json_path = os.path.join(temp_dir, 'fabric.mod.json')
        try:
            with zipfile.ZipFile(jar_path, 'r') as jar:
                if 'fabric.mod.json' not in jar.namelist():
                    raise FileNotFoundError(f"'fabric.mod.json' n'a pas été trouvé dans '{jar_path}'.")
                jar.extract('fabric.mod.json', temp_dir)
            self._mod_json = FabricModJson(temp_json_path)
        finally:
            if os.path.exists(temp_json_path):
                os.remove(temp_json_path)

    @property
    def id(self) -> str:
        return self._mod_json.id

    @property
    def name(self) -> str:
        return self._mod_json.name

    @property
    def description(self) -> str:
        return self._mod_json.description

    @property
    def version(self) -> str:
        return self._mod_json.version 