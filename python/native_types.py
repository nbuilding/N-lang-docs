from type import NTypeVars, NGenericType
from enums import EnumType, EnumValue

list_generic = NGenericType("t")
n_list_type = NTypeVars("list", [list_generic])

map_key_generic = NGenericType("k")
map_value_generic = NGenericType("v")
n_map_type = NTypeVars("map", [map_key_generic, map_value_generic])
class NMap(dict):
	def __init__(self, *args, **kw):
		super(NMap, self).__init__(*args, **kw)

cmd_generic = NGenericType("t")
n_cmd_type = NTypeVars("cmd", [cmd_generic])

maybe_generic = NGenericType("t")
n_maybe_type = EnumType("maybe", [
	("yes", [maybe_generic]),
	("none", []),
], [maybe_generic])
none = EnumValue("none")
def yes(value):
	return EnumValue("yes", [value])
