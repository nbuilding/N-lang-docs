import importlib
import lark
import os.path
from lark import Lark
from colorama import Fore, Style

from variable import Variable
from function import Function
from native_function import NativeFunction
from type import NType, NGenericType, NAliasType, NTypeVars, NModule, apply_generics, apply_generics_to, resolve_equal_types
from enums import EnumType, EnumValue, EnumPattern
from native_function import NativeFunction
from native_types import n_list_type, n_cmd_type
from cmd import Cmd
from type_check_error import TypeCheckError, display_type
from display import display_value
from operation_types import binary_operation_types, unary_operation_types, comparable_types, iterable_types
from file import File
from imported_error import ImportedError
import native_functions
from syntax_error import format_error
from classes import NClass, NConstructor

basepath = os.path.dirname(__file__)
syntaxpath = os.path.abspath(os.path.join(basepath, "syntax.lark"))

def parse_file(file_path, base_path):
	import_scope = Scope(base_path=base_path, file_path=file_path)
	native_functions.add_funcs(import_scope)

	with open(syntaxpath, "r") as f:
		parse = f.read()
	n_parser = Lark(parse, start="start", propagate_positions=True)

	with open(file_path, "r") as f:
		file = File(f, name=os.path.relpath(file_path, start=base_path))

	try:
		tree = file.parse(n_parser)
	except lark.exceptions.UnexpectedCharacters as e:
		format_error(e, os.path.relpath(file_path, start=base_path))

	return import_scope, tree, file

async def eval_file(file_path, base_path):
	import_scope, tree, _ = parse_file(file_path, base_path)

	import_scope.variables = {**import_scope.variables, **(await parse_tree(tree, import_scope)).variables}
	return import_scope

def type_check_file(file_path, base_path):
	import_scope, tree, text_file = parse_file(file_path, base_path)

	scope = type_check(tree, import_scope)
	import_scope.variables = {**import_scope.variables, **scope.variables}
	import_scope.public_types = {**import_scope.public_types, **scope.public_types}
	import_scope.errors += scope.errors[:]
	import_scope.warnings += scope.warnings[:]
	return import_scope, text_file

def type_check(tree, import_scope):
	scope = import_scope.new_scope(inherit_errors=False)
	if tree.data == "start":
		for child in tree.children:
			scope.type_check_command(child)
	else:
		scope.errors.append(TypeCheckError(tree, "Internal issue: I cannot type check from a non-starting branch."))
	return scope

async def parse_tree(tree, import_scope):
	if tree.data == "start":
		scope = import_scope.new_scope(inherit_errors=False)
		for child in tree.children:
			await scope.eval_command(child)
		return scope
	else:
		raise SyntaxError("Unable to run parse_tree on non-starting branch")


def get_destructure_pattern(name):
	if type(name) == lark.Tree:
		if name.data == "record_pattern":
			names = []
			for pattern in name.children:
				if type(pattern) == lark.Token:
					names.append((pattern.value, (pattern.value, pattern)))
				else:
					key, value = pattern.children
					names.append((key.value, get_destructure_pattern(value)))
			return (dict(names), name)
		elif name.data == "tuple_pattern":
			return (tuple(get_destructure_pattern(pattern) for pattern in name.children), name)
	return (None if name.value == "_" else name.value, name)

def get_conditional_destructure_pattern(tree):
	if type(tree) == lark.Tree:
		if tree.data == "list_pattern":
			patterns = []
			for pattern in tree.children:
				patterns.append(get_conditional_destructure_pattern(pattern))
			return (patterns, tree)
		elif tree.data == "enum_pattern":
			enum_name, *pattern_trees = tree.children
			patterns = []
			for pattern in pattern_trees:
				patterns.append(get_conditional_destructure_pattern(pattern))
			return (EnumPattern(enum_name, patterns), tree)
	return get_destructure_pattern(tree)

def pattern_to_name(pattern_and_src):
	pattern, _ = pattern_and_src
	if isinstance(pattern, str):
		return pattern
	else:
		return "<destructuring pattern>"

