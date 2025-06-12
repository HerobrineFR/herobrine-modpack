import os
import shutil
import zipfile
from src.ModrinthIndex.MrPackIndex import MrPackIndex
from src.MrPackFabricMod.MrPackFabricMod import MrPackFabricMod
import json

class MrPack:
    def __init__(self, mrpack_path: str):
        self._mrpack_path = mrpack_path
        self._extract_dir = os.path.join('temp', 'mrpack')
        if os.path.exists(self._extract_dir):
            shutil.rmtree(self._extract_dir)
        os.makedirs(self._extract_dir, exist_ok=True)
        with zipfile.ZipFile(mrpack_path, 'r') as z:
            z.extractall(self._extract_dir)
        
        # Initialize index
        index_path = os.path.join(self._extract_dir, 'modrinth.index.json')
        self._index = MrPackIndex(index_path)

    @property
    def version(self):
        return self._index.version

    @property
    def mods(self):
        return self._index.mods

    def prepare(self):
        self._index.rewrite_updated_file()
        self.prepare_overrides_mods()
        self.prepare_overrides()
        print(f"Veuillez valider le contenu du dossier : {self._extract_dir}\nAppuyez sur Entrée pour continuer...")
        input()
        # Repack dans le .mrpack d'origine
        if os.path.exists(self._mrpack_path):
            os.remove(self._mrpack_path)
        # Crée le zip dans temp, puis renomme
        temp_zip_path = os.path.join('temp', 'temp_mrpack.zip')
        shutil.make_archive(temp_zip_path[:-4], 'zip', self._extract_dir)
        
        # Redéfinir le chemin vers output/filename
        filename = os.path.basename(self._mrpack_path)
        output_dir = 'output'
        os.makedirs(output_dir, exist_ok=True)
        self._mrpack_path = os.path.join(output_dir, filename)
        
        os.rename(temp_zip_path, self._mrpack_path)

    def prepare_overrides_mods(self):
        with open('memory/dev_mods.json', 'r', encoding='utf-8') as f:
            dev_mods = json.load(f)
        mods_dir = os.path.join(self._extract_dir, 'overrides', 'mods')
        if not os.path.isdir(mods_dir):
            return
        for fname in os.listdir(mods_dir):
            if fname.endswith('.jar') or fname.endswith('.jar.disabled'):
                fpath = os.path.join(mods_dir, fname)
                mod = MrPackFabricMod(fpath)
                mod.change_file_extension_with_updated_status()
                if mod.id in dev_mods:
                    os.remove(fpath)

    def prepare_overrides(self, path: str = "temp/mrpack/overrides", override_memory=None):
        override_memory_path = os.path.join('memory', 'override_memory.json')
        is_root = override_memory is None
        if override_memory is None:
            if os.path.isfile(override_memory_path):
                with open(override_memory_path, 'r', encoding='utf-8') as f:
                    try:
                        override_memory = json.load(f)
                    except json.JSONDecodeError:
                        override_memory = {}
            else:
                override_memory = {}
        # Parcours des dossiers
        if not os.path.isdir(path):
            return
        entries = list(os.scandir(path))
        dirs = [entry for entry in entries if entry.is_dir()]
        # Exclure temp/mrpack/overrides/mods
        exclude_dir = os.path.join('temp', 'mrpack', 'overrides', 'mods').replace(os.sep, '/')
        dirs = [entry for entry in dirs if entry.path.replace(os.sep, '/') != exclude_dir]
        files = [entry for entry in entries if entry.is_file()]
        for entry in dirs:
            p = entry.path
            p = p.replace(os.sep, '/')
            mem = override_memory.get(p)
            reset = False
            status = None
            if mem and mem.get('type') == 'directory':
                status = mem.get('status')
                if mem.get('status') == 'TEMP':
                    print(f"Répertoire temporaire détecté : {p}. Voulez-vous le réinitialiser ? (O/N) : ", end="")
                    while True:
                        resp = input().strip().upper()
                        if resp == 'O':
                            reset = True
                            break
                        elif resp == 'N':
                            reset = False
                            break
                        else:
                            print("Réponse invalide. Tapez O ou N : ", end="")
            if reset or not mem or mem.get('type') != 'directory':
                print(f"Répertoire : {p}")
                print("Inclure (I), Exclure (E), Inclure temporairement (T), Gérer au cas par cas (M) ? : ", end="")
                while True:
                    resp = input().strip().upper()
                    if resp == 'I':
                        status = 'INCLUDE'
                        break
                    elif resp == 'E':
                        status = 'EXCLUDE'
                        break
                    elif resp == 'T':
                        status = 'TEMP'
                        break
                    elif resp == 'M':
                        status = 'MIXE'
                        break
                    else:
                        print("Réponse invalide. Tapez I, E, T ou M : ", end="")
                override_memory[p] = {'status': status, 'type': 'directory'}
            if status == 'EXCLUDE':
                shutil.rmtree(p)
                files = [f for f in files if not f.path.startswith(p + os.sep)]
            if status == 'MIXE':
                self.prepare_overrides(p, override_memory)
            if status is None:
                raise Exception(f"Status invalide pour le répertoire : {p}")
        # Parcours des fichiers
        for entry in files:
            p = entry.path
            p = p.replace(os.sep, '/')
            mem = override_memory.get(p)
            reset = False
            status = None
            if mem and mem.get('type') == 'file':
                status = mem.get('status')
                if mem.get('status') == 'TEMP':
                    print(f"Fichier temporaire détecté : {p}. Voulez-vous le réinitialiser ? (O/N) : ", end="")
                    while True:
                        resp = input().strip().upper()
                        if resp == 'O':
                            reset = True
                            break
                        elif resp == 'N':
                            reset = False
                            break
                        else:
                            print("Réponse invalide. Tapez O ou N : ", end="")
            if reset or not mem or mem.get('type') != 'file':
                print(f"Fichier : {p}")
                print("Inclure (I), Exclure (E), Inclure temporairement (T) ? : ", end="")
                while True:
                    resp = input().strip().upper()
                    if resp == 'I':
                        status = 'INCLUDE'
                        break
                    elif resp == 'E':
                        status = 'EXCLUDE'
                        break
                    elif resp == 'T':
                        status = 'TEMP'
                        break
                    else:
                        print("Réponse invalide. Tapez I, E ou T : ", end="")
                override_memory[p] = {'status': status, 'type': 'file'}
            if status == 'EXCLUDE':
                os.remove(p)
            if status is None:
                raise Exception(f"Status invalide pour le fichier : {p}")
        if is_root:
            os.makedirs(os.path.dirname(override_memory_path), exist_ok=True)
            with open(override_memory_path, 'w', encoding='utf-8') as f:
                json.dump(override_memory, f, ensure_ascii=False, indent=2) 