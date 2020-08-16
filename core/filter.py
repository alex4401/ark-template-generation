import yaml
from typing import List, Dict


class Filter:
    path: str
    dinoClasses: List[str] = list()
    nameOverrides: Dict[str, str] = dict()
    includeCloningTimes: bool = True


def load_filter(filename: str) -> List[str]:
    with open(filename, 'rt') as fp:
        doc = yaml.safe_load(fp)
    
    doc = doc['filter']
       
    out = Filter()
    out.path = filename
    
    for field_name in out.__annotations__.keys():
        field = doc.get(field_name, None)
        if field != None:
            setattr(out, field_name, field)
    
    return out
