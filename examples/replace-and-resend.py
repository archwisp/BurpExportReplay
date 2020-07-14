# vim:ts=4:sts=4:sw=4:et:
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

