# Internal Libraries

Internal Libraries are used to add complicated features from Python and JavaScript for users to use in N, you can import these using the `import` keyword. Here are the libraries you can import.

**Table of contents**

1. [`FileIO`](#FileIO)
2. [`json`](#json)
3. [`request`](#request)
4. [`SystemIO`](#SystemIO)
5. [`times`](#times)
6. [`websocket`](#websocket)
7. [`mutex`](#mutex)
8. [Making your own](#Making%20your%20own)
9. [Notes](#Notes)

## `FileIO`

This is used for file input and output:

```js
import FileIO
```

`FileIO.write: (str, str) -> cmd[()]`:
Takes in a path to a file and writes the data wanted into it, this does clear the file and will create it if it does not exist.

```js
FileIO.write("test.txt", "test")!
```

`FileIO.append: (str, str) -> cmd[()]`:
Takes in a path to a file and writes the data wanted into it, this does not clear the file and will create it if it does not exist.

```js
FileIO.append("test.txt", "test")!
```

`FileIO.read: (str) -> cmd[maybe[str]]`:
Takes in a path to a file and reads the data in it, returns it as a string if it does exist.

```js
FileIO.read("test.txt")! |> default("")
```

`FileIO.writeBytes: (str, list[int]) -> cmd[()]`:
Takes in a path to a file and writes the data wanted into it, this does clear the file and will create it if it does not exist.

```js
FileIO.writeBytes("test.txt", [32, 33, 34, 35])!
```

`FileIO.appendBytes: (str, list[int]) -> cmd[()]`:
Takes in a path to a file and writes the data wanted into it, this does not clear the file and will create it if it does not exist.

```js
FileIO.appendBytes("test.txt", [32, 33, 34, 35])!
```

`FileIO.readBytes: (str) -> cmd[maybe[list[int]]]`:
Takes in a path to a file and reads the data in it, returns it as a list of bytes if it does exist.

```js
FileIO.readBytes("test.txt")! |> default([])
```

`FileIO.getFiles: (str) -> cmd[list[(bool, str)]]`:
Requires the `FILE_ALLOW` environment variable to be set to `true`, takes in a path and returns all of the files/folders there, the `bool` in the output indicates whether it is a file or not.

```js
FileIO.getFiles("./")!
```

## `json`

This is used for dealing with `json` information:

```js
import json
```

`json.value`: An enum that is the main way that `json` deals with info:

```js
type pub value = object(map[str, value])
               | number(float)
               | string(str)
               | boolean(bool)
               | null
```

`json.stringify: (json.value) -> str`:
This takes a json value and turns it into a string for ease of use.

```js
print(json.stringify(value))
```

`json.parse: (str) -> json.value`:
This takes in a string and will return a `json.value` in an attempt to parse it, if it cannot parse it then it will return a `json.null`

```js
print(json.parse('{ test: "test" }'))
```

`json.parseSafe: (str) -> maybe[json.value]`:
This takes in a string and will return a `json.value` in an attempt to parse it, if it cannot parse it then it will return `none`

```js
print(json.parseSafe("{ test: \"test\" }") |> default(json.string("invalid")))
```

## `request`

Used for http related activities:

```js
import request
```

`request.request: (str, str, maybe[json.value], maybe[json.value]) -> cmd[{ code: int, response: str, return: json.value }]:`:
This takes in a url, request type, headers, and data to send and gives back the request reponse

```js
request.post("github.com", "GET", none, none)! // Gets github.com's base page
```

`request.createServer: int -> ( (str, str, json.value) -> cmd[{ responseCode: int, data: list[int], headers: map[str, str], mimetype: str }] ) -> cmd[()]`:
This takes in a port to open to and a function which takes in a path, request type, and additional data and returns a response code, the data in bytes, headers, and the MIME type for the data given and opens a server on `http://localhost:<PORTNUMBER>`

```js
request.createServer(
  3000,
  (path:str requestType:str, additionalData:str) -> cmd[{ responseCode: int, data: list[int], headers: map[str, str], mimetype: str }] {
    return {
      responseCode: 200,
      data: [32, 33, 34, 35],
      headers: mapFrom([]),
      mimetype: "text/plain",
    }
  }
)!
```

## `SystemIO`

Used for interacting with the console:

```js
import SystemIO
```

`SystemIO.inp: (str) -> cmd[str]`:
Takes in a string and prints it out and awaits user input, once it is inputted it will give back the input

```js
print("You said: " + SystemIO.inp("hello! ")!)
```

`SystemIO.run: (str) -> cmd[bool]`:
Requires the `COMMAND_ALLOW` environment variable to be set to `true`, takes in a string and runs the command in the terminal, returns `true` if it was successful

```js
SystemIO.run("echo hello")!
```

`SystemIO.sendSTDOUT: [t] (t) -> cmd[t]`:
Prints to the STDOUT, this does not append a newline to the end.
```js
SystemIO.sendSTDOUT("Printing to the STDOUT\n")!
```

## `times`

Used for stopping the program and getting the current time:

```js
import times
```

`times.sleep: (int) -> cmd[()]`:
Takes in an integer and stops the thread it is in for that many milliseconds

```js
times.sleep(1000)!
```

`times.getTime: (()) -> cmd[float]`:
Returns the current epoch time

```js
times.getTime()!
```

## `websocket`

Used for websocket related activities

```js
import websocket
```

`websocket.send: (str) -> cmd[result[(), int]]`:
This is a type used for sending data in a websocket, if it does not have an error it will return an `ok(())` otherwise it will return an `err` with the error code it got.

```js
alias send = str -> cmd[()]
```

`websocket.close: () -> cmd[()]`:
Currently unused.

`websocket.user: { send: str -> cmd[()], disconnect: () -> cmd[()], ip: (int, int, int, int), uuid: str }`:
Used as an individual user when hosting a websocket server.

```js
alias user = {
  send: str -> cmd[()]
  disconnect: () -> cmd[()]
  ip: (int, int, int, int)
  uuid: str
}
```

`websocket.connect: ({ onOpen: websocket.send -> cmd[bool], onMessage: websocket.send -> cmd[bool] }, str) -> cmd[maybe[str]]`:
Connects to a websocket, `onOpen` and `onMessage` run in parallel and if either return `true` it will exit out of both, the `str` is an error message that my occur when connecting.

```js
let websocketTest = websocket.connect({
  onOpen: [send: websocket.send] -> cmd[bool] {
    print("Open!")
    let _ = send("hi")!
    return false
  }
  onMessage: [send: websocket.send message: str] -> cmd[bool] {
    print(message)
    let _ = send("hello")!
    return message == "hello"
  }
}, "wss://echo.websocket.org")!
```

`websocket.createServer: ({ onConnect: (websocket.user, str) -> cmd[bool], onMessage: (websocket.user, str) -> cmd[bool], onDisconnect: (websocket.user, { code: int, reson: str }) -> cmd[bool] }, int) -> cmd[()]`:
Opens a websocket server on `ws://localhost:<PORTNUMBER>`. Runs `onConnect` when a user connects, `onMessage` runs when a user sends a message, and `onDisconnect` will run when a user disconnects, if either of these return `true` then the websocket server will close.

```js
websocket.createServer(
  {
    onConnect: (user:websocket.user, path:str) -> cmd[bool] {
      print(user)
      user.send("hello")!
      return false
    }
    onMessage: (user:websocket.user, message:str) -> cmd[bool] {
      print(message)
      user.send(message)!
      return false
    }
    onDisconnect: (user:websocket.user, exitData:maybe[{ code: int, reason:str }]) -> cmd[bool] { return false }
  },
  3000
)!
```

## `mutex`

Mutex is a way of locking variables to avoid race conditions when implementing parallelism. You can pass in a value and get a `mutex.locked` which you can then attempt to lock and get a `mutex.unlocked`, which you can read or write to. While one thread has locked the mutex value, no other thread is able to access it until it unlocks it again. Mutex values do not need the `mut` modifier applied to them.

`mutex.new: [t] (t) -> mutex.locked[t]`:
Creates a new `mutex.locked` value from the value passed in.

```js
let mutexValue = mutex.new(0)
```

`mutex.tryAccess: [a, b] (mutex.unlocked[a] -> cmd[b], mutex.locked[a]) -> cmd[maybe[b]]`
Attempts to access the `mutex.locked` if it locked by another thread then it will continue without running the function. If it unlocked then it runs the function passed in and returns its result.

```js
mutexValue
          |> mutex.tryAccess(
            (unlocked: mutex.unlocked[int]) -> cmd[()] {
              // Do stuff with mutex
            }
          )!
```

`mutex.access: [a, b] (mutex.unlocked[a] -> cmd[b], mutex.locked[a]) -> cmd[b]`
Same as `mutex.tryAccess` but it will wait for the value to be unlocked so it can run the function passed in before continuing.

```js
mutexValue
          |> mutex.access(
            (unlocked: mutex.unlocked[int]) -> cmd[()] {
              // Do stuff with mutex
            }
          )!
```

`mutex.read: [t] (mutex.unlocked[t]) -> cmd[t]`
Reads the value contained in a `mutex.unlocked`.

```js
let val = unlocked
                  |> mutex.read()!
```

`mutex.write: [t] (t, mutex.unlocked[t]) -> cmd[t]`
Writes a value to a `mutex.unlocked` and returns the value.

```js
unlocked
        |> mutex.write(val + 1)!
```

## Making your own

Whenever the `import` keyword is called with a name that does not match one of these libraries, N will check for a python file of the same name in the directory, if it finds one it will check if it has a function called `_values`, if this is successful then it will treat the file as a mapping for python.

The `_values` function returns a dictionary of strings, which equate to the names of the functions, and types in the N syntax. These types are represented as such:

- `str`, `int`, `float`, `bool`, and `char` are represented as their name wrapped in quotes (`"str"`)
  - `char`s at runtime are represeted as one length strings
- `list[t]` is `n_list_type.with_typevars([t])`
- `map[k, v]` is `n_map_type.with_typevars([k, v])`
  - Respresented as a dictionary during runtime
- `cmd[t]` is `n_cmd_type.with_typevars([t])`
  - Represented as a `Cmd` object from `ncmd.py` at runtime
- `maybe[t]` is `n_maybe_type.with_typevars([t])`
  - All enum values are represented as an `EnumValue` from `enums.py`
- `result[o, e]` is `n_result_type.with_typevars([o, e])`, `n_result_type` comes from `native_types.py`
- `module` is `n_module_type.with_typevars([])`
  - Represented as a `NModuleWrapper` from `type.py` at runtime
- Records are represented as dictionaries during type checking and runtime

The `_types` function is optional but if included must return a dictionary of strings to types. These types must be of the class `NTypeVars` from `type.py`

These files may in the future be part of a Pypi library for ease of access.


## Notes

- All of these are written in Python or JavaScript.
- Later there may be a way to write your own, but this is unlikely.
- The imported libraries are not records, but record-like.
