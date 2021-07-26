# Type Aliases

Type aliases are great ways of compressing types into a more friendly form for usage in functions and other type declarations. It can be used as so:
```js
// This will create a simple alias for a record type
alias test = {
	a:int,
	b:int,
	c:str,
}

let test2 = [val:test] -> () {
	print(val.b)
}
```
Here it may not seem that useful but when dealing with many different complex records and functions it is very useful to help figure out the types for everything. The `websocket` library uses this to help it make itself a bit more consise
```js
import websocket // Used for connecting to WebSockets
let websocketTest = websocket.connect({
  onOpen: [send: websocket.send] -> cmd[bool] {
    print("Open!")
    let _ = send("hi")!
    return false
  },
  onMessage: [send: websocket.send message: str] -> cmd[bool] {
    print(message)
    let _ = send("hello")!
    return message == "hello"
  }
}, "wss://echo.websocket.org")!
```
In this example `websocket.send` is acutally a type alias for `str -> cmd[()]`. Here is is small but it is also useful to changing the type of many different, similar records if changes are needed, such as a `user` record to add another field, as it would be impractical and problematic to do it by hand.

## Notes:
- When printing out the type of a value that uses an alias as its type, it will not print out the alias' name.
