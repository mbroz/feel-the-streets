import json
from shared.semantic_change import ChangeType
from shared.diff_utils import ChangeKind
from shared.humanization_utils import underscored_to_words

def get_dictchange_description(dictchange):
    if dictchange.kind is ChangeKind.add:
        return _("Property {property} was added with value {value}").format(property=dictchange.key, value=repr(dictchange.new_value))
    elif dictchange.kind is ChangeKind.change:
        return _("Property {property} changed from {old} to {new}").format(property=dictchange.key, old=repr(dictchange.old_value), new=repr(dictchange.new_value))
    elif dictchange.kind is ChangeKind.remove:
        return _("Property {property} was removed").format(property=dictchange.key)
    else:
        raise RuntimeError("Unknown dictchange kind %s."%dictchange.kind)

def get_change_description(change, include_geometry_changes=False):
    if change.type is ChangeType.delete:
        return "* " + _("Object {osm_id} was deleted").format(osm_id=change.osm_id) + "\n"
    elif change.type is ChangeType.create:
        msg = "* " + _("New object created") + "\n"
        for propchange in change.property_changes:
            if propchange.key == "data":
                data = json.loads(propchange.new_value)
                for key, val in data.items():
                    msg += "{0}: {1}\n".format(underscored_to_words(key), repr(val))
            else:
                if propchange.key == "geometry" and not include_geometry_changes:
                    continue
                msg += "{0}: {1}\n".format(propchange.key, propchange.new_value)
        return msg
    elif change.type is ChangeType.update:
        msg = "* " + _("Object {osm_id} was changed").format(osm_id=change.osm_id) + "\n"
        for subchange in change.property_changes:
            if subchange.key == "geometry" and not include_geometry_changes:
                continue
            msg += get_dictchange_description(subchange) + "\n"
        for subchange in change.data_changes:
            msg += get_dictchange_description(subchange) + "\n"
        return msg
    else:
        raise RuntimeError("Invalid semantic change type %s."%change.type)