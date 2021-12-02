# Functions

In N, functions are a type of value, like strings or lists. This means they
can be stored in variables or passed around as arguments for or return values
from another function.

As a preview for what this article entails, the following code defines a
function named `getPi` that takes a `()` (the unit type) and returns a float.
Then, `getPi` is called and printed.

```js
let getPi = () -> float {
	return 3.141592653589793
}

print(getPi())
```

The above definition benefits from type inference and syntactic sugar. The
following code is a more verbose equivalent of the above example.

```js
let getPi: () -> float = (_: ()])-> float {
	return 3.141592653589793
}

print(getPi(()))
```

## Function expressions

The following is an example of a function expression. This alone does not make
the function expression usable; it needs to be stored somewhere before it can be
called.

```js
(a:float, b:float) -> float {
	return (a^2 + b^2)^0.5
}
```

Function expressions start with a list of arguments, separated by spaces and
enclosed by parenthesis. Each argument consists of a [definite
pattern](./destructuring.md), which can just be the argument name, followed by a
colon (`:`) then the type annotation of the argument. Note that, unlike `let`
statements, argument type annotations cannot be inferred and thus are required.
In the example above, the function expression has two arguments: `a` and `b`,
both floats.

After the arguments, there is an arrow (`->`) and then the return type
annotation. Like the function arguments, the return type annotation cannot be
inferred and is thus also required. In the above example, the function returns a
float. If this arrow is ommited then N is forced to assume that the function returns
a `()`

Then, after the return type is the body of the function: statements enclosed by
curly brackets (`{` and `}`).

Functions are required to `return` a value with the proper type by the end of
the function.

### Syntactic sugar for `()`

If the function expression has no arguments, the function is assumed to take a
`()`, a unit value. And if it does not include an `-> returntype` then the return
type is assumed to be a `()`.

```ts
assert type () -> int {
	return 3
} : () -> int
```

A function with a return type of `()` or `cmd[()]` does not need a `return`
statement. There is an implicit `return ()` at the end of the function for
convenience. The following example is valid, despite the function expression
lacking an explicit `return` statement.

```js
() {
	print("Hello")
}
```

**NOTE**: The above function may be optimized and never called during runtime
because its return value is known at compile time (unit types only have one
possible value during runtime).

### Declaring functions

Unlike many programming languages, N does not have a special syntax for
declaring functions. Instead, you can store the function in a variable like with
any other value using a `let` statement. You can take advantage of type inference to avoid redundantly listing types.

The following code declares a function `add` that takes two integers and returns
an integer.

```ts
let add = (a:int, b:int) -> int {
	return a + b
}
```

## Calling functions

In the `add` example above, `add` in reality is a function that takes an
integer, then returns another function that takes another integer before
returning an integer. This is called **currying**; in N, all functions are
curried, so functions will take one argument at a time.

Thus, it is perfectly valid to only give one argument to `add` for **partial
application**.

```ts
let addOne = add(1)
```

`addOne` is a function that takes a single integer and returns the integer
incremented by one.

```js
assert value addOne(3) == 4
assert value addOne(-2) == -1
```

Currying and partial application are useful for creating more specific functions
that can operate on values with certain options preset. For this reason, it is
good practice in N to have any options arguments as the first arguments for a
function, then the value to transform as the last argument.

### Type annotations

To demonstrate that functions with multiple arguments actually take one argument
at a time and then return another function, before we had it so that the type
annotation of the `add` function from above is `int -> (int -> int)`.

```ts
assert type add : int -> int -> int
```

But now, to avoid confusion, we have the arguments in a tuple and the return
type ouside as so

```ts
assert type add : (int, int) -> int
```

#### More syntactic sugar with `()`

If a function takes a `()`, you can call a function passing in the `()` by
simply doing `functionName()` instead of `functionName(())`.

### Immediately invoked function expressions

In some cases, you may want to declare a temporary variable in an expression
context. Immmediately invoked function expressions (IIFEs) can be used to
include multiple statements and return a value.

```js
let deltaXSquared = () -> float {
	let deltaX = x1 - x2
	return deltaX * deltaX
}()

// Alternative

let deltaXSquared = () |> () -> float {
	let deltaX = x1 - x2
	return deltaX * deltaX
}
```

**NOTE**: Some implementations require parentheses around function expressions
when used like this.

This pattern is especially useful for creating a `cmd[()]` to export as the main
command for an N program.

```js
import times

let pub main = () -> cmd[()] {
	print("Wait a second...")
	times.sleep(1000)!
	print("Thanks.")
}()
```

See [Procedures](./async.md) for more information on commands.
