from pathlib import Path
from typing import Optional, Union, List

from .const import CORE_GAME
from .file import load_json, JsonData

# TODO: extracted from metalpike experiment, clean up

ROOT_ASB = 'data/asb'
ROOT_WIKI = 'data/wiki'


def find_mod(manifest, id):
    for file, metadata in manifest['files'].items():
        mod = metadata.get('mod', None)
        if not mod and id == 'core':
            return file, None
        elif mod and mod['id'] == id:
            return file, mod
    return None


def find_mod_ex(obelisk_path, id):
    manifest = load_json(obelisk_path / ROOT_ASB / '_manifest.json')
    for file, metadata in manifest['files'].items():
        mod = metadata.get('mod', None)
        if not mod and id == CORE_GAME:
            return None
        elif mod and mod['id'] == id:
            return mod
    return None


class ObASB:
    data: List[JsonData]

    def __init__(self, obelisk: Path, mod):
        self.obelisk_path = obelisk
        self.data = list()
        self.include(self.get_file_name(mod))

    def get_file_name(self, mod):
        if not mod:
            return 'values.json'

        return mod['id'] + '-' + mod['tag'] + '.json'

    def include(self, filename):
        new_data = load_json(self.obelisk_path / ROOT_ASB / filename)
        self.data += new_data['species']

    def get_dinos(self):
        return self.data

    def get_dino(self, blueprint_path: str):
        for dino in self.get_dinos():
            if dino['blueprintPath'] == blueprint_path:
                return dino


class ObSVGs:
    WILDCARD = '*'

    def __init__(self, path: Path, mod):
        self.mod = mod
        self.path = path / 'spawns'

    def list(self, mod, class_name: str, dino_mod: Optional[str]):
        pattern = '*'
        if mod:
            pattern += '/' + mod['id'] + '-' + mod['tag']
        pattern += f'/Spawning_{class_name}'
        if dino_mod and dino_mod != CORE_GAME:
            pattern += f'_({dino_mod})'
        pattern += '.svg'

        return self.path.glob(pattern)
