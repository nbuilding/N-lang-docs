# Importing .n files

Imports are a great way of using other people's code and exploding files so they are less cumbersome. The `imp` keyword is used to import another file along with a path to the file:
```js
// the pub modifier allows variables to be public

let pub test = "Hello"
let test2 = "Goodbye" // Cannot be accessed when imported

print("test")
```

This will be `run.n`
```js
// imp takes in a string or a name (deprecated) and returns a record after running though the file

let importedThings = imp "./import.n" // This goes though the file so it will print out test
// let importedthings = imp import // deprecated, does the sames thing as the line before it

print(importedThings.test) // Prints out hello
//print(importedthigns.test2) will cause an error because it is not public
```
The `pub` modifier is used to export values to other files. This is why it can be applied to nearly every type or variable declaration, as by default, all values are private, to prevent malicious or accidental messing of code in other files.

Though it may be useful, circular imports are outlawed in the current system as there is no good way of making it work properly in the system we have defined.	

## Notes:
- `imp` returns a record-like object and so its type is as such, so it cannot be assigned to a record typed variable.
- `imp` runs though the imported file.
- `imp` can be called with a name not a string but that is deprecated.
