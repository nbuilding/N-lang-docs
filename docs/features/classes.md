# Classes

Like a few programming languages, N has classes.

```js
/// A sheep.
class pub Sheep [colour:str age:float name:str] {
	/// The display name for the type of sheep based on its wool colour.
	let typeName = colour + " sheep"

	/// Create a new Sheep with the given name
	let pub rename = [newName:str] -> Sheep {
		return Sheep(colour, age, newName)
	}

	let pub introduction = "Hi, I'm " + name + ", and I am a " + typeName + "."
}
```

To create a class, start with the `class` keyword. You can make the class public
by adding the `pub` keyword like you would for variables and types. Making the
class public will export both the type and constructor.

After the keywords, specify the class name (in the above example, `Sheep`) and
the arguments for the constructor, which have the same syntax as a function
expression. By convention, class names are capitalized.

Then, enclosed in curly brackets (`{` and `}`) is the class body. The same
statements that you can find in a normal N file can be placed inside a class
body, so you can call `print` or define variables.

You can define public properties and methods—accessible outside the class
body—using the `pub` keyword.

```js
let billy = Sheep("white", 5, "Billy")

assert value billy.rename("Bob").introduction
	== "Hi, I'm Bob, and I am a white sheep."
```

To create an instance of a class, you can call the class name like a function,
specifying the constructor's arguments. The class constructor is a normal
function, so you can curry it.

Class instances are records, so you can access public properties and methods
using dot (`.`) notation. `billy.typeName` would be a type error in the above
example because `typeName` is not a public property (it is private).

## Representation of classes in N

In reality, N classes are syntactic sugar for functions that return a record.
For example, the above example is equivalent to the following:

```js
alias pub Sheep = {
	rename: str -> Sheep
	introduction: str
}

let pub Sheep = [colour:str age:float name:str] -> Sheep {
	let typeName = colour + " sheep"

	let pub rename = [newName:str] -> Sheep {
		return Sheep(colour, age, newName)
	}

	let pub introduction = "Hi, I'm " + name + ", and I am a " + typeName + "."

	return {
		rename
		introduction
	}
}
```

A few keen readers among you may note that this means that class types are
merely aliases of record types. This means that classes are structurally typed,
not nominally typed, like TypeScript. This allows for duck-typing: if the class instance walks like a duck and quacks like a duck, then it must be a duck.

Thus, the following code is valid and free of type errors.

```js
class Duck [] {
	let pub walk = "Waddle waddle."

	let pub quack = "Quack. Got any grapes?"
}

class Human [] {
	let pub walk = "I am walking."

	let pub quack = "\"Quack.\""
}

// This is valid.
let definitelyADuck: Duck = Human()
```

## Recommended idiomatic patterns

When working with classes in N, here are some suggested coding patterns to meet
various needs.

### Private constructors

To make only the class constructor private while exporting the class type, you
will have to give the class a different name, then export a type alias for the
unexported class name.

```js
class Sheep_ [...] { ... }

alias pub Sheep = Sheep_
```

### Multiple constructors

To support multiple constructors, you can instead make helper functions as
static methods separate from the class that construct the class. Optionally, you
can make the main class constructor private and only export the helper
functions.

In the `Sheep` example, we can export a function `makeBlackSheep`, taking
advantage of currying, which constructs a black sheep.

```js
let pub makeBlackSheep = Sheep("black")
```

## Limitations

Unlike other object-oriented languages, N does not support class inheritance
yet.
