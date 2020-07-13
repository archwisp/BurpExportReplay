# BurpExportReplay
BurpExportReplay is a framework for ingesting, analyzing, modifying, and
re-sending items that have been saved from a Burp Suite session. 

I developed this framework many years ago to assist in testing SOAP web
services because Burp didn't handle custom headers or authenticators in the
request body very well. Even these days, I run across encoded request content
that is much easier to deal with when you can script it.

But where this framework really shines is when doing authorization testing.
Once you have gone through the application with your admin user, you can save
all of those request, and start removing or replacing tokens to see what still
works. 

I recommend setting up a new Burp instance, funnelling all of the modified
requests through it, and using Logger++ to assist in review of the results. The
goal is to automate the re-send but review the responses manually.

## Example 
There are a few examples in the `./examples/` directory, but I'll go through a
simple example to show how this works.

To get started, we need a file containing burp items in it. There is an example
file in the `./examples/data/` directory that contains a few requests that get
sent when Firefox starts up.  Or, you can generate your own by highlighting
items in the Proxy -> HTTP history tab, right-clicking on the items, and
selecting Save Items. Leave the Base64 encoding option enabled.

The example below simply loads the files specified on the command-line,
replaces some headers and body content, and re-sends the requests through the
specified proxy.

***examples/replace-and-resend.py:***
```
import sys
from burpexportreplay import burpexport, burpreplay 

if len(sys.argv) == 1:
    print("Usage: %s file1.xml {file2.xml file3.xml ...}" % (sys.argv[0]))

files = sys.argv[1:]
items = burpexport.loadItems(files)
# items = items[0:1]

for item in items:
    request = burpexport.getItemRequest(item)
    request = burpreplay.updateRequestCookie(request, b'ASP.NET_SessionId', b'FAKESESSION')
    request = burpreplay.updateRequestCookie(request, b'.ASPXAUTH', b'FAKEAUTHT')
    request = burpreplay.updateRequestHeader(request, b'User-Agent', b'FAKEAGENT')
    request = burpreplay.updateRequestAuthorization(request, b'bearer', b'FAKEAUTHORIZATION')
    request = burpreplay.updateRequestBody(request, b'FAKEDATA')
    request = burpreplay.updateRequestXCsrfToken(request, b'FAKETOKEN')
    burpreplay.replaceItemRequest(item, request)

burpreplay.resendItems(items, threads=5, proxy_host='127.0.0.1', proxy_port='8080')
```

That's it!

## Installation
This command will build the package and install it in external
mode. That means that you can freely modify the source and your scripts will
reflect those changes immediately, without having to reinstall.

If you want a more trasitional pip install, remove the `-e` flag.  
``` 
git clone https://github.com/archwisp/BurpExportReplay.git
cd BurpExportReplay
python3 -m pip install -e .
```
