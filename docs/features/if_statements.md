# `if` statements and expressions

Like many programming languages, N has `if` and `if`/`else` statements and
expressions for control flow.

Its syntax is inspired by Rust, so no parentheses are required around the
condition. <!-- However, for aesthetic reasons, omitting parentheses is
discouraged and may be required in a future version of N. -->

## `if` and `if`/`else` statements

`if` statements can be used wherever other statements like the `let` statement
are allowed; the `else` branch is not required.

```js
if divisor == 0 {
	return err("Cannot divide by zero.")
}
```

The statements in the `if` and `else` branches must be enclosed by curly
brackets (`{` and `}`); they are not optional. Multiple statements can be used
inside the branches. You can also use `else if` without needing curly brackets
around the second `if` statement.

```js
type divisionError =
	| divisionByZero
	| dividendNotDivisible

let divideSafe = [dividend:int divisor:int] -> result[int, divisionError] {
	if divisor == 0 {
		return err(divisionByZero)
	} else if dividend % divisor /= 0 {
		return err(dividendNotDivisible)
	} else {
		let quotient = dividend / divisor
		return ok(quotient)
	}
}
```

## `if`/`else` expressions

N uses a similar syntax for `if`/`else` expressions for returning different
values based on the condition. This is equivalent to the ternary operator found
in a few programming languages such as C.

While the syntax is similar, the `else` branch is required for expressions, and
the curly brackets may only contain an expression. Statements cannot be used
within `if`/`else` expressions.

```js
print(
	"n is "
		+ if n % 2 == 0 {
			"even"
		} else {
			"odd"
		}
)
```

## `if let`

Instead of an expression, `if` statements and expressions also support `if let`.
`if let` is followed by a [conditional
pattern](./destructuring.md#conditional-patterns) then an expression; if the
resulting value matches the pattern, then the `if` branch is run with the
extracted values from the pattern. Otherwise, the `else` branch is run, if
present.

**NOTE**: `if let` is a special syntax, not an expression, so you cannot put
parentheses around `let ... = ...`.

`if let` is especially useful for extracting values contained in an enum value.
For example, the following example gets the first item from a list `names`, but
if the list is empty, then the `else` branch returns `Doe` as a default value.

```js
let first = if <yes name> = names[0] {
	name
} else {
	"Doe"
}
```
