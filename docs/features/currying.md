# Currying and the Pipe Operator

Currying is a useful way of pre-filling arguments in functions to stop the need of having to copy an argument serveral times. Currying occurs when a function is called with less arguments then it takes in, creating a new function that takes in the arguments that were not filled, and pre-filled values based on the arguments that were passed in. Here is an example of currying:
```js
let sum = [a:int b:int] -> int {
	return a + b
}

let addOne = sum(1) // Here it is called with one less argument than intended; this ends up returning a function that is an int -> int, which when called will add one to the number

print(addOne(2)) // Prints 3
```
The `|>` operator goes well with currying as it takes in a function on the right side and applies the arugment on the left to the function on the right, allowing for useages like this:
```js
2
 |> sum(1) // Same as sum(1, 2) or sum(1)(2)
 |> print // Note that the pipe operator can be stacked indefinitely. This still prints 3
```

## Notes
- You can call currying with no arguments on a function that takes in at least one argument.