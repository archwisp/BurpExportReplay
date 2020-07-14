# BurpExportReplay
BurpExportReplay is a framework for ingesting, analyzing, modifying, and
re-sending items that have been saved from a Burp Suite session. 

I created this framework many years ago to assist in testing SOAP web
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
There are a few examples in the `./examples/` directory that show some of the
things you can do, but I'll go through the `replace-and-resend.py` example to
show how this works.

To get started, we need a file containing saved burp items. You can either use
the `./examples/data/sample-burp-items.xml` file included in this project, or
you can generate your own. The included file contains a few requests that get
sent when Firefox starts up. 

To generate your own, select the ***Proxy*** tab, select the ***HTTP
history*** sub-tab, highlight the items you want to re-send, right-click on the
items and select ***Save Items***. Leave the Base64 encoding option enabled.

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

for item in items:
    request = burpexport.getItemRequest(item)
    request = burpreplay.updateRequestCookie(request, b'ASP.NET_SessionId', b'FAKESESSION')
    request = burpreplay.updateRequestCookie(request, b'.ASPXAUTH', b'FAKEAUTH')
    request = burpreplay.updateRequestHeader(request, b'User-Agent', b'FAKEAGENT')
    request = burpreplay.updateRequestAuthorization(request, b'bearer', b'FAKEAUTHORIZATION')
    request = burpreplay.updateRequestBody(request, b'FAKEDATA')
    request = burpreplay.updateRequestXCsrfToken(request, b'FAKETOKEN')
    burpreplay.replaceItemRequest(item, request)

burpreplay.resendItems(items, threads=5, proxy_host='127.0.0.1', proxy_port='8080')
```

Then just run the script like this:
```
python3 examples/replace-and-resend.py examples/data/sample-burp-items.xml
```

That's it! Just watch your proxy history and see the new requests fill in with the replaced contents. 

## Installation
This commands below will build the package from this repository and install it
in external mode. That means that you can freely modify the source and your
scripts will reflect those changes immediately, without having to reinstall.

If you want a more trasitional pip install, remove the `-e` flag.  
``` 
git clone https://github.com/archwisp/BurpExportReplay.git
cd BurpExportReplay
python3 -m pip install -e .
```
