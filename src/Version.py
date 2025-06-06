import json
import os
from src.MrPack import MrPack
from src.FabricMod.FabricMod import FabricMod

class Version:
    loaded_list = []

    class Mod:
        def __init__(self, id: str, name: str, description: str, version: str):
            self._id = id
            self._name = name
            self._description = description
            self._version = version

        @classmethod
        def from_fabric_mod(cls, fabric_mod: FabricMod) -> 'Version.Mod':
            return cls(
                id=fabric_mod.id,
                name=fabric_mod.name,
                description=fabric_mod.description,
                version=fabric_mod.version
            )

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

    def __init__(self, version_id: str, parent_version_id: str):
        self._version_id = version_id
        self._parent_version_id = parent_version_id
        self._mods = []

    def updateWithMrPack(self, mrpack: MrPack):
        self._mods = []
        for mod in mrpack.mods:
            self._mods.append(self.Mod.from_fabric_mod(mod))

    @staticmethod
    def fromMemory(version_id: str) -> 'Version':
        file_path = os.path.join('memory', 'versions', f"{version_id}.json")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Version file not found: {file_path}")
        with open(file_path, 'r') as f:
            data = json.load(f)
        version = Version(data['version_id'], data['parent_version_id'])
        version._mods = [Version.Mod(**mod_data) for mod_data in data.get('mods', [])]
        Version.loaded_list.append(version)
        return version
        
    @staticmethod
    def fromMrPack(mrpack: 'MrPack', parent_version_id: str) -> 'Version':
        version = Version(mrpack.version, parent_version_id)
        version.updateWithMrPack(mrpack)
        Version.loaded_list.append(version)
        
        # Sauvegarder dans memory
        memory_dir = os.path.join('memory', 'versions')
        os.makedirs(memory_dir, exist_ok=True)
        file_path = os.path.join(memory_dir, f"{version._version_id}.json")
        
        data = {
            'version_id': version._version_id,
            'parent_version_id': version._parent_version_id,
            'mods': [
                {
                    'id': mod.id,
                    'name': mod.name,
                    'description': mod.description,
                    'version': mod.version
                }
                for mod in version._mods
            ]
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        return version
        
    def getChangeLog(self) -> str:
        changelog = [f"## {self._version_id}\n"]
        
        if not self._parent_version_id:
            changelog.append("\n### Mods ajoutés:")
            changelog.extend([f"- {mod.id}" for mod in self._mods])
            return "\n".join(changelog)
            
        parent = Version.fromMemory(self._parent_version_id)
        
        # Créer des dictionnaires pour faciliter la recherche
        current_mods = {mod.id: mod for mod in self._mods}
        parent_mods = {mod.id: mod for mod in parent._mods}
        
        # Trouver les mods ajoutés, mis à jour et supprimés
        added_mods = [mod for mod_id, mod in current_mods.items() if mod_id not in parent_mods]
        updated_mods = [
            f"{mod.id}: {parent_mods[mod.id].version} → {mod.version}"
            for mod_id, mod in current_mods.items()
            if mod_id in parent_mods and parent_mods[mod_id].version != mod.version
        ]
        removed_mods = [mod for mod_id, mod in parent_mods.items() if mod_id not in current_mods]
        
        if added_mods:
            changelog.append("\n### Mods ajoutés:")
            changelog.extend([f"- {mod.id}" for mod in added_mods])
            
        if updated_mods:
            changelog.append("\n### Mods updatés:")
            changelog.extend([f"- {mod}" for mod in updated_mods])
            
        if removed_mods:
            changelog.append("\n### Mods supprimés:")
            changelog.extend([f"- {mod.id}" for mod in removed_mods])
            
        return "\n".join(changelog)
        
    @staticmethod
    def generateChangelog() -> str:
        changelog = ["# Herobrine Modpack Changelog\n"]
        
        # Ajouter le changelog de chaque version
        for version in Version.loaded_list:
            changelog.append(version.getChangeLog())
            changelog.append("")  # Ajouter une ligne vide entre les versions
            
        changelog_str = "\n".join(changelog)
        
        # Écrire dans CHANGELOG.md
        with open('CHANGELOG.md', 'w', encoding='utf-8') as f:
            f.write(changelog_str)
            
        return changelog_str
        
    @staticmethod
    def get(mrpack: MrPack) -> 'Version':
        try:
            version = Version.fromMemory(mrpack.version)
            version.updateWithMrPack(mrpack)
            return version
        except FileNotFoundError:
            # Lire la version parente depuis current_version.txt
            current_version_path = os.path.join('memory', 'current_version.txt')
            parent_version_id = None
            if os.path.exists(current_version_path):
                with open(current_version_path, 'r') as f:
                    parent_version_id = f.read().strip()
                    if parent_version_id == 'None':
                        parent_version_id = None
            
            return Version.fromMrPack(mrpack, parent_version_id)
        
        
    
    