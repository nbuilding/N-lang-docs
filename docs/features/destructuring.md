# Destructuring

Destructuring is the main way to get items out of tuples and can be used inside an `if` statment to check whether or not a destucurable type fits a certain pattern. There are two different types of detructuring:

```js
let a,
  b = (1, 2) // Sets a and b to 1 and 2 respectively
let { a, c: b } = { a: 1, c: 1 } // Sets a and c in the record to a and b respectively
```

This is a direct destructure, which can only be done with tuples and records, as they have defined fields or types.

```js
if let [a, b] = [1, 2] { // If it is able to destructure then it runs the code
	print(a)
	print(b)
} else {
	print("Destructure failed")
}

if let <yes a> = yes("test") { // Sets a to "test" as it managed to destructure correctly, so it is not a maybe
	print(a)
}
```

## Conditional patterns

The next type of destrucuting is the conditional `let`, as this is the only time list destructuring or enum destrucuring can be used. This is very useful for dealing with json types:

```js
import json
let jsonToStrMap = [val:json.value] -> maybe[map[str, str]] {
	if let <object valueMap> = val { // Checks if val is a json.object and stores it in valueMap if it is
		return entries(map) // For each of the entries in the map run the following code
			|> filterMap(([(key, value): (str, json.value)] -> maybe[(str, str)] {
				if let <string str> = value { // If the value in the map can be turned into a json.string then run the following code
					return yes((key, str))
				} else {
					return none // If it is not a json.string then remove it from the map
				}
			}))
			|> mapFrom()
			|> yes()
	} else {
		return none // If the value is not a json.object then return none
	}
}
```

## Notes

- All destructuring types can be used with a conditional let.
