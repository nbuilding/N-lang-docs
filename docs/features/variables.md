# Variables

Like in mathematics and many programming languages, N has variables that allow
you to store values of any type under a variable name.

In N, all variables are constants. This means that their value, once set, will
never change. This makes N programs reliable because you can trust that a
function can be run multiple times without behaving differently, and this allows
N programs to be multi-threaded without running into issues with race
conditions. <!-- This might seem odd, especially for users coming from some
programming languages, because "variable" implies that the variable should be
variable, or changeable. However, like in math, "variable" in this sense implies
that the value itself at runtime is variable. -->

## `let` statements

To create a variable, you can use the `let` statement. The keyword `let` is
followed by the variable name, a colon (`:`), the type of the variable (called
the type annotation), an equals sign (`=`), and the expression whose evaluated
result should be stored in the variable. In the following example, we set a
variable named `name` to the string `"Billy"`, and we indicate that `name` is of
the `str` type.

```js
let name: str = 'Billy'
```

In many cases, however, the type can be inferred, so the type annotation can be
omitted. The above code can be simplified to the following:

```js
let name = 'Billy'
```

You can use a [definite pattern](./destructuring.md) in a `let` statement to
extract values from various types of values, such as records and tuples.

```js
let { name, age: yearsSinceBirth } = {
  name: "Billy",
  age: 36,
}

assert value (name, yearsSinceBirth) == ("Billy", 36)
```

Learn more about definite patterns at [Patterns](./destructuring.md).

### Exporting variables

In a module, you can export a variable by adding the `pub` keyword after `let`. For example, the following exports a variable named `wow` from the module,
making it accessible by other modules.

```js
// a.n

let pub a = "aaaaaa"
```

```js
// b.n

let aModule = imp "./a.n"

assert value aModule.a == "aaaaaa"
```

Learn more about exporting values at [Importing .n
files](./importing_n_files.md).

## Other ways of creating variables

`let` statements aren't the only way variables can be defined.

Function arguments can also store the argument values given to the function by a
function call. [Definite patterns](./destructuring.md) can also be used in
function arguments. Notably, however, type annotations are required for function
arguments.

For example, in the following example, `name` and `age` are usable like
variables inside the `displayPerson` function.

```js
let displayPerson = [(name, age): (str, int)] -> str {
  return name + ", a " + intInBase10(age) + "-year-old neckbeard"
}

assert value displayPerson(("Billy", 36)) == "Billy, a 36-year-old neckbeard"
```

Variables are also created by conditional patterns in [`if let`](./if_statements.md#if-let) statements and expressions. In the following
example, `text` is usable like a variable containing a string.

```js
if let yes(text) = yes("hello") {
  assert value text == "hello"
}
```