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

def hasCsrfToken(item, verbose = False):
    request = burpexport.getItemRequest(item)

    csrfTokens = [
            b'Token', b'CSRF', b'CSRFToken', b'antiCSRF',
            b'__RequestVerificationToken', b'RequestVerificationToken'
            b'antiForgery', b'Forgery', b'X-CSRF-TOKEN'
    ]

    for csrfToken in csrfTokens:
        if b'&' + csrfToken + b'=' in request:
            if verbose:
                print("[*] Found \"%s\" token in %s" % (csrfToken, burpexport.getItemPath(item)))

            return True

    return False

def printCsrfVulns(items, excludes):
    actions = []

    for item in items:
        action = "%s %s" % (burpexport.getItemMethod(item), burpexport.getItemPath(item))
        if action in excludes:
            print("[*] Skipping %s" % (action))
            continue

        if (burpexport.getItemMethod(item) == 'POST'):
            request = burpexport.getItemRequest(item)
            if not hasCsrfToken(item, True):
                if (action not in actions):
                    actions.append(action) 

    print("No anti-CSRF token found in requests to these urls:")
    for action in sorted(actions):
        print(action)

printCsrfVulns(items, '')
