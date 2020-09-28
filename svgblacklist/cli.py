import sys
import re
import shutil
import hashlib
import logging

from typing import Dict, Any, List, Iterable, Tuple
from pathlib import Path
from collections import defaultdict
from mwclient import Site
from tqdm import tqdm

from core import blueprint, dino, cli
from core.file import load_json, query, dump_json, JsonData
from core.filter import load_filter, Filter, CORE_GAME
from core.data_context import ObASB, ObSVGs, find_mod_ex

MW_UA = 'https://github.com/alex4401/ark-template-generation.git svgblacklist (User:alexrmski)'


def run():
    mw_server = cli.get_str('site', 'localhost:8084')

    main(mw_server)


def main(mw_address: str):
    mw = Site(mw_address, clients_useragent=MW_UA, path='/')
    mod = find_mod_ex(obelisk_path, flt.modId)
    asb = ObASB(obelisk_path, mod)
    svgs = ObSVGs(svg_path, mod)

    if mod and not flt.modNameOverride:
        flt.modNameOverride = mod['title']

    if output_path.is_dir():
        shutil.rmtree(output_path)
    output_path.mkdir()

    print('Gathering information about local maps')
    results = defaultdict(list)
    with tqdm(total=len(asb.get_dinos())) as t:
        for dino_data in asb.get_dinos():
            matched = False
            bp = blueprint.get_path(dino_data)
            class_name = blueprint.get_class_name(bp)

            if dino.should_skip(flt, dino_data):
                t.update()
                continue

            found = svgs.list(mod, class_name, flt.modId)
            #if options.LinkAgainstMod:
            #    found = list(found)
            #    found += svgContext.list(mod, class_name, options.LinkAgainstMod)

            for file in found:
                t.total += 1

                world = file.relative_to(svg_path).parts[1]
                world = flt.worldNameOverrides.get(world, world)

                if world in flt.skipMaps:
                    t.update()
                    continue

                dino_name = dino.get_descriptive_name(flt, dino_data)

                name = ''
                if mod:
                    name += 'Mod ' + flt.modNameOverride + ' '
                name += 'Spawning ' + dino_name + ' ' + world + '.svg'
                results[bp].append((file, world, name))
                t.update()

            t.update()

    item_count = sum([len(files) for _, files in results.items()])

    wiki_hashes = build_hash_db(mw, item_count)

    print('Comparing local versions against remote data')
    checked_files = set()
    files_to_update = list()
    with tqdm(total=item_count) as t:
        for bp, files in results.items():
            for original_file, _, target_file in files:
                if target_file in checked_files:
                    print(f'Collision found:\t', target_file)
                    t.update()
                    continue
                checked_files.add(target_file)

                input_data = original_file.read_text()
                sha1 = hashlib.sha1(input_data.encode('utf-8')).hexdigest()

                wiki_hash = wiki_hashes.get('File:' + target_file, None)
                if wiki_hash == None:
                    print(target_file, 'not in hash database.')
                    files_to_update.append((original_file, target_file))
                elif wiki_hash != sha1:
                    print(target_file, 'is out of date:', wiki_hash, sha1)
                    files_to_update.append((original_file, target_file))
                t.update()

    print('Copying modified files on disk')
    for original_file, target_file in files_to_update:
        target = (output_path / target_file)
        if target.is_file():
            continue

        input_data = original_file.read_text()
        target.write_text(input_data)