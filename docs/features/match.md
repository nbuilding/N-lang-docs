# Match

Match statements are simple ways of shortening down if-else statements, they are also arguably faster to run than if-else statements. Here is an example of a match statement:

```js
print(match ("Hello!") {
	"Hello!" -> "hi"
	"How are you?" -> "I am good"
	_ -> "I do not understand"
})
```

This prints out `hi`. Match statements take in a value and it will take in a set of inputs and outputs, along with a default or `_` option, which it will fall back upon if it cannot find a matching input for the value given in. Here is an example:

```js
print(match ("e") {
	"Hello!" -> "hi"
	"How are you?" -> "I am good"
	_ -> "I do not understand"
})
```

This will print out `I do not understand`.

Match statements can also deconstruct enums, but a must also be supplied:

```js
print(match (maybeStrValue) {
	yes(v) => v
	none => "none" // Can be ommitted as _ will catch none if it is not there
	_ => "This should never occur"
})
```

This is the exact same as `maybeStrValue | "none"`

## Notes:

- You cannot have two default options
- You can have expressions as an input
- If you have two of the same input it will choose the one later
- All inputs must be of the same type
- All outputs must be of the same type
- Match is an expression and cannot be used as a statement
