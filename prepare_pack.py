from src.MrPack import MrPack
from src.Version import Version
import os
import shutil
import argparse

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Prepare a Modrinth modpack')
    parser.add_argument('mrpack_path', help='Path to the .mrpack file')
    args = parser.parse_args()
    
    # Clean le dossier temp
    if os.path.exists('temp'):
        shutil.rmtree('temp')
        
    pack = MrPack(args.mrpack_path)
    pack.prepare()
    
    # Créer/mettre à jour la version
    version = Version.get(pack)
    
    # Générer le changelog
    Version.generateChangelog()
