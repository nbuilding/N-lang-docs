# For Loops

For loops are a great way to run code a certain or changing amount of ways in a concise manner. For example, here is a for loop that `print`s all of the numbers 0-9
```js
for (i in range(0, 10, 1)) { // range takes in a lower bound (inclusive), and upper bound (exclusive), and a step size are returns an int array
	print(i)
} // This will print 0 - 9
```
This is not all that the `for` loop can do. As you saw, the for loop above used the `range` function, which is an internal function that takes in a lower bound, upper bound, and a step parameter and it will return a `list` with numbers from the lower bound (inclusive) and the upper bound (exclusive) with differences of the step variable like so:
```js
range(0, 10, 1) // [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
range(0, 10, 2) // [0, 2, 4, 6, 8]
```
This is used in the `for` loop example as the `for` loop iterates through each item in the `list`, setting `i` to the next item in the list before each cycle, allowing for useage of the `for` loop like so:
```js
for (i in ["this", "is", "a", "test"]) {
	print(i)
}
```
This ends up outputting
```
this
is
a
test
```
This is not only limited to list literals as we have seen, making it a useful feature to read evey item in a list.

## Notes:
- Currently the only iterables that are registered are `list` values
- The old syntax will still run, but will give a deprecation warning
