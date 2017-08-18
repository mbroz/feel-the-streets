import logging

log = logging.getLogger(__name__)
def convert_boolean(class_name, prop, val, record):
    if val == "yes": return True
    elif val == "no": return False
    else:
        record.add_type_violation(class_name, prop, val, "bool")
        return None


def convert_enum(prop, val, enum, record):
    try:
        return enum[val]
    except:
        record.add_missing_enum_member(enum.__qualname__, val)
        return None
def convert_float(class_name, prop, val, record):
    val = val.replace(",", ".")
    try:
        return float(val)
    except:
        record.add_type_violation(class_name, prop, val, "float")
        return None
        

def convert_integer(class_name, prop, val, record):
    try:
        return int(val)
    except:
        record.add_type_violation(class_name, prop, val, "int")
        return None