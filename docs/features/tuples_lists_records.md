# Tuples, Lists, and Records

Tuples, lists, and records are all types that store multiple values, each of them all have their own use. Let us start with tuples, tuples are values that can store a set amount of values of different types. The main way to recover the values is to destructure the tuple. Here is an example of a tuple value:

```js
// This will declare a simple tuple with a int and a char
let tuplevalue:(int, char) = (1, \{a})
```

You can use `..` on tuples to add them into functions:

```js
let subsectionTuple = (1, 4)

print(range(1, 10, 1).subsection(..subsectionTuple))
```

You can also do this with tuple literals too, though it may be inefficient.

This makes a simple tuple with an `int` and a `char`. Next, let us take a look at records, records are used to store certain types and assign a name or key to each value, allowing for easier and more human-understandable usage like so:

```js
// This will declare a record with an int called value and then get that from it
let recordvalue: { value: int } = {
  value: 1,
}
let value = recordvalue.value
```

Here this simply makes a record with one value, but a record can also be used as a simpler way of storing class-like data, without the usage of a class. Lastly is a list, which takes in a type and stores a list of values of that type, there is no limit to how many items a data can hold, here is an example of a list in action:

```js
// This will declare a list of strings
let mut listvalue: list[str] = ['a', 'b', 'c'],

listvalue = listvalue.append('d'), // Append is a void function

let listindexvalue = listvalue.itemAt(1), // This returns a maybe which will need to be defaulted

print(listindexvalue),
```



To edit a record or set an item in a list you are able to use the `..` operator, here is an example of its use:

```js
let listvalue:list[str] = ["a", "b", "c"]

print([..listvalue, "d"]) // prints out ["a", "b", "c", "d"]
```

The `..` operator works by inserting all of the items in the list that it is used on into the list literal, for example a `[..["a", "b"], "c", ..["d"]]` will evaluate to a `["a", "b", "c", "d"]`. For records it works a bit different, you are able to override fields in records by inserting them later as so:

```js
let recordvalue: { value1: int, value2: str } = {
	value1: 1,
	value2: "2",
}

print({
	..recordvalue,
	value1: 2,
}) // prints out { value1: 2, value2: "2" }
```

The `..` operator can even be used with two records to create a new one:

```js
let recordvalue: { value1: int, value2: str } = {
	value1: 1,
	value2: "2",
}

let recordvalue1: { value2: str, value3: bool } = {
	value2: "3",
	value3: false,
}

print({
	..recordvalue,
	..recordvalue1,
}) // prints out { value1: 1, value2: "3", value3: false }
```

## Notes:

- All of the above can be [destructured](./destructuring.md).
- Tuples can only be [destructured](./destructuring.md) to get the values from them.
- `append` returns a list.
- `itemAt` will return a `maybe` for null saftey, see how to deal with that [here](./enums.md).
- Most of the list functions are intended to be used with the [pipe operator](./currying.md).
- You are able to attempt to access a value on a `maybe` record type, this will return a `maybe` which is `none` if the record is `none` and a `yes` if the record is a `yes`
