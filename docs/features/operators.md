# Operators

Operators are very useful for manipulating values, this will go through all of the operators currently in N:

### `OR`
The OR operator (`||` or `|`) can be used on two booleans or two ints, it will either output a bool or an int depending on its inputs.

When the inputs are booleans it will return true if one of the values are `true`, the `||` variation is the standard for bools:
```js
let val = true || false // true

let val1 = false || false // false
```

When the inputs are ints it will return an int that has all of the bits combined, the `|` variation is the standard for ints:
```js
let val1 = 0b1100 // 12
let val2 = 0b0111 // 7

let val = val1 | val2 // 15 or:
/*
  1100
| 0111 =
  1111
*/
```

### `AND`
The AND operator (`&&` or `&`) can be used on two booleans or two ints, it will either output a bool or an int depending on its inputs.

When the inputs are booleans it will return true if both of the values are `true`, the `&&` variation is the standard for bools:
```js
let val = true || false // true

let val1 = false || false // false
```

When the inputs are ints it will return an int that has all of the bits combined, the `&` variation is the standard for ints:
```js
let val1 = 0b1100 // 12
let val2 = 0b0111 // 7

let val = val1 & val2 // 4 or:
/*
  1100
& 0111 =
  0100
*/
```

### `ADD`
The ADD operator (`+`) can be used on ints, floats, chars, and strings to combine or mathematically add them together.

When the inputs are ints it will return an int which is the mathematical addition of the two numbers:
```js
let val = 1 + 2 // 3
```

When the inputs are floats it will return a float which is the mathematical addition of the two numbers: 
```js
let val = 1.5 + 2.5 // 4.0
```

When the inputs are both strings it will return a string which is the concatenation of both of the strings:
```js
let val = "hel" + "llo" // "hello"
```

When one of the inputs are a string and another is a char it will take the string version of the char and concatenate them:
```js
let val = \{h} + "ello" // "hello"
```

### `SUBTRACT`
The SUBTRACT operator (`-`) can be used on ints and floats as a sign to signal a number as negative or as a mathematical expression

When the inputs are both ints it will return an int which is the mathematical subtraction of the two numbers:
```js
let val = 2 - 1 // 1

let val1 = -1 // -1
```

When the inputs are both floats it will return a float which is the mathematical subtraction of the two numbers:
```js
let val = 2.5 - 0.5 // 2.0

let val1 = -1.5 // -1.5
```

### `MULTIPLY`
The MULTIPLY operator (`*`) can be used on ints and floats as a mathematical expression

When the inputs are both ints it will return an int which is the mathematical multiplication of the two numbers:
```js
let val = 2 * 3 // 6
```

When the inputs are both floats it will return a float which is the mathematical multiplication of the two numbers:
```js
let val = 2.5 * 0.5 // 1.25
```

### `DIVIDE`
The DIVIDE operator (`/`) can be used on ints and floats as a mathematical expression

When the inputs are both ints it will return an int which is the mathematical division of the two numbers and it will truncate the number:
```js
let val = 7 / 4 // 3
```

When the inputs are both floats it will return a float which is the mathematical division of the two numbers:
```js
let val = 2.5 / 0.5 // 5.0
```

### `SHIFTL` and `SHIFTR`
The SHIFTL (`>>`) and SHIFTR (`<<`) operators take in two ints and will bit shift the int on the left the amount of times as the number on the right:
```js
let val = 1 << 3 // 0100 from 0001 or 4

let val1 = 8 >> 2 // 0010 from 1000 or 2
```

### `IN`
The IN operator (`in`) can be used on values in lists, chars, and strings to measure whether a value is in them.

When the values given are a list and a item whose type is type of the values in the list it will return `true` if the item is in the list:
```js
let val = 1 in [1, 2, 3, 4] // true
```

When the values given are a char and a string or a string and a string it will return true if the char or the string is inside the string:
```js
let val = \{e} in "hello" // true

let val1 = "hi" in "hello" // false
```

### `MODULO`
The MODULO operator (`%`) can be used to get the remainder of a division between ints or floats

When the values given are ints then it will return the remainder of a division between those two ints:
```js
let val = 12 % 5 // 2
```

When the values given are floats then it will return the reaminder of a division between those floats as a float:
```js
let val = 1.5 % 1.0 // 0.5
```

### `EXPONENT`
The EXPONENT operator (`^`) can be used to get the exponent of two ints or two floats

When the values given are ints it will return the exponent of both as a float to account for negative exponents:
```js
let val = 2^3 // 8.0
```

When the values given are floats it will return the exponent of both as a float:
```js
let val = 1.5 ^ 2.0 // 2.25
```

### `VALUEACCESS`
The VALUEACCESS operator (`[` x `]`) can be used to get items from lists, maps, and the `maybe` variations of each

When the values given are a list and and int it will return the item in the index of the list as a `maybe`, if it cannot get that item it will return a `none`:
```js
let val = [1, 2, 3, 4][0] // yes(1)

let val1 = [1, 2, 3, 4][10] // none
```

When the values given are a map and a value of its key type it will return the item associated with that key as a `maybe` if the key does not exist it will return `none`:
```js
let m = mapFrom([
	(1, "one"),
	(2, "two")
])

let val = m[1] // yes("one")

let val1 = m[10] // none
```

When the values given are a `maybe` it will run as normal if the value is not a `none` but if it is a `none` then it will return `none`:
```js
let m = mapFrom([
	(1, [1, 2, 3]),
	(2, [2, 3, 4])
])

let val = m[1][0] // yes(1)

let val = m[1][10] // none

let val1 = m[10][0] // none
```

### `NOT`
The NOT operator (`~` or `not`) takes in a bool invert the bool:
```js
let val = ~true // false
```
