#!/usr/bin/python # vim:ts=4:sts=4:sw=4:et:
import sys, getopt, base64, re
from xml.dom import minidom
import socket, urllib, json
import gzip

# BurpSuite Item elements contain the following elements:
#   <!ELEMENT item (time, url, host, port, protocol, method, path, extension, request, status, responselength, mimetype, response, comment)>
#   url = getXmlTagData(item, 'url')
#
def loadItems(files):
    items = minidom.NodeList()

    for file in files:
        xml = minidom.parse(file)
        items.extend(xml.getElementsByTagName('item'))

    return items

def getXmlTagData(item, tag):
    return item.getElementsByTagName(tag).item(0).firstChild.data

def getItemRequest(item):
    return base64.b64decode(getXmlTagData(item, 'request'))

def getItemResponse(item):
    return base64.b64decode(getXmlTagData(item, 'response'))

def getItemHost(item):
    return getXmlTagData(item, 'host')

def getItemPath(item):
    return getXmlTagData(item, 'path')

def getItemPort(item):
    return getXmlTagData(item, 'port')

def getItemProtocol(item):
    return getXmlTagData(item, 'protocol')

def getItemUrl(item):
    return getXmlTagData(item, 'url')

def getItemMethod(item):
    return getXmlTagData(item, 'method')

def isGzipCompressed(body):
    return body[0:4] == b'\x1f\x8b\x08\x00'

def getRequestBody(request, decompress=False):
    body = None
    parts = request.split(b'\r\n\r\n')

    if len(parts) > 0:
        body = parts[1]
        if decompress:
            body = decompressRequestBody(body)

    return body

def decompressRequestBody(body):
    if isGzipCompressed(body): 
        body = gzip.decompress(body)

    return body

def getRequestHttpPostParameters(request):
    ctmatch = re.search(r'Content-Type: (.*?);', request)
    
    if not hasattr(ctmatch, 'pos'):
        raise Exception("Content-Type not specified!")
    
    contentType = ctmatch.group(1)
    
    if contentType == 'application/json':
        match = re.search(r'\r\n\r\n(.*$)', request)
        if not hasattr(match, 'pos'):
            open('post-request.txt','w').write(request)
            raise Exception("Unable to parse application/json POST data!")
        params = json.loads(match.group(1))

    elif contentType == 'multipart/form-data':
            raise Exception("Multipart/form-data content type is not supported.")
    else:
        raise Exception("Unsupported Content-Type!")

    return params

def getSoapCall(request):
    match = re.search("(<s:Envelope .*$)", request)

    if not hasattr(match, 'pos'):
        print("... [*] This request does not appear to be a SOAP request!")
        return request

    requestBody = match.group(0)
    requestDom = minidom.parseString(requestBody)
    soapBody = requestDom.getElementsByTagName('s:Body')
    return soapBody.item(0).firstChild

def getSoapParameters(request):
    parameters = []
    soapCall = getSoapCall(request)

    if hasattr(soapCall, 'hasChildNodes'):
        if (soapCall.hasChildNodes()):
            for child in soapCall.childNodes:
                parameters.append(child.localName)

    return parameters

def printMethodPaths(items, printParameters = False):
    actions = []
    for item in items:
        request = getItemRequest(item)
        action = "%s %s" % (getXmlTagData(item, 'method'), getXmlTagData(item, 'path'))
        if (action not in actions):
            actions.append(action) 

    for action in sorted(actions):
        print(action)

