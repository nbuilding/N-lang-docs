# While, break, and continue

While loops are great for running a piece of code over and over again until a condition is met, here is one that waits for the user to type hello:
```js
while ( SystemIO.inp("Please type `hello`: ")! /= "hello" ) {}
```

The other main situations while loops find themselves in are times when a user wants to run a set of code indefinitely:
```js
while (true) {
	print("hi")
}
```
This ends up filling the screen with `hi`, but it can be used for more productive measures as well.

Break is used in while loops, for loops, and if statements to break out of them whenever it is needed, here is an example:
```js
while (true) {
	if (SystemIO.inp("Please type `hello`: ")! == "hello") {
		break
	}
}
```
Here it is the exact same effect as the first example but it is a lot more readable, break can also be used to cut off for loops
```js
for (i in range(0, 10, 1)) {
	if (i == 5) {
		break
	}
	print(i)
}
```
This will now only count until 4, as it breaks when it gets to 5.

Continue is used to skip over the rest of a loop when called, it can be used in for loops to skip certain items:
```js
for (i in range(0, 10, 1)) {
	if (i == 5) {
		continue
	}
	print(i)
}
```
Now, instead of stopping once it reaches 5, it just skips printing out the number 5, but continues to 6, 7, 8, and 9. This can also be done with while loops as well.
