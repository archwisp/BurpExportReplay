#vim:ts=4:sts=4:sw=4:et:
import sys, time
from burpexportreplay import burpexport, burpreplay, multiprocessor 
import json
import copy
import gzip

if len(sys.argv) == 1:
    print("Usage: %s file1.xml {file2.xml file3.xml ...}" % (sys.argv[0]))

files = sys.argv[1:]
items = burpexport.loadItems(files)

for item in items:
    request = burpexport.getItemRequest(item)
    
    # Since we're just printing the data out to review, we can tell the decoder
    # the ignore errors. If you want to see the accurate bytes, remove the
    # decode() call.
    
    print(request.decode("utf-8", errors="ignore"))
    body = burpexport.getRequestBody(request, decompress=False)
    
    if (b'Content-Encoding: gzip' in request):
        if burpexport.isGzipCompressed(body): 
            print("\nDecompressed body:\n")
            print(burpexport.decompressRequestBody(body).decode('utf-8') + "\n")