class Scope:
	def __init__(self, parent=None, parent_function=None, errors=None, warnings=None, base_path="", file_path=""):
		self.parent = parent
		self.parent_function = parent_function
		self.variables = {}
		self.types = {}
		self.public_types = {}
		self.errors = errors if errors is not None else []
		self.warnings = warnings if warnings is not None else []
		# The path of the directory containing the initial file. Used to
		# determine the relative path of a file to the starting file.
		self.base_path = base_path
		# The path of the file the Scope is associated with.
		self.file_path = file_path

	def new_scope(self, parent_function=None, inherit_errors=True):
		return Scope(
			self,
			parent_function=parent_function or self.parent_function,
			errors=self.errors if inherit_errors else [],
			warnings=self.warnings if inherit_errors else [],
			base_path=self.base_path,
			file_path=self.file_path,
		)

	def get_variable(self, name, err=True):
		variable = self.variables.get(name)
		if variable is None:
			if self.parent:
				return self.parent.get_variable(name, err=err)
			elif err:
				raise NameError("You tried to get a variable/function `%s`, but it isn't defined." % name)
		else:
			return variable

	def get_type(self, name, err=True):
		scope_type = self.types.get(name)
		if scope_type is None:
			if self.parent:
				return self.parent.get_type(name, err=err)
			elif err:
				raise NameError("You tried to get a type `%s`, but it isn't defined." % name)
		else:
			return scope_type

	def get_parent_function(self):
		if self.parent_function is None:
			if self.parent:
				return self.parent.get_parent_function()
			else:
				return None
		else:
			return self.parent_function

	def get_module_type(self, module_type, err=True):
		*modules, type_name = module_type.children
		if len(modules) > 0:
			current_module = self.get_variable(modules[0].value, err=err)
			if current_module is None:
				self.errors.append(TypeCheckError(modules[0], "I can't find `%s` from this scope." % modules[0].value))
				return None
			current_module = current_module.type
			if not isinstance(current_module, NModule):
				self.errors.append(TypeCheckError(modules[0], "%s is not a module." % modules[0].value))
				return None
			for module in modules[1:]:
				current_module = current_module.get(module.value)
				if not isinstance(current_module, NModule):
					self.errors.append(TypeCheckError(module, "%s is not a module." % module.value))
					return None
			n_type = current_module.types.get(type_name.value)
			if n_type is None:
				self.errors.append(TypeCheckError(type_name, "The module doesn't export a type `%s`." % type_name.value))
				return None
		else:
			n_type = self.get_type(type_name.value, err=err)
			if n_type is None:
				self.errors.append(TypeCheckError(module_type, "I don't know what type you're referring to by `%s`." % type_name.value))
				return None
		if n_type == "invalid":
			return None
		else:
			return n_type

	def parse_type(self, tree_or_token, err=True):
		if type(tree_or_token) == lark.Tree:
			if tree_or_token.data == "with_typevars":
				module_type, *typevars = tree_or_token.children
				typevar_type = self.get_module_type(module_type, err=err)
				parsed_typevars = [self.parse_type(typevar, err=err) for typevar in typevars]
				if typevar_type is None:
					return None
				elif isinstance(typevar_type, NAliasType) or isinstance(typevar_type, NTypeVars):
					# Duck typing :sunglasses:
					if len(typevars) < len(typevar_type.typevars):
						self.errors.append(TypeCheckError(tree_or_token, "%s expects %d type variable(s)." % (name.value, len(typevar_type.typevars))))
						return None
					elif len(typevars) > len(typevar_type.typevars):
						self.errors.append(TypeCheckError(tree_or_token, "%s only expects %d type variable(s)." % (name.value, len(typevar_type.typevars))))
						return None
					return typevar_type.with_typevars(parsed_typevars) if None not in parsed_typevars else None
				else:
					self.errors.append(TypeCheckError(tree_or_token, "%s doesn't take any type variables." % name.value))
					return None
			elif tree_or_token.data == "tupledef":
				tuple_type = [self.parse_type(child, err=err) for child in tree_or_token.children]
				return tuple_type if None not in tuple_type else None
			elif tree_or_token.data == "recorddef":
				record_type = {entry.children[0].value: self.parse_type(entry.children[1], err=err) for entry in tree_or_token.children}
				return record_type if None not in record_type.values() else None
			elif tree_or_token.data == "module_type":
				n_type = self.get_module_type(tree_or_token, err=err)
				if n_type is None:
					return None
				elif (isinstance(n_type, NAliasType) or isinstance(n_type, NTypeVars)) and len(n_type.typevars) > 0:
					self.errors.append(TypeCheckError(tree_or_token, "%s expects %d type variables." % (type_name.value, len(n_type.typevars))))
					return None
				elif isinstance(n_type, NAliasType):
					return n_type.with_typevars()
				return n_type
			elif err:
				raise NameError("Type annotation of type %s; I am not ready for this." % tree_or_token.data)
			else:
				self.errors.append(TypeCheckError(tree_or_token, "Internal problem: encountered a type annotation type %s." % tree_or_token.data))
				return None
		elif tree_or_token.type == "UNIT":
			return "unit"
		elif err:
			raise NameError("Type annotation token of type %s; I am not ready for this." % tree_or_token.data)
		else:
			self.errors.append(TypeCheckError(tree_or_token, "Internal problem: encountered a type annotation token type %s." % tree_or_token.data))
			return None

	def get_name_type(self, name_type, err=True, get_type=True):
		pattern = get_destructure_pattern(name_type.children[0])
		if len(name_type.children) == 1:
			# No type annotation given, so it's implied
			return pattern, 'infer'
		else:
			return pattern, self.parse_type(name_type.children[1], err) if get_type else 'whatever'

	"""
	This is to be used to get the NClass value for evaluating classes
	"""
	def get_class_val(self, modifiers, name, class_value):
		scope = Scope()
		for ins in class_value.children:
			type_check_class_command(ins, scope)
		return NClass(None, None, None, None)

		# TODO get type_check_class_command working

	"""
	This is meant as the type checker to get_class_val
	as not all instructions are allowed to be a class_instruction
	and some are exclusive to it
	"""
	def type_check_class_command(self, tree, scope):
		if tree.data != "instruction":
			scope.errors.append(TypeCheckError(tree, "Internal problem: I am unable to deal with %s inside a class." % tree.data))
			return False

		command = tree.children[0]

		if command.data == "declare":
			modifiers, name_type, value = command.children
			pattern, ty = scope.get_name_type(name_type, err=False)
			name = pattern_to_name(pattern)

			value_type = scope.type_check_expr(value)
			resolved_value_type = apply_generics(value_type, ty)
			if ty == 'infer':
				ty = resolved_value_type
			else:
				_, incompatible = resolve_equal_types(ty, resolved_value_type)
				if incompatible:
					scope.errors.append(TypeCheckError(value, "You set %s, which is defined to be a %s, to what evaluates to a %s." % (name, display_type(ty), display_type(value_type))))

			public = any(modifier.type == "PUBLIC" for modifier in modifiers.children)
			scope.assign_to_pattern(pattern, ty, True, None, public)
		elif command.data == "enum_definition":
			modifiers, type_def, constructors = command.children
			type_name, sc, typevars = scope.get_name_typevars(type_def)
			variants = []
			enum_type = EnumType(type_name.value, variants, typevars)
			scope.types[type_name] = enum_type
			if any(modifier.type == "PUBLIC" for modifier in modifiers.children):
				scope.public_types[type_name] = scope.types[type_name]
			for constructor in constructors.children:
				modifiers, constructor_name, *types = constructor.children
				public = any(modifier.type == "PUBLIC" for modifier in modifiers.children)
				types = [sc.parse_type(type_token, err=False) for type_token in types]
				variants.append((constructor_name.value, types))
				if constructor_name.value in scope.variables:
					scope.errors.append(TypeCheckError(constructor_name, "You've already defined `%s` in this scope." % constructor_name.value))
				if len(types) >= 1:
					scope.variables[constructor_name.value] = NativeFunction(scope, [("idk", arg_type) for arg_type in types], enum_type, id, public=public)
				else:
					scope.variables[constructor_name.value] = Variable(enum_type, "I don't think this is used", public=public)
		elif command.data == "class_constuctor":
			args, instructions = command.children
			contructor = NConstructor(args, instructions)
			# help
		else:
			scope.errors.append(TypeCheckError(command, "Internal problem: I am unable to deal with the command %s inside a class." % command.data))




	"""
	This method is meant to be usable for both evaluation and type checking.
	"""
	def assign_to_pattern(self, pattern_and_src, value_or_type, warn=False, path=None, public=False):
		path_name = path or "the value"
		pattern, src = pattern_and_src
		if isinstance(pattern, dict):
			is_dict = isinstance(value_or_type, dict)
			if is_dict:
				# Should this be an error? Warning?
				unused_keys = [key for key in value_or_type.keys() if key not in pattern]
				if len(unused_keys) > 0:
					self.errors.append(TypeCheckError(src, "%s (%s) has field(s) %s, but you haven't destructured them. (Hint: use `_` to denote unused fields.)" % (display_type(value_or_type), path_name, ", ".join(unused_keys))))
			else:
				if warn:
					if value_or_type is not None:
						self.errors.append(TypeCheckError(src, "I can't destructure %s as a record because %s is not a record." % (path_name, display_type(value_or_type))))
				else:
					raise TypeError("Destructuring non-record as record.")
			for key, (sub_pattern, parse_src) in pattern.items():
				value = value_or_type.get(key) if is_dict else None
				if is_dict and value is None:
					if warn:
						self.errors.append(TypeCheckError(parse_src, "I can't get the field %s from %s because %s doesn't have that field." % (key, path_name, display_type(value_or_type))))
					else:
						raise TypeError("Given record doesn't have a key %s." % key)
				self.assign_to_pattern((sub_pattern, parse_src), value, warn, "%s.%s" % (path or "<record>", key), public)
		elif isinstance(pattern, tuple):
			# I believe the interpreter uses actual Python tuples, while the
			# type checker uses lists for tuple types. We should fix that for
			# the type checker.
			is_tuple = isinstance(value_or_type, list) if warn else isinstance(value_or_type, tuple)
			if not is_tuple:
				if warn:
					if value_or_type is not None:
						self.errors.append(TypeCheckError(src, "I can't destructure %s as a tuple because %s is not a tuple." % (path_name, display_type(value_or_type))))
				else:
					raise TypeError("Destructuring non-record as record.")
			if is_tuple and len(pattern) != len(value_or_type):
				if warn:
					if len(pattern) > len(value_or_type):
						_, parse_src = pattern[len(value_or_type)]
						self.errors.append(TypeCheckError(parse_src, "I can't destructure %d items from a %s." % (len(pattern), display_type(value_or_type))))
					else:
						self.errors.append(TypeCheckError(src, "I can't destructure only %d items from a %s. (Hint: use `_` to denote unused members of a destructured tuple.)" % (len(pattern), display_type(value_or_type))))
				else:
					raise TypeError("Number of destructured values from tuple doesn't match tuple length.")
			for i, (sub_pattern, parse_src) in enumerate(pattern):
				value = value_or_type[i] if is_tuple and i < len(value_or_type) else None
				self.assign_to_pattern((sub_pattern, parse_src), value, warn, "%s.%d" % (path or "<tuple>", i), public)
		elif pattern is not None:
			name = pattern
			if warn and name in self.variables:
				self.errors.append(TypeCheckError(src, "You've already defined `%s`." % name))
			self.variables[name] = Variable(value_or_type, value_or_type, public)

	"""
	Sets variables from a pattern given a value or a type and returns whether
	the entire pattern matched.

	This is used by both type-checking (with warn=True) and interpreting
	(warn=False). During type-checking, `value_or_type` is the type (notably,
	tuples are lists), so it must determine whether it's even reasonable to
	destructure the type (for example, it doesn't make sense to destructure a
	record as a list), and error accordingly. During interpreting,
	`value_or_type` is the actual value, and thanks to the type-checker, the
	value should be guaranteed to fit the pattern.

	- warn=True - Is the pattern valid?
	- warn=False - Does the pattern match?

	Note that this sets variables while checking the pattern, so it's possible
	that variables are assigned even if the entire pattern doesn't match.
	Fortunately, this is only used in cases where the conditional let would
	create a new scope (such as in an if statement), so the extra variables can
	be discarded if the pattern ends up not matching.

	NOTE: This must return True if warn=True. (In other words, don't short
	circuit if a pattern fails to match.)
	"""
	def assign_to_cond_pattern(self, cond_pattern_and_src, value_or_type, warn=False, path=None):
		path_name = path or "the value"
		pattern, src = cond_pattern_and_src
		if isinstance(pattern, EnumPattern):
			if warn:
				if not isinstance(value_or_type, EnumType):
					if value_or_type is not None:
						self.errors.append(TypeCheckError(src, "I cannot destructure %s as an enum because it's a %s." % (path_name, display_type(value_or_type))))
					return True
				else:
					variant_types = value_or_type.get_types(pattern.variant)
					if variant_types is None:
						self.errors.append(TypeCheckError(src, "%s has no variant %s because it's a %s." % (path_name, pattern.variant, display_type(value_or_type))))
						return True
					elif len(pattern.patterns) < len(variant_types):
						self.errors.append(TypeCheckError(src, "Variant %s has %d fields, but you only destructure %d of them." % (pattern.variant, len(variant_types), len(pattern.patterns))))
						return True
					elif len(pattern.patterns) > len(variant_types):
						self.errors.append(TypeCheckError(pattern.patterns[len(variant_types)][1], "Variant %s only has %d fields." % (pattern.variant, len(variant_types))))
						return True
			else:
				if not isinstance(value_or_type, EnumValue):
					raise TypeError("Destructuring non-enum as enum.")
				elif pattern.variant != value_or_type.variant:
					return False
			for i, (sub_pattern, parse_src) in enumerate(pattern.patterns):
				if warn:
					value = variant_types[i]
				else:
					value = value_or_type.values[i]
				valid = self.assign_to_cond_pattern((sub_pattern, parse_src), value, warn, "%s.%s#%d" % (path or "<enum>", pattern.variant, i + 1))
				if not valid:
					return False
		if isinstance(pattern, list):
			if warn:
				if not isinstance(value_or_type, NTypeVars) or value_or_type.base_type is not n_list_type:
					if value_or_type is not None:
						self.errors.append(TypeCheckError(src, "I cannot destructure %s as a list because it's a %s." % (path_name, display_type(value_or_type))))
					return True
				contained_type = value_or_type.typevars[0]
			else:
				if not isinstance(value_or_type, list):
					raise TypeError("Destructuring non-list as list.")
			if not warn and len(value_or_type) != len(pattern):
				return False
			for i, (sub_pattern, parse_src) in enumerate(pattern):
				valid = self.assign_to_cond_pattern((sub_pattern, parse_src), contained_type if warn else value_or_type[i], warn, "%s[%d]" % (path or "<enum variant>", i))
				if not valid:
					return False
		else:
			self.assign_to_pattern(cond_pattern_and_src, value_or_type, warn, path)
		return True

	async def eval_record_entry(self, entry):
		if type(entry) is lark.Tree:
			return entry.children[0].value, await self.eval_expr(entry.children[1])
		else:
			return entry.value, self.eval_value(entry)

	def eval_value(self, value):
		if value.type == "NUMBER":
			if "." in str(value.value):
				return float(value)
			return int(value)
		elif value.type == "STRING":
			return bytes(value[1:-1], 'utf-8').decode('unicode_escape')
		elif value.type == "BOOLEAN":
			if value.value == "false":
				return False
			elif value.value == "true":
				return True
			else:
				raise SyntaxError("Unexpected boolean value %s" % value.value)
		elif value.type == "NAME":
			return self.get_variable(value.value).value
		elif value.type == "UNIT":
			return ()
		else:
			raise SyntaxError("Unexpected value type %s value %s" % (value.type, value.value))

	"""
	Evaluate a parsed expression with Trees and Tokens from Lark.
	"""
	async def eval_expr(self, expr):
		if type(expr) is lark.Token:
			return self.eval_value(expr)

		if expr.data == "ifelse_expr":
			condition, if_true, if_false = expr.children
			scope = self.new_scope()
			if condition.data == "conditional_let":
				pattern, value = condition.children
				if scope.assign_to_cond_pattern(get_conditional_destructure_pattern(pattern), await self.eval_expr(value)):
					return await scope.eval_expr(if_true)
				else:
					return await scope.eval_expr(if_false)
			elif await self.eval_expr(condition):
				return await self.eval_expr(if_true)
			else:
				return await self.eval_expr(if_false)
		elif expr.data == "function_def" or expr.data == "anonymous_func":
			if expr.data == "function_def":
				arguments, returntype, codeblock = expr.children
			else:
				arguments, returntype, *codeblock = expr.children
				codeblock = lark.tree.Tree("code_block", codeblock)
			if len(arguments.children) > 0 and arguments.children[0].data == "generic_declaration":
				_, *arguments = arguments.children
			else:
				arguments = arguments.children
			return Function(
				self,
				[self.get_name_type(arg, get_type=False) for arg in arguments],
				returntype,
				codeblock
			)
		elif expr.data == "function_callback" or expr.data == "function_callback_pipe":
			if expr.data == "function_callback":
				function, *arguments = expr.children[0].children
			else:
				mainarg = expr.children[0]
				function, *arguments = expr.children[1].children
				arguments.append(mainarg)
			arg_values = []
			for arg in arguments:
				arg_values.append(await self.eval_expr(arg))
			return await (await self.eval_expr(function)).run(arg_values)
		elif expr.data == "or_expression":
			left, _, right = expr.children
			return await self.eval_expr(left) or await self.eval_expr(right)
		elif expr.data == "and_expression":
			left, _, right = expr.children
			return await self.eval_expr(left) and await self.eval_expr(right)
		elif expr.data == "not_expression":
			_, value = expr.children
			return not await self.eval_expr(value)
		elif expr.data == "compare_expression":
			# compare_expression chains leftwards. It's rather complex because it
			# chains but doesn't accumulate a value unlike addition. Also, there's a
			# lot of comparison operators.
			# For example, (1 = 2) = 3 (in code as `1 = 2 = 3`).
			left, comparison, right = expr.children
			if left.data == "compare_expression":
				# If left side is a comparison, it also needs to be true for the
				# entire expression to be true.
				if not await self.eval_expr(left):
					return False
				# Use the left side's right value as the comparison value for this
				# comparison. For example, for `1 = 2 = 3`, where `1 = 2` is `left`,
				# we'll use `2`, which is `left`'s `right`.
				left = left.children[2]
			comparison = comparison.type
			if comparison == "EQUALS":
				return await self.eval_expr(left) == await self.eval_expr(right)
			elif comparison == "GORE":
				return await self.eval_expr(left) >= await self.eval_expr(right)
			elif comparison == "LORE":
				return await self.eval_expr(left) <= await self.eval_expr(right)
			elif comparison == "LESS":
				return await self.eval_expr(left) < await self.eval_expr(right)
			elif comparison == "GREATER":
				return await self.eval_expr(left) > await self.eval_expr(right)
			elif comparison == "NEQUALS":
				return await self.eval_expr(left) != await self.eval_expr(right)
			else:
				raise SyntaxError("Unexpected operation for compare_expression: %s" % comparison)
		elif expr.data == "sum_expression":
			left, operation, right = expr.children
			if operation.type == "ADD":
				return await self.eval_expr(left) + await self.eval_expr(right)
			elif operation.type == "SUBTRACT":
				return await self.eval_expr(left) - await self.eval_expr(right)
			else:
				raise SyntaxError("Unexpected operation for sum_expression: %s" % operation)
		elif expr.data == "product_expression":
			left, operation, right = expr.children
			if operation.type == "MULTIPLY":
				return await self.eval_expr(left) * await self.eval_expr(right)
			elif operation.type == "DIVIDE":
				return await self.eval_expr(left) / await self.eval_expr(right)
			elif operation.type == "ROUNDDIV":
				return await self.eval_expr(left) // await self.eval_expr(right)
			elif operation.type == "MODULO":
				return await self.eval_expr(left) % await self.eval_expr(right)
			else:
				raise SyntaxError("Unexpected operation for product_expression: %s" % operation)
		elif expr.data == "exponent_expression":
			left, _, right = expr.children
			return await self.eval_expr(left) ** await self.eval_expr(right)
		elif expr.data == "unary_expression":
			operation, value = expr.children
			if operation.type == "NEGATE":
				return -await self.eval_expr(value)
			elif operation.type == "NOT":
				return not await self.eval_expr(value)
			else:
				raise SyntaxError("Unexpected operation for unary_expression: %s" % operation)
		elif expr.data == "char":
			val = expr.children[0]
			if type(val) == lark.Tree:
				code = val.children[0].value
				if code == "n":
					return "\n"
				elif code == "t":
					return "\t"
				elif code == "r":
					return "\r"
				else:
					raise SyntaxError("Unexpected escape code: %s" % code)
			else:
				return val.value
		elif expr.data == "value":
			token_or_tree = expr.children[0]
			if type(token_or_tree) is lark.Tree:
				return await self.eval_expr(token_or_tree)
			else:
				return self.eval_value(token_or_tree)
		elif expr.data == "impn":
			file_path = os.path.join(os.path.dirname(self.file_path), expr.children[0] + ".n")
			val = await eval_file(file_path, self.base_path)
			holder = {}
			for key in val.variables.keys():
				if val.variables[key].public:
					holder[key] = val.variables[key].value
			return NModule(expr.children[0] + ".n", holder)
		elif expr.data == "record_access":
			return (await self.eval_expr(expr.children[0]))[expr.children[1].value]
		elif expr.data == "tupleval":
			values = []
			for e in expr.children:
				values.append(await self.eval_expr(e))
			return tuple(values)
		elif expr.data == "listval":
			values = []
			for e in expr.children:
				values.append(await self.eval_expr(e))
			return values
		elif expr.data == "recordval":
			entries = []
			for entry in expr.children:
				entries.append(await self.eval_record_entry(entry))
			return dict(entries)
		elif expr.data == "await_expression":
			value, _ = expr.children
			command = await self.eval_expr(value)
			_, using_await_future, cmd_resume_future = self.get_parent_function()
			if not using_await_future.done():
				using_await_future.set_result((True, None))
				await cmd_resume_future
			if isinstance(command, Cmd):
				return await command.eval()
			else:
				# Sometimes cmd functions will return the contained value if
				# they don't use await. That's fine because type checking will
				# allow it, but the interpreter doesn't know that.
				return command
		else:
			print('(parse tree):', expr)
			raise SyntaxError("Unexpected command/expression type %s" % expr.data)

	"""
	Evaluates a command given parsed Trees and Tokens from Lark.
	"""
	async def eval_command(self, tree):
		if tree.data == "code_block":
			exit, value = (False, None)
			for instruction in tree.children:
				exit, value = await self.eval_command(instruction)
				if exit:
					return exit, value
			return exit, value
		elif tree.data != "instruction":
			raise SyntaxError("Command %s not implemented" % (tree.data))

		command = tree.children[0]

		if command.data == "imp":
			import_name = command.children[0].value
			lib = importlib.import_module("libraries." + import_name)
			self.variables[import_name] = Variable(None, NModule(import_name, {
				key: NativeFunction.from_imported(self, types, getattr(lib, key))
				for key, types in lib._values().items()
			}))
			try:
				lib._prepare(self)
			except AttributeError:
				# Apparently it's more Pythonic to use try/except than hasattr
				pass
		elif command.data == "for":
			var, iterable, code = command.children
			pattern, _ = self.get_name_type(var, get_type=False)
			for i in range(int(iterable)):
				scope = self.new_scope()

				scope.assign_to_pattern(pattern, i)
				exit, value = await scope.eval_command(code)
				if exit:
					return True, value
		elif command.data == "return":
			return (True, await self.eval_expr(command.children[0]))
		elif command.data == "declare":
			modifiers, name_type, value = command.children
			pattern, _ = self.get_name_type(name_type, get_type=False)
			public = any(modifier.type == "PUBLIC" for modifier in modifiers.children)
			self.assign_to_pattern(pattern, await self.eval_expr(value), False, None, public)
		elif command.data == "vary":
			name, value = command.children
			self.get_variable(name.value).value = await self.eval_expr(value)
		elif command.data == "if":
			condition, body = command.children
			scope = self.new_scope()
			if condition.data == "conditional_let":
				pattern, value = condition.children
				yes = scope.assign_to_cond_pattern(get_conditional_destructure_pattern(pattern), await self.eval_expr(value))
			else:
				yes = await self.eval_expr(condition)
			if yes:
				exit, value = await scope.eval_command(body)
				if exit:
					return (True, value)
		elif command.data == "ifelse":
			condition, if_true, if_false = command.children
			scope = self.new_scope()
			if condition.data == "conditional_let":
				pattern, value = condition.children
				yes = scope.assign_to_cond_pattern(get_conditional_destructure_pattern(pattern), await self.eval_expr(value))
			else:
				yes = await self.eval_expr(condition)
			if yes:
				exit, value = await scope.eval_command(if_true)
			else:
				exit, value = await self.new_scope().eval_command(if_false)
			if exit:
				return (True, value)
		elif command.data == "enum_definition":
			_, type_def, constructors = command.children
			type_name, *_ = type_def.children
			enum_type = NType(type_name.value)
			self.types[type_name.value] = enum_type
			for constructor in constructors.children:
				modifiers, constructor_name, *types = constructor.children
				public = any(modifier.type == "PUBLIC" for modifier in modifiers.children)
				if len(types) >= 1:
					self.variables[constructor_name] = NativeFunction(self, [("idk", arg_type) for arg_type in types], enum_type, EnumValue.construct(constructor_name), public=public)
				else:
					self.variables[constructor_name] = Variable(enum_type, EnumValue(constructor_name), public=public)
		elif command.data == "alias_definition":
			# Type aliases are purely for type checking so they do nothing at runtime
			pass
		elif command.data == "class_definition":
			modifiers, name, class_args, class_body = command.children
			public = any(modifier.type == "PUBLIC" for modifier in modifiers.children)
			self.variables[name.value] = NConstructor(
				self,
				[self.get_name_type(arg, get_type=False) for arg in class_args.children],
				class_body,
				public
			)
		else:
			await self.eval_expr(command)

		# No return
		return (False, None)

	"""
	A helper function to generalize getting a type name and its type variables,
	used by enum and type alias definitions. It also puts the type variables in
	a temporary scope so that the type definition can use them.
	"""
	def get_name_typevars(self, type_def):
		type_name, *type_typevars = type_def.children
		if type_name.value in self.types:
			self.errors.append(TypeCheckError(type_name, "You've already defined the type `%s`." % type_name.value))
		scope = self.new_scope()
		typevars = []
		for typevar_name in type_typevars:
			typevar = NGenericType(typevar_name.value)
			if typevar_name.value in scope.types:
				self.errors.append(TypeCheckError(typevar_name, "You've already used the generic type `%s`." % typevar_name.value))
			scope.types[typevar_name.value] = typevar
			typevars.append(typevar)
		return type_name, scope, typevars

	def get_record_entry_type(self, entry):
		if type(entry) is lark.Tree:
			return entry.children[0].value, self.type_check_expr(entry.children[1])
		else:
			return entry.value, self.get_value_type(entry)

	def get_value_type(self, value):
		if type(value) == lark.Tree:
			if value.data == "char":
				return "char"
		if value.type == "NUMBER":
			if "." in str(value.value):
				return "float"
			return "int"
		elif value.type == "STRING":
			return "str"
		elif value.type == "BOOLEAN":
			return "bool"
		elif value.type == "NAME":
			variable = self.get_variable(value.value, err=False)
			if variable is None:
				self.errors.append(TypeCheckError(value, "You haven't yet defined %s." % value.value))
				return None
			else:
				return variable.type
		elif value.type == "UNIT":
			return "unit"

		self.errors.append(TypeCheckError(value, "Internal problem: I don't know the value type %s." % value.type))

	"""
	Type checks an expression and returns its type.
	"""
	def type_check_expr(self, expr):
		if type(expr) is lark.Token:
			return self.get_value_type(expr)

		if expr.data == "ifelse_expr":
			condition, if_true, if_false = expr.children
			scope = self.new_scope()
			if condition.data == "conditional_let":
				pattern, value = condition.children
				eval_type = self.type_check_expr(value)
				scope.assign_to_cond_pattern(get_conditional_destructure_pattern(pattern), eval_type, True)
			else:
				cond_type = self.type_check_expr(condition)
				if cond_type is not None and cond_type != "bool":
					self.errors.append(TypeCheckError(condition, "The condition here should be a boolean, not a %s." % display_type(cond_type)))
			if_true_type = scope.type_check_expr(if_true)
			if_false_type = scope.type_check_expr(if_false)
			if if_true_type is None or if_false_type is None:
				return None
			return_type, incompatible = resolve_equal_types(if_true_type, if_false_type)
			if incompatible:
				self.errors.append(TypeCheckError(expr, "The branches of the if-else expression should have the same type, but the true branch has type %s while the false branch has type %s." % (display_type(if_true_type), display_type(if_false_type))))
				return None
			if type(condition.children[0]) is lark.Token:
				if condition.children[0].value == "true":
					self.warnings.append(TypeCheckError(condition, "The else statement of the expression will never run."))
				if condition.children[0].value == "false":
					self.warnings.append(TypeCheckError(condition, "The if statement of the expression will never run."))
			return return_type
		elif expr.data == "function_def" or expr.data == "anonymous_func":
			if expr.data == "function_def":
				arguments, returntype, codeblock = expr.children
			else:
				arguments, returntype, *cb = expr.children
				codeblock = lark.tree.Tree("code_block", cb)
			generic_types = []
			if len(arguments.children) > 0 and arguments.children[0].data == "generic_declaration":
				generics, *arguments = arguments.children
				wrap_scope = self.new_scope()
				for generic in generics.children:
					if generic.value in wrap_scope.types:
						self.errors.append(TypeCheckError(generic, "You already defined a generic type with this name."))
					generic_type = NGenericType(generic.value)
					wrap_scope.types[generic.value] = generic_type
					generic_types.append(generic_type)
			else:
				arguments = arguments.children
				wrap_scope = self
			arguments = [wrap_scope.get_name_type(arg, err=False) for arg in arguments]
			dummy_function = Function(self, arguments, wrap_scope.parse_type(returntype, err=False), codeblock, generic_types)
			scope = wrap_scope.new_scope(parent_function=dummy_function)
			for arg_pattern, arg_type in arguments:
				scope.assign_to_pattern(arg_pattern, arg_type, True)
			scope.type_check_command(codeblock)
			return dummy_function.type
		elif expr.data == "function_callback" or expr.data == "function_callback_pipe":
			if expr.data == "function_callback":
				function, *arguments = expr.children[0].children
			else:
				mainarg = expr.children[0]
				function, *arguments = expr.children[1].children
				arguments.append(mainarg)
			func_type = self.type_check_expr(function)
			if func_type is None:
				return None
			if not isinstance(func_type, tuple):
				self.errors.append(TypeCheckError(expr, "You tried to call a %s, which isn't a function." % display_type(func_type)))
				return None
			*arg_types, return_type = func_type
			generics = {}
			parameters_have_none = False
			for n, (argument, arg_type) in enumerate(zip(arguments, arg_types), start=1):
				check_type = self.type_check_expr(argument)
				if check_type is None:
					parameters_have_none = True
				resolved_arg_type = apply_generics(arg_type, check_type, generics)
				_, incompatible = resolve_equal_types(check_type, resolved_arg_type)
				if incompatible:
					if expr.data == "function_callback":
						self.errors.append(TypeCheckError(argument, "%s's argument #%d should be a %s, but you gave a %s." % (display_type(func_type), n, display_type(resolved_arg_type), display_type(check_type))))
					else:
						if n == len(arguments):
							self.errors.append(TypeCheckError(argument, "This left operand of |>, which I pass as the last argument to %s, should be a %s, but you gave a %s." % (display_type(func_type), display_type(resolved_arg_type), display_type(check_type))))
						else:
							self.errors.append(TypeCheckError(argument, "The argument #%d here should be a %s because the function is a %s, but you gave a %s." % (n, display_type(resolved_arg_type), display_type(func_type), display_type(check_type))))
			if len(arguments) > len(arg_types):
				self.errors.append(TypeCheckError(expr, "A %s has %d argument(s), but you gave %d." % (display_type(func_type), len(arg_types), len(arguments))))
				return None
			elif len(arguments) < len(arg_types):
				return tuple(apply_generics_to(arg_type, generics) for arg_type in func_type[len(arguments):])
			elif parameters_have_none and len(generics) > 0:
				# If one of the parameters is none, the generics likely did not
				# get assigned correctly, so the function's return type is
				# unknown.
				return None
			else:
				return apply_generics_to(return_type, generics)
		elif expr.data == "value":
			token_or_tree = expr.children[0]
			if type(token_or_tree) is lark.Tree:
				if token_or_tree.data != "char":
					return self.type_check_expr(token_or_tree)
				else:
					return self.get_value_type(token_or_tree)
			else:
				return self.get_value_type(token_or_tree)
		elif expr.data == "record_access":
			value, field = expr.children
			value_type = self.type_check_expr(value)
			if value_type is None:
				return None
			elif not isinstance(value_type, dict):
				self.errors.append(TypeCheckError(value, "You can only get fields from records, not %s." % display_type(value_type)))
				return None
			elif field.value not in value_type:
				self.errors.append(TypeCheckError(expr, "%s doesn't have a field `%s`." % (display_type(value_type), field.value)))
				return None
			else:
				return value_type[field.value]
		elif expr.data == "await_expression":
			value, _ = expr.children
			value_type = self.type_check_expr(value)
			contained_type = None
			if n_cmd_type.is_type(value_type):
				contained_type = value_type.typevars[0]
			elif value_type is not None:
				self.errors.append(TypeCheckError(expr, "You can only use the await operator on cmds, not %s." % display_type(value_type)))
			parent_function = self.get_parent_function()
			if parent_function is None:
				self.errors.append(TypeCheckError(expr, "You can't use the await operator outside a function."))
			elif parent_function.returntype is not None and not n_cmd_type.is_type(parent_function.returntype):
				self.errors.append(TypeCheckError(expr, "You can only use the await operator in a function that returns a cmd, but the surrounding function returns a %s." % display_type(parent_function.returntype)))
			return contained_type

		if len(expr.children) == 2 and type(expr.children[0]) is lark.Token:
			operation, value = expr.children
			operation_type = operation.type
			if operation_type == "NOT_KW":
				operation_type = "NOT"
			types = unary_operation_types.get(operation_type)
			if types:
				value_type = self.type_check_expr(value)
				if value_type is None:
					return None
				return_type = types.get(value_type)
				if return_type is None:
					self.errors.append(TypeCheckError(expr, "I don't know how to use %s on a %s." % (operation.type, display_type(value_type))))
					return None
				else:
					return return_type

		# For now, we assert that both operands are of the same time. In the
		# future, when we add traits for operations, this assumption may no
		# longer hold.
		if len(expr.children) == 3 and type(expr.children[1]) is lark.Token:
			left, operation, right = expr.children
			types = binary_operation_types.get(operation.type)
			if types:
				left_type = self.type_check_expr(left)
				right_type = self.type_check_expr(right)
				# When `type_check_expr` returns None, that means that there has
				# been an error and we don't know what type the user meant it to
				# return. That error should've been logged, so there's no need
				# to log more errors. Stop checking and pass down the None.
				if left_type is None or right_type is None:
					return None
				if isinstance(left_type, dict) or isinstance(right_type, dict):
					return_type = None
				else:
					return_type = types.get((left_type, right_type))
				if return_type is None:
					self.errors.append(TypeCheckError(expr, "I don't know how to use %s on a %s and %s." % (operation.type, display_type(left_type), display_type(right_type))))
					return None
				else:
					return return_type
			elif expr.data == "compare_expression":
				left, comparison, right = expr.children
				if left.data == "compare_expression":
					# We'll assume that any type errors will have been logged,
					# so this can only return 'bool' or None. We don't care
					# either way.
					self.type_check_expr(left)
					# We don't want to report errors twice, so we create a new
					# scope to store the errors, then discard the scope.
					scope = self.new_scope()
					scope.errors = []
					scope.warnings = []
					left_type = scope.type_check_expr(left.children[2])
				else:
					left_type = self.type_check_expr(left)
				right_type = self.type_check_expr(right)
				resolved_type, incompatible = resolve_equal_types(left_type, right_type)
				if incompatible:
					self.errors.append(TypeCheckError(comparison, "I can't compare %s and %s because they aren't the same type. You know they won't ever be equal." % (display_type(left_type), display_type(right_type))))
				if comparison.type != "EQUALS" and comparison.type != "NEQUALS" and comparison.type != "NEQUALS_QUIRKY":
					if resolved_type is not None and resolved_type not in comparable_types:
						self.errors.append(TypeCheckError(comparison, "I don't know how to compare %s." % display_type(resolved_type)))
				# We don't return None even if there are errors because we know
				# for sure that comparison operators return a boolean.
				return 'bool'

		elif expr.data == "tupleval":
			return [self.type_check_expr(e) for e in expr.children]
		elif expr.data == "listval":
			if (len(expr.children) == 0):
				return n_list_type

			first, *rest = [self.type_check_expr(e) for e in expr.children]
			contained_type = first

			for i, item_type in enumerate(rest):
				resolved_contained_type, incompatible = resolve_equal_types(contained_type, item_type)
				if incompatible:
					self.errors.append(TypeCheckError(expr.children[i+1], "The list item #%s's type is %s while the first item's type is %s" % (i + 2, item_type, first)))
				elif resolved_contained_type is not None:
					# To deal with cases like [[], [3]] as list[int]
					contained_type = resolved_contained_type

			return n_list_type.with_typevars([contained_type])
		elif expr.data == "impn":
			file_path = os.path.join(os.path.dirname(self.file_path), expr.children[0] + ".n")
			if os.path.isfile(file_path):
				impn, f = type_check_file(file_path, self.base_path)
				if len(impn.errors) != 0:
					self.errors.append(ImportedError(impn.errors[:], f))
				if len(impn.warnings) != 0:
					self.warnings.append(ImportedError(impn.warnings[:], f))
				holder = {}
				for key in impn.variables.keys():
					if impn.variables[key].public:
						holder[key] = impn.variables[key].type
				if holder == {}:
					self.warnings.append(TypeCheckError(expr.children[0], "There was nothing to import from %s" % expr.children[0]))
				return NModule(expr.children[0] + ".n", holder, types=impn.public_types)
			else:
				self.errors.append(TypeCheckError(expr.children[0], "The file %s does not exist" % (expr.children[0] + ".n")))
				return None
		elif expr.data == "recordval":
			record_type = dict(self.get_record_entry_type(entry) for entry in expr.children)
			if None in record_type.values():
				return None
			else:
				return record_type
		self.errors.append(TypeCheckError(expr, "Internal problem: I don't know the command/expression type %s." % expr.data))
		return None

	"""
	Type checks a command. Returns whether any code will run after the command
	to determine if any code is unreachable.
	"""
	def type_check_command(self, tree):
		if tree.data == "code_block":
			exit_point = None
			warned = False
			for instruction in tree.children:
			    exit = self.type_check_command(instruction)
			    if exit and exit_point is None:
			        exit_point = exit
			    elif exit_point and not warned:
			        warned = True
			        self.warnings.append(TypeCheckError(exit_point, "There are commands after this return statement, but I will never run them."))
			return exit_point
		elif tree.data != "instruction":
			self.errors.append(TypeCheckError(tree, "Internal problem: I only deal with instructions, not %s." % tree.data))
			return False

		command = tree.children[0]

		if command.data == "imp":
			import_name = command.children[0].value
			import_type = None
			if import_name in self.variables:
				self.errors.append(TypeCheckError(command.children[0], "You've already used the name `%s`." % import_name))
			try:
				imp = importlib.import_module("libraries." + command.children[0])
				types = {}
				try:
					types = imp._types()
				except AttributeError:
					pass
				import_type = NModule(import_name, imp._values(), types=types)
			except AttributeError:
				self.errors.append(TypeCheckError(command.children[0], "`%s` isn't a compatible native library." % command.children[0]))
			except ModuleNotFoundError:
				self.errors.append(TypeCheckError(command.children[0], "I can't find the native library `%s`." % command.children[0]))
			self.variables[import_name] = Variable(import_type, import_type)
		elif command.data == "for":
			var, iterable, code = command.children
			pattern, ty = self.get_name_type(var, err=False)
			iterable_type = self.type_check_expr(iterable)
			iterated_type = iterable_types.get(iterable_type)
			if iterable_type is not None:
				if iterated_type is None:
					self.errors.append(TypeCheckError(iterable, "I can't loop over a %s." % display_type(iterable_type)))
				elif ty == 'infer':
					ty = iterated_type
				elif ty != iterated_type:
					self.errors.append(TypeCheckError(ty, "Looping over a %s produces %s values, not %s." % (display_type(iterable_type), display_type(iterated_type), display_type(ty))))
			scope = self.new_scope()
			scope.assign_to_pattern(pattern, ty, True)
			return scope.type_check_command(code)
		elif command.data == "return":
			return_type = self.type_check_expr(command.children[0])
			parent_function = self.get_parent_function()
			if parent_function is None:
				self.errors.append(TypeCheckError(command, "You can't return outside a function."))
			else:
				# e.g. return []
				_, incompatible = resolve_equal_types(parent_function.returntype, return_type)
				if n_cmd_type.is_type(parent_function.returntype):
					if incompatible:
						_, incompatible = resolve_equal_types(parent_function.returntype.typevars[0], return_type)
					if incompatible:
						self.errors.append(TypeCheckError(command.children[0], "You returned a %s, but the function is supposed to return a %s or a %s." % (display_type(return_type), display_type(parent_function.returntype), display_type(parent_function.returntype.typevars[0]))))
				elif incompatible:
					self.errors.append(TypeCheckError(command.children[0], "You returned a %s, but the function is supposed to return a %s." % (display_type(return_type), display_type(parent_function.returntype))))
			return command
		elif command.data == "declare":
			modifiers, name_type, value = command.children
			pattern, ty = self.get_name_type(name_type, err=False)
			name = pattern_to_name(pattern)

			value_type = self.type_check_expr(value)
			resolved_value_type = apply_generics(value_type, ty)
			if ty == 'infer':
				ty = resolved_value_type
			else:
				_, incompatible = resolve_equal_types(ty, resolved_value_type)
				if incompatible:
					self.errors.append(TypeCheckError(value, "You set %s, which is defined to be a %s, to what evaluates to a %s." % (name, display_type(ty), display_type(value_type))))

			public = any(modifier.type == "PUBLIC" for modifier in modifiers.children)
			self.assign_to_pattern(pattern, ty, True, None, public)
		elif command.data == "vary":
			name, value = command.children
			variable = self.get_variable(name.value)
			if variable is None:
				self.errors.append(TypeCheckError(name, "The variable `%s` does not exist." % (name.value)))
			else:
				ty = variable.type
				value_type = self.type_check_expr(value)

				# Allow for cases like
				# let empty = [] // empty has type list[t]
				# NOTE: At this point, `empty` can be used, for example, as an
				# argument that expects list[int]. This might be a bug.
				# var empty = ["wow"] // empty now is known to have type list[str]
				resolved_type, incompatible = resolve_equal_types(ty, value_type)
				if incompatible:
					self.errors.append(TypeCheckError(value, "You set %s, which is defined to be a %s, to what evaluates to a %s." % (name, display_type(ty), display_type(value_type))))
				variable.type = resolved_type
		elif command.data == "if":
			condition, body = command.children
			scope = self.new_scope()
			if condition.data == "conditional_let":
				pattern, value = condition.children
				eval_type = self.type_check_expr(value)
				scope.assign_to_cond_pattern(get_conditional_destructure_pattern(pattern), eval_type, True)
			else:
				cond_type = self.type_check_expr(condition)
				if type(condition.children[0]) is lark.Token:
					if condition.children[0].value == "true":
						self.warnings.append(TypeCheckError(condition, "This will always run."))
					if condition.children[0].value == "false":
						self.warnings.append(TypeCheckError(condition, "This will never run."))
				if cond_type is not None and cond_type != "bool":
					self.errors.append(TypeCheckError(condition, "The condition here should be a boolean, not a %s." % display_type(cond_type)))
			scope.type_check_command(body)
		elif command.data == "ifelse":
			condition, if_true, if_false = command.children
			scope = self.new_scope()
			if condition.data == "conditional_let":
				pattern, value = condition.children
				eval_type = self.type_check_expr(value)
				scope.assign_to_cond_pattern(get_conditional_destructure_pattern(pattern), eval_type, True)
			else:
				cond_type = self.type_check_expr(condition)
				if type(condition.children[0]) is lark.Token:
					if condition.children[0].value == "true":
						self.warnings.append(TypeCheckError(condition, "The else statement of the expression will never run."))
					if condition.children[0].value == "false":
						self.warnings.append(TypeCheckError(condition, "The if statement of the expression will never run."))
				if cond_type is not None and cond_type != "bool":
					self.errors.append(TypeCheckError(condition, "The condition here should be a boolean, not a %s." % display_type(cond_type)))
			exit_if_true = scope.type_check_command(if_true)
			exit_if_false = scope.type_check_command(if_false)
			if exit_if_true and exit_if_false:
				return command
		elif command.data == "enum_definition":
			modifiers, type_def, constructors = command.children
			type_name, scope, typevars = self.get_name_typevars(type_def)
			variants = []
			enum_type = EnumType(type_name.value, variants, typevars)
			self.types[type_name] = enum_type
			if any(modifier.type == "PUBLIC" for modifier in modifiers.children):
				self.public_types[type_name] = self.types[type_name]
			for constructor in constructors.children:
				modifiers, constructor_name, *types = constructor.children
				public = any(modifier.type == "PUBLIC" for modifier in modifiers.children)
				types = [scope.parse_type(type_token, err=False) for type_token in types]
				variants.append((constructor_name.value, types))
				if constructor_name.value in self.variables:
					self.errors.append(TypeCheckError(constructor_name, "You've already defined `%s` in this scope." % constructor_name.value))
				if len(types) >= 1:
					self.variables[constructor_name.value] = NativeFunction(self, [("idk", arg_type) for arg_type in types], enum_type, id, public=public)
				else:
					self.variables[constructor_name.value] = Variable(enum_type, "I don't think this is used", public=public)
		elif command.data == "alias_definition":
			modifiers, alias_def, alias_type = command.children
			alias_name, scope, typevars = self.get_name_typevars(alias_def)
			alias_type = scope.parse_type(alias_type, err=False)
			if alias_type is None:
				self.types[alias_name] = "invalid"
			else:
				self.types[alias_name] = NAliasType(alias_name.value, alias_type, typevars)
			if any(modifier.type == "PUBLIC" for modifier in modifiers.children):
				self.public_types[alias_name] = self.types[alias_name]
		elif command.data == "class_definition":
			modifiers, name, class_args, class_body = command.children
			public = any(modifier.type == "PUBLIC" for modifier in modifiers.children)

			if len(class_args.children) > 0 and class_args.children[0].data == "generic_declaration":
				self.errors.append(TypeCheckError(class_args.children[0], "Classes do not support generic types."))
				return False
			arguments = [self.get_name_type(arg, err=False) for arg in class_args.children]
			scope = self.new_scope(parent_function=None)
			for arg_pattern, arg_type in arguments:
				scope.assign_to_pattern(arg_pattern, arg_type, True)
			scope.type_check_command(class_body)

			class_type = {}
			for prop_name, var in scope.variables.items():
				if var.public:
					if var.type is None:
						class_type = "invalid"
						break
					else:
						class_type[prop_name] = var.type
			constructor_type = tuple([*(arg_type for _, arg_type in arguments), class_type])

			if name.value in self.types:
				scope.errors.append(TypeCheckError(name, "You've already defined the `%s` type in this scope." % name.value))
			self.types[name.value] = class_type
			if public:
				self.public_types[name.value] = self.types[name.value]

			if name.value in self.variables:
				scope.errors.append(TypeCheckError(name, "You've already defined `%s` in this scope." % name.value))
			self.variables[name.value] = Variable(constructor_type, constructor_type, public)
		else:
			self.type_check_expr(command)

		# No return
		return False

	def add_native_function(self, name, argument_types, return_type, function):
		self.variables[name] = NativeFunction(self, argument_types, return_type, function)