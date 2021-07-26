# Procedures

In N, all functions aim to be pure and free of side effects. Given the same
input values, a function should always return the same output. This has several
benefits:

- Functions can be silently evaluated for debugging or eager evaluation (in a
  REPL, for example) without causing side effects and changing the behavior of
  the program. That is, the program won't notice whether its functions are being
  called more than once.

- Function return values can be cached (memoized) without changing how the
  program behaves (other than performance and memory use)

- Tests can run reliably and the same every time they're run.

- A compiler can optimise code by removing or caching unnecessary function
  calls.

Of course, pure functions can't do everything. For example, reading from a file
might give a different result each time. For these cases, N provides a special
built-in type `cmd` (short for "command"), which are used for any procedure that
has an unreliable return value or cannot be reliably optimised away if the
return value is unused.

Functions that return `cmd` values are known as "procedures." Procedures
themselves are still pure; given the same inputs, they will still return the
same `cmd` value. However, the `cmd` can be defined to return different values
depending on the resulting values from other `cmd`s.

**IMPORTANT**: These `cmd` values do not do anything on their own; simply
calling `FileIO.read` as a normal function will not do anything. Rather, the
main file being run will export the `cmd` value to the N using `let pub`. Then,
N will execute the commands encoded inside the `cmd` value.

For example, the following code reads a file named `hello.txt` using
`FileIO.read` from the built-in `FileIO` module. The contents of the file could
be anything—the file could also not exist! Thus, `FileIO.read` returns a `cmd`
value that has a result type of `maybe[str]`; this is represented in a function return type annotation as `cmd[maybe[str]]`.

```js
import FileIO

let printFile = [maybeFile: maybe[str]] -> cmd[()] {
	if let <yes contents> = maybeFile {
		print(contents)
	} else {
		print("hello.txt does not exist!")
	}
}

let pub mainCmd = FileIO.read("hello.txt")
	|> then(printFile)
```

Above, we use `FileIO.read("hello.txt")` to get a `cmd` value. This function
call alone does not read the file. Instead, we create a new `cmd` value using
the built-in `then` function that, when given the result from `FileIO.read`'s
`cmd` value, will give the resulting value to a procedure (in this case
`printFile`) to create a new `cmd` value to execute next.

Note that although `printFile` has a return type of `cmd[()]`, it has no
`return` statement. In N, functions with a return type of `cmd[()]` or `()` will
implicitly return the value of the correct type at the end of the function.

Finally, we set `mainCmd` to the resulting `cmd` value, and then export it with
`pub`, so N can access and execute the command.

The `then` function can be unwieldy to use, however. Fortunately, N provides
syntactic sugar for chaining `cmd` values one after another using the `!`
("bang") operator.

```js
import times
import FileIO

let main = [] -> cmd[()] {
	FileIO.write(
		"fruit.txt",
		"It has been "
			+ intInBase10(floor(times.getTime()!))
			+ "ms since the UNIX epoch.",
	)!
	for (fruit in ["apple", "orange", "banana"]) {
		times.sleep(1000)!
		FileIO.append("fruit.txt", fruit)!
	}
}

let pub mainCmd = main()
```

The `!` operator can only be used inside procedures—functions that return a
`cmd` value, and they can only be used on other `cmd` values. This is syntactic
sugar for pausing the function while the `cmd` is being executed, then
continuing the rest of the function with the resulting value. You can see how
the resulting value from the command returned by `times.getTime` is used to
write the number of milliseconds since the UNIX epoch to a file.

**IMPORTANT**: Do not forget to use `!` on `cmd` values to execute them inside
procedures. Omitting it will simply return the `cmd` value and discard it, like
the following:

```js
times.sleep(1000)
```

**NOTE**: The Python implementation does not support the use of `!` in
statements. In order to sleep for 1000 milliseconds, one must write the
following, discarding the `()` result from `times.sleep`'s command.

```js
let _ = times.sleep(1000)!
```

However, if possible, avoid writing code this way, as it is error-prone. The
type checker can help catch accidental omissions of the `!` operator, but `let _ =` implies that the omission is intentional.

Remember that because functions have to be pure, non-procedural functions cannot
call procedures. For this reason, you cannot use the `!` operator outside of
procedures; that is, the `!` operator can only be used inside functions that
return a `cmd` value.

## A note on `print`

`print` is quite an oddball function because it produces a side effect—it prints
text to standard output. Thus, whether or not `print` is called an extra time is
noticeable.

`print` is primarily used for debugging, to see if a value during runtime is
correct or if code in a procedure is reached properly. This way, `print` can be
used inside non-procedural functions without the use of the `!` operator.
However, in production, lone `print` statements may be optimised away because it
is seen as a pure function.

There is currently no reliable way to print text to stdout. In older versions of
N, one could use the `fek` module's `paer` procedure, but this has been removed
in later versions. Perhaps the built-in module `SystemIO` may one day have a
reliable `print` procedure that returns a `cmd` value to ensure it does not get
optimised away.
