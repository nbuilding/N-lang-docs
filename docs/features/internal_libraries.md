# Internal Libraries

Internal Libraries are used to add complicated features from Python and JavaScrpt for users to use in N, you can import these using the `import` keyword. Here are the libraries you can import:

`FileIO`: This is used for file input and output:
```js
import FileIO
```

`FileIO.write: str -> str -> cmd[()]`:
Takes in a path to a file and writes the data wanted into it, this does clear the file and will create it if it does not exist.
```js
FileIO.write("test.txt", "test")!
```

`FileIO.append: str -> str -> cmd[()]`:
Takes in a path to a file and writes the data wanted into it, this does not clear the file and will create it if it does not exist.
```js
FileIO.append("test.txt", "test")!
```

`FileIO.read: str -> cmd[maybe[str]]`:
Takes in a path to a file and reads the data in it, returns it as a string if it does exist.
```js
FileIO.read("test.txt")! |> default("")
```

`FileIO.writeBytes: str -> list[int] -> cmd[()]`:
Takes in a path to a file and writes the data wanted into it, this does clear the file and will create it if it does not exist.
```js
FileIO.writeBytes("test.txt", [32, 33, 34, 35])!
```

`FileIO.appendBytes: str -> list[int] -> cmd[()]`:
Takes in a path to a file and writes the data wanted into it, this does not clear the file and will create it if it does not exist.
```js
FileIO.appendBytes("test.txt", [32, 33, 34, 35])!
```

`FileIO.readBytes: str -> cmd[maybe[list[int]]]`:
Takes in a path to a file and reads the data in it, returns it as a list of bytes if it does exist.
```js
FileIO.readBytes("test.txt")! |> default([])
```

`FileIO.getFiles: str -> cmd[list[(bool, str)]]`:
Requires the `FILE_ALLOW` environment variable to be set to `true`, takes in a path and returns all of the files/folders there, the `bool` in the output indicates whether it is a file or not.
```js
FileIO.getFiles("./")!
```

`json`: This is used for dealing with `json` information:
```js
import json
```

`json.value`: An enum that is the main way that `json` deals with info:
```js
type pub value = <object map[str, value]>
               | <number float>
               | <string str>
               | <boolean bool>
               | null
```

`json.stringify: json.value -> str`:
This takes a json value and turns it into a string for ease of use.
```js
print(json.stringify(value))
```

`json.parse: str -> json.value`:
This takes in a string and will return a `json.value` in an attempt to parse it, if it cannot parse it then it will return a `json.null`
```js
print(json.parse("{ test: \"test\" }"))
```

`json.parseSafe: str -> maybe[json.value]`:
This takes in a string and will return a `json.value` in an attempt to parse it, if it cannot parse it then it will return `none`
```js
print(json.parseSafe("{ test: \"test\" }") |> default(json.string("invalid")))
```

`request`: used for http related activities:
```js
import request
```

`request.get: str -> map[str, str] -> cmd[{ code: int; response: str; return: json.value }:`:
This takes in a url and a set of headers and makes a GET request to the url with those headers
```js
request.get("github.com", mapfrom([("","")]))!
```

`request.post: str -> map[str, str] -> map[str, str] -> cmd[{ code: int; response: str; text: str }`:
This takes in a url, data to send, and headers and makes a POST request to the url with that data.
```js
request.post("github.com", mapFrom(["hello", "hello"]), mapfrom([("","")]))!
```

`request.delete: str -> map[str, str] -> cmd[{ code: int; response: str; return: json.value }:`:
This takes in a url and a set of headers and makes a DELETE request to the url with those headers
```js
request.delete("github.com", mapfrom([("","")]))!
```

`request.head: str -> map[str, str] -> cmd[{ code: int; response: str; return: json.value }:`:
This takes in a url and a set of headers and makes a HEAD request to the url with those headers
```js
request.head("github.com", mapfrom([("","")]))!
```

`request.options: str -> map[str, str] -> cmd[{ code: int; response: str; return: json.value }:`:
This takes in a url and a set of headers and makes a OPTIONS request to the url with those headers
```js
request.options("github.com", mapfrom([("","")]))!
```

