# Type variables

In N code, you'll often encounter mysterious letters like `list[t]` in certain types. For example, the `print` function:

```ts
assert type print : [t] t -> t
```

That `[t]` in the function type annotation means that you can substitute `t` with any type. This allows `print` to be able to accept and return any type, not just strings:

```ts
assert type print("Hello!") : str
assert type print(3.14) : float
```

The same `t` is used in the function's argument and return type, which means that the return type must be the same as the argument type.

For a more sophisticated example, let us consider `map`, whose much more complicated type signature is shown below. However, when broken down, it is much simpler than it looks.

```ts
assert type map : [a, b] (list[a], (a -> b)) -> list[b]
```

`map` is a function that takes another function (the transformer) and a list, then returns a new list containing items of a different type, each transformed by the magic transformer function.

Here, `[a, b]` declares two type variables. This means that the argument of the transformer function `a -> b` and the items of the list `list[a]` must be the same type, but the items of the list `list[a]` do not have to be the same type as the _return_ type (`b`) of the transformer function because `a` and `b` can stand for different types.

For example, `intInBase10` converts ints to strs (`int -> str`), so we know that `a` must stand for an `int`, and `b` must stand for a `str`. Since `a` must stand for the same type throughout the function, and likewise for `b`, we can determine the type of `map(intInBase10)`.

```ts
assert type map(intInBase10) : list[int] -> list[str]
```

At the time of writing this, `map` is not a built-in function provided by N. And the `intInBase10` function has been moved to the trait of `int`, `toString`

Type variables can also be used in enum and alias declarations. For example, you could make an alias for a tuple of three of the same type:

```ts
alias triplet[t] = (t, t, t)
```

N's `result` type can be defined in N using type variables as well:

```ts
type result[o, e]
	| ok(o)
	| err(e)
```

In the above two examples, the `[t]` is needed to declare the type variable `t`. Otherwise, as warned above, N will give an error about how type `t` is undefined.

Since the types take type variables, you need to specify them explicitly, in the same order as they are defined, to substitute the type variables in their type definitions. For example,

```ts
let vector3: triplet[float] = (0.5, -0.5, 3.14)

let myResult: result[int, str] = err("Failure!")
```
