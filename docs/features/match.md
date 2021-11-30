# Match

Match expressions are a faster and more effective way of checking values than reeditions of if-else statements, as instead of checking each one until the condition matches, it checks immediately using a dictionary internally. Here is an example of a match statement:

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

## Notes:

- You cannot have two default options
- You can have expressions as an input
- If you have two of the same input it will choose the one later
- All inputs must be of the same type
- All outputts must be of the same type