`request.patch: str -> map[str, str] -> map[str, str] -> cmd[{ code: int; response: str; text: str }`:
This takes in a url, data to send, and headers and makes a PATCH request to the url with that data.
```js
request.patch("github.com", mapFrom(["hello", "hello"]), mapfrom([("","")]))!
```

`request.put: str -> map[str, str] -> map[str, str] -> cmd[{ code: int; response: str; text: str }`:
This takes in a url, data to send, and headers and makes a PUT request to the url with that data.
```js
request.put("github.com", mapFrom(["hello", "hello"]), mapfrom([("","")]))!
```

`request.createServer: int -> ( str -> str -> json.value -> cmd[{ responseCode: int; data: list[int]; headers: map[str, str]; mimetype: str }] ) -> cmd[()]`:
This takes in a port to open to and a function which takes in a path, request type, and additional data and returns a response code, the data in bytes, headers, and the MIME type for the data given and opens a server on `http://localhost:<PORTNUMBER>`
```js
request.createServer(
  3000,
  [path:str requestType:str additionalData:str] -> cmd[{ responseCode: int; data: list[int]; headers: map[str, str]; mimetype: str }] {
    return {
      responseCode: 200
      data: [32, 33, 34, 35]
      headers: mapFrom([])
      mimetype: "text/plain"
    }
  }
)!
```

`SystemIO`: Used for interacting with the console:
```js
import SystemIO
```

`SystemIO.inp: str -> cmd[str]`:
Takes in a string and prints it out and awaits user input, once it is inputted it will give back the input
```js
print("You said: " + SystemIO.inp("hello! ")!)
```

`SystemIO.run: str -> cmd[bool]`:
Requires the `COMMAND_ALLOW` environment variable to be set to `true`, takes in a string and runs the command in the terminal, returns `true` if it was successful
```js
SystemIO.run("echo hello")!
```

`times`: Used for stopping the program and getting the current time:
```js
import times
```

`times.sleep: int -> cmd[()]`:
Takes in an integer and stops the thread it is in for that many milliseconds
```js
times.sleep(1000)!
```

`times.getTime: () -> cmd[float]`:
Returns the current epoch time
```js
times.getTime()!
```

`websocket`: Used for websocket related activities
```js
import websocket
```

`websocket.send: str -> cmd[result[(), int]]`:
This is a type used for sending data in a websocket, if it does not have an error it will return an `ok(())` otherwise it will return an `err` with the error code it got.
```js
alias send = str -> cmd[()]
```

`websocket.close: () -> cmd[()]`:
Currently unused.

`websocket.user: { send: str -> cmd[()]; disconnect: () -> cmd[()]; ip: (int, int, int, int); uuid: str }`:
Used as an individual user when hosting a websocket server.
```js
alias user = {
  send: str -> cmd[()]
  disconnect: () -> cmd[()]
  ip: (int, int, int, int)
  uuid: str
}
```

`websocket.connect: { onOpen: websocket.send -> cmd[bool]; onMessage: websocket.send -> cmd[bool] } -> str -> cmd[maybe[str]]`:
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

`websocket.createServer: int -> { onConnect: websocket.user -> str -> cmd[bool]; onMessage: websocket.user -> str -> cmd[bool]; onDisconnect: websocket.user -> { code: int; reson: str } -> cmd[bool] }`:
Opens a websocket server on `ws://localhost:<PORTNUMBER>`. Runs `onConnect` when a user connects, `onMessage` runs when a user sends a message, and `onDisconnect` will run when a user disconnects, if either of these return `true` then the websocket server will close.
```js
let _ = websocket.createServer(
  {
    onConnect: [user:websocket.user path:str] -> cmd[bool] {
      print(user)
      let _ = user.send("hello")!
      return false
    }
    onMessage: [user:websocket.user message:str] -> cmd[bool] {
      print(message)
      let _ = user.send(message)!
      return false
    }
    onDisconnect: [user:websocket.user exitData:maybe[{ code: int; reason:str }]] -> cmd[bool] { return false }
  },
  3000
)!
```

## Notes
- All of these are written in python or js.
- Later there may be a way to write your own, but this is unlikely.
- The imported libraries are not records, but record-like.