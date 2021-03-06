# Built-in functions

N provides many built-in functions that are available to use globally without
needing to import anything.

**Contents**

- [Basics](#basics)
- [Lists](#lists)
- [Maps](#maps)
- [`maybe` values](#maybe-values)
- [Commands](#commands)
- [Printing for debugging](#printing-for-debugging)
- [Runtime unit tests](#runtime-unit-tests)

## Basics

### `int.toString` : `() -> str`

Converts an integer to a string.

```ts
assert value (10).toString() = "10"
```

**NOTE**: To convert a float to a string, use the `stringify` function from the
`json` built-in module.

**NOTE**: To parse a string as an integer or float, use the `parse` or
`parseSafe` function from the `json` module.

### `int.toFloat` : `() -> float`

Converts an integer to a float. Inverse of `round`, `floor`, and `ceil`.

```ts
assert value (3).toFloat() == 3.0
```

### `float.round` : `() -> int`

Converts a float to an integer. Non-integers are rounded to the nearest integer;
if the fractional part is 0.5, then it is rounded up. Inverse of `toFloat`.

```ts
assert value (10.5).round() == 11
assert value (-10.5).round() == -10
```

**NOTE**: The behavior for `round`, `floor`, and `ceil` when given an infinity
or NaN is undefined. See nbuilding/N-lang#243.

### `float.floor` : `() -> int`

Converts a float to an integer, rounding down. Inverse of `toFloat`.

```ts
assert value (10.5).floor() == 10
assert value (-10.5).floor() == -11
```

### `float.ceil` : `() -> int`

Converts a float to an integer, rounding up. Inverse of `toFloat`.

```ts
assert value (10.5).ceil() == 11
assert value (10.4).ceil() == 11
assert value (-10.5).ceil() == -10
```

### `char.charCode` : `() -> int`

Gets the Unicode code point value for the given character. Inverse of `intCode`.

```ts
assert value \{a}.charCode() == 97
assert value \{🕴}.charCode() == 0x1f574
```

### `int.intCode` : `() -> char`

Converts the given Unicode code point to the corresponding character. Invalid
code points are converted to � (U+FFFD, REPLACEMENT CHARACTER). Inverse of
`charCode`.

```ts
assert value (32).intCode() == \{ }
assert value (-1).intCode() == \u{FFFD}
```

### `str.charAt` : `(int) -> maybe[char]`

Gets the character (not grapheme or code point) at the given index. Since
strings are probably not stored in UTF-32, this is probably O(n), but this is
implementation-defined. Negative indices aren't supported.

```ts
assert value "abc".charAt(1) == yes(\{b})
assert value "abc".charAt(-1) == none
```

**NOTE**: N now has a special character access syntax that should be used
instead: `string[index]`.

### `str.substring` : `(int, int) -> str`

Gets a portion of a string given a start index (inclusive) then the end index
(exclusive). The indices work as they do in Python, so they support negative
indices; however, if the start index is after the end index, then `substring`
returns an empty string.

```ts
assert value "abc".substring(0, 2) == "ab"
assert value "apple sauce".substring(-3, -1) == "uc"
assert value "banana jam".substring(0, -1) == "banana ja"
assert value "hi".substring(0, 100) == "hi"
assert value "hi".substring(2, 100) == ""
assert value "hello world".substring(5, 3) == ""
```

### `str.split` : `(char) -> list[str]`

Splits the given string by a character. Returns an empty array for an empty
string.

```ts
assert value split(\{b}, "abc") == ["a", "c"]
assert value split(\{b}, "") == []
assert value split(\{b}, "apple") == ["apple"]
```

### `str.strip` : `() -> str`

Removes whitespace characters.

```ts
assert value " abc ".strip() == "abc"
```

**NOTE**: The characters removed by `strip` are implementation-defined. See
nbuilding/N-lang#245.

## Lists

### `list[t].len` : `() -> int`

Gets the length of the given value. The behavior of `len` depends on the type
of value given; if the argument is a string or list, then it'll return its
length (for strings, this is in Unicode characters, not code points or
graphemes). Otherwise, it'll return zero.

```ts
assert value "abc".len() == 3
assert value (100).len() == 0
```

### `list[t].itemAt` : `[t] (int) -> maybe[t]`

Gets the item of a list by index. Does not support negative indices.

```ts
assert value [1, 2, 3]itemAt(1) == yes(2)
assert value [1, 2, 3].itemAt(-1) == none
```

**NOTE**: N now has a special list item access syntax that should be used
instead: `list[index]`.

**NOTE**: The representation of lists in memory is implementation-defined, so
item access may be O(n) in the worst case.

### `list[t].append` : `[t] (t) -> list[t]`

Returns a new list with the given item added to the end of the given list.

```ts
let list == [1, 2, 3]
assert value append(4, list) == [1, 2, 3, 4]
assert value list == [1, 2, 3]
```

**NOTE**: `append` does not mutate the list.

### `list[t].subsection` : `[t] (int, int) -> list[t]`

Returns a list containing a portion of the items in the given list; analogous to
`substring` but for lists.

```ts
assert value [0, 1, 2, 3, 4, 5].subsection(2, 4) == [2, 3]
assert value [0, 1, 2, 3, 4, 5].subsection(4, 1000) == [4, 5]
assert value [1, 2, 3].subsection(-3, -5) == []
assert value [1, 2, 3].subsection(-3, 1) == [1]
assert value [1, 2, 3].subsection(3, 2) == []
```

### `list[a].filterMap` : `[a, b] ((a) -> maybe[b]) -> list[b]`

Applies the given function to each item in the given list. If the function
returns `none`, the item will not be included in the list; otherwise, the
contained value in the `maybe` value will be included in the new list. Returns a
new list containing the resulting `yes`-contained values given by the function.

`filterMap` is intentionally generalized because `filter` and `map` can be
easily defined in terms of `filterMap`.

```ts
assert value [0, 1, 2, 3, 4].filterMap([value:int] -> maybe[int] {
	return yes(value * value + 1)
}) == [1, 2, 5, 10, 17]
```

### `range` : `(int, int, int) -> list[int]`

Returns a list of integers within the specified range. This takes a starting
value (inclusive), an end value (exclusive), and a step value. This is based on
[Python's `range`
constructor](https://docs.python.org/3/library/stdtypes.html#typesseq-range), so
it supports negative step values.

`range` is intended to be used with `for` loops to loop over a range of
integers.

```ts
assert value range(0, 3, 1) == [0, 1, 2]
assert value range(0, 10, 1) == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
assert value range(1, 11, 1) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
assert value range(0, 30, 5) == [0, 5, 10, 15, 20, 25]
assert value range(0, 10, 3) == [0, 3, 6, 9]
assert value range(0, -10, -1) == [0, -1, -2, -3, -4, -5, -6, -7, -8, -9]
assert value range(0, 0, 1) == []
assert value range(1, 0, 1) == []
```

**NOTE**: The representation of lists in memory is implementation-defined, so an
implementation may attempt to store the entire list in memory. This may be
costly for performance when iterating over a large range.

### `str.parseInt` : `() -> maybe[int]`

Returns an int if it able to parse the string into a base 10 integer, will return none if it fails

```js
assert value "asdf".parseInt() == none
assert value "10".parseInt() == 10
```

### `str.parseFloat` : `() -> maybe[float]`

Returns a int if it able to parse the string into a base 10 float, will return none if it fails or if the value is not finite

```js
assert value "asdf".parseInt() == none
assert value "nan".parseInt() == none
assert value "inf".parseInt() == none
assert value "-inf".parseInt() == none
assert value "10.34".parseInt() == 10
```

### `exit` : `(int) -> ()`

Exits the program with the given exit code

```js
print("test")

exit(0)

print("this will never run")
```

## Maps

### `mapFrom` : `[k, v] (list[(k, v)]) -> map[k, v]`

Creates a map from the given list of key-value pairs. Inverse of `entries`.

```ts
let map == mapFrom([("a", 1), ("b", 2)])
assert type map : map[str, int]
```

**NOTE**: Maps allow functions and commands as keys, but the behavior of these
maps is undefined.

### `entries` : `[k, v] (map[k, v]) -> list[(k, v)]`

Returns a list of key-value pairs from the map. Inverse of `mapFrom`.

```ts
assert value entries(map) == [("a", 1), ("b", 2)]
```

**NOTE**: The order of the key-value pairs should be preserved.

### `getValue` : `[k, v] (k, map[k, v]) -> maybe[v]`

Gets a value from the given map by the given key.

```ts
assert value getValue("b", map) == yes(2)
assert value getValue("c", map) == none
```

**NOTE**: N now has a special map value access syntax that should be used
instead: `map[key]`.

**NOTE**: The value access algorithm is implementation-defined and may be O(n)
in the worst case.

## `maybe` values

### `maybe[t].default` : `[t] (t) -> t`

Given a default value and a `maybe` value, returns the default value if the
`maybe` value is `none`; otherwise, it returns the value contained in the
`maybe` value.

```ts
assert value yes("test").default("test1") == "test"
assert value none.default("test1") == "test1"
```

This is equivalent to:

```ts
let default = [t] (defaultValue:t, maybe:maybe[t]) -> t {
	if let yes(value) = maybe {
		return value
	} else {
		return defaultValue
	}
}
```

## Commands

### `then` : `[a, b] ((a) -> cmd[b], cmd[a]) -> cmd[b]`

Returns a new command that first executes the given command, then runs the given
function given the result from the given command, then executes the resulting
command from that function.

```ts
import FileIO
assert type then([text: maybe[str]] -> cmd[()] {
	assert value len(text |> default("")) > 0
}, FileIO.read("./README.md")) : cmd[()]
```

This is equivalent to:

```ts
let then = [[a, b] function:(a -> cmd[b]) command:cmd[a]] -> cmd[b] {
	return function(command!)
}
```

### `parallel` : `[t] (cmd[t]) -> cmd[cmd[t]]`

Returns a new command that executes the given command in parallel. The result of
this new command is another command that resolves when the given command
finishes executing.

You can use the resulting command of the command returned by `parallel` to wait
for the command running in parallel to finish.

```ts
let parallelCmd = () |> ([] -> cmd[()] {
	let _ = parallel(() |> ([] -> cmd[()] {
		assert value true
	}))!
})
```

**NOTE**: The program exits when the main command finishes, so commands running
in parallel will be stopped.

## Printing for debugging

### `printWithEnd` : `[t] (str, t) -> t`

Prints the given value to stdout followed by the specified string and flushes,
then returns the value. Non-string values are pretty-printed in an
implementation-defined manner.

```ts
let printed = 3.14
	|> printWithEnd(" ")
assert value printed == 3.14
```

**NOTE**: This function is impure, but it is not a procedure for convenience.
Thus, this should only be used for development and debugging purposes, not for
actual output to stdout.

### `print` : `[t] (t) -> t`

Equivalent to `printWithEnd("\n")` and thus shares its caveats.

```ts
assert value print("test") = "test"
```

## Runtime unit tests

### `intoModule` : `[m] (m) -> maybe[module]`

Attempts to convert the given type to a `module` value. Imports from `imp` will
be successfully converted to a `module`; `intoModule` will return `none` for all
other values.

See `getUnitTestResults` below for an example.

### `module.getUnitTestResults` : `() -> list[{ hasPassed: bool, fileLine: int, unitTestType: str, possibleTypes: maybe[(str, str)] }]`

Gets a list of assertion results from the given `module` value. Assertion
results are a record with fields that depend on the type of assertion used in
the module.

Results from both `assert type` and `assert value` will include a `hasPassed`
field, a boolean that represents whether the assertion passed.

`assert type` results also have the following fields:

- `fileLine`, which is always `0`
- `unitTestType`, which is always the string `"type"`
- `possibleTypes`, which is a tuple containing implementation-defined strings
  (meant to be displayed to the user) wrapped in `yes`.

`assert value` results have the following fields:

- `fileLine`, an integer representing the line the assertion was on
- `unitTestType`, which is always the string `"value"`
- `possibleTypes`, which is always `none`

```ts
if let yes(module) = intoModule(imp "./imports/unit-test.n") {
	let results = module.getUnitTestResults()

	assert value len(results) == 4

	assert value (results |> itemAt(0)) == yes({
		hasPassed: true
		fileLine: 3
		unitTestType: "value"
		possibleTypes: none
	})

	assert value (results |> itemAt(1)) == yes({
		hasPassed: false
		fileLine: 5
		unitTestType: "value"
		possibleTypes: none
	})

	for (result in (results |> subsection(2, 4))) {
		assert value result.hasPassed
		assert value result.unitTestType == "type"
		assert value if let yes(_) == result.possibleTypes { true } else { false }
	}

	assert value (results |> itemAt(2) |> default({
		hasPassed: true
		fileLine: 0
		unitTestType: "value"
		possibleTypes: none
	})).fileLine == 7

	assert value (results |> itemAt(3) |> default({
		hasPassed: true
		fileLine: 0
		unitTestType: "value"
		possibleTypes: none
	})).fileLine == 9
}
```
