from .blueprint import get_class_name
from .file import JsonData
from .filter import Filter

def get_descriptive_name(flt: Filter, blueprint: JsonData) -> str:
    if not flt.nameOverrides:
    	return blueprint['name']
    
    class_name = get_class_name(blueprint)
    override = flt.nameOverrides.get(class_name, None)
    if override:
    	return override
    
    return blueprint['name']
