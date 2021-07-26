# Literals

Literals are the raw values like `1` or `"a"` that are the main basis for values in N along with variables, this will go through all literals currently in N.

## Number Literals

### Decimal Literals
This is the plain and simple way of writing an int, it is a base ten number such as `10`:
```js
let val = 32

print(val) // prints out 32
```

### Float Literals
This is the same as the decimal literal, but it has a decimal point so it evals to a float:
```js
let val = 32.5

print(val) // prints out 32.5
```

### Hex Literals
This allows you to write in hex and is prefaced by a `0x`, this ends up evaluating to an int:
```js
let val = 0xff

print(val) // prints out 255
```

### Octal Literals
This allows you to write in octal and is prefaced by a `0o`, this ends up evaluating to an int:
```js
let val = 0o21

print(val) // prints out 17
```

### Binary Literals
This allows you to write in binary and is prefaced by a `0b`, this ends up evaluating to an int:
```js
let val = 0b1011

print(val) // prints out 11
```

## Boolean Literals
This allows you to write raw `true` or `false` values:
```js
let val = false

print(val) // prints out false
```

## List Literals
This is the main way to write out lists:
```js
let val = [1, 2, 3]

print(val) // prints out [1, 2, 3]
```
List literals can also use the `..` operator to combine lists into it:
```js
let val = [..[1, 2], 3]

print(val) // prints out [1, 2, 3]
```

## Tuple Literals
This is the main way to write out tuples:
```js
let val = (1, "2", false)

print(val) // prints out (1, "2", false)
```

## Record Literals
This is the main way to write out records:
```js
let val = {
	value1: 1
	value2: "2"
}

print(val) // prints out { value1: 1; value2: "2" }
```
Records literals can also used the `..` operator to combine or override fields:
```js
let val = {
	..{ value1: 1; value2: "2" }
	..{ value2: "3"; value3: false}
}

print(val) // prints out { value1: 1; value2: "3"; value3: false }
```

## Char Literals

### Raw Char Literals
This is the main way of turning a unicode character into a char:
```js
let val = \{a}

print(val) // prints out a
```

### Escape Code Literals
This is the main way of using special characters such as `\n`:
```js
let val = \n

print(val) // prints out a newline
```
The currently supported escape codes are `\n`, `\t`, `\r`, `\v`, `\0`, `\f`, and `\b`.

### Unicode Escape Code Literals
This is the main way of getting a unicode character from its hex index:
```js
let val = \u{ff}

print(val) // prints out ÿ
```

## String Literals
This is the main way to write out raw strings for use in a program:
```js
let val = "hello!"

print(val) // prints out hello!
```
String literals can also use escape codes such as the Escape Code Literals and the Unicode Escape Code Literals. In addition to those it can also use the `\"` escape code to allow for "s in the string:
```js
let val = "hello!\n (\"how are \u{ff}ou\")"

print(val) // prints out:
/*
hello!
 ("how are ÿou")
*/
```
