# Tuples, Lists, and Records

Tuples, lists, and records are all types that store multiple values, each of them all have their own use. Let us start with tuples, tuples are values that can store a set amount of values of different types. The main way to recover the values are to destructure the tuple. Here is an example of a tuple value:
```js
// This will declare a simple tuple with a int and a char
let tuplevalue:(int, char) = (1, \{a})
```
This makes a simple tuple with an `int` and a `char`. Next let us take a look at records, records are used to store certain types and assign a name or key to each value, allowing for easier and more human understandable useage like so:
```js
// This will declare a record with a int called value and then get that from it
let recordvalue:{ value: int } = {
	value: 1 // There is either a newline or ; at the end
}
let value = recordvalue.value
```
Here this simply makes a record with one value, but a record can also be used as a simpler way or storing class-like data, without the useage of a class. Lastly is a list, which takes in a type and stores a list of values of that type, there is no limit to how many items a data can hold, here is and example of a list in action:
```js
// This will declare a list of strings
let listvalue:list[str] = ["a", "b", "c"]

var listvalue = append("d", listvalue) // Append is not a void function

let listindexvalue = itemAt(1, listvalue) // This returns a maybe which will need to be defaulted

print(listindexvalue)
```

## Notes:
- All of the above can be [destructured](./destructuring.md).
- Tuples can only be [destructured](./destructuring.md) to get the values from them.
- `append` returns a list.
- `itemAt` will return a `maybe` for null saftey, see how to deal with that [here](./enums.md).
- Most of the list functions are intended to be used with the [pipe operator](./currying.md).