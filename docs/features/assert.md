# Assert

assert is a powerful tool to help with unit tests in software, they are able to not only check the type of any value or variable, but they are also able to assert the value of it too. This is mostly useful in situations where you want to unit test N files. There are two versions, assert value and assert type, they work as so:
```js
assert type 1: int

assert value 1 + 1 = 2
```
During compile and execution the results of these tests are stored and can be accessed by any file that imports them as so:
```js
if let <yes mod> = intoModule(imp "./test.n") {
	print(getUnitTestResults(mod))
}
```
For more info on these functions please see the [native functions documentation](./native_functions.md). N uses assert internally for its type and value based checks. You are able to see them in the `tests/assertions` folder in the `N-lang` repo.


## Notes:
- assert value takes in a `bool`