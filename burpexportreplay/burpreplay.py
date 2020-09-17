from burpexportreplay import burpexport, multiprocessor
import socket, ssl, time
import re, base64
import multiprocessing

def resendItems(items, threads=1, host = False, port = False, proxy_host = False, proxy_port = False):
    jobs = []
    for item in items:
        args = {"item": item, "host": host, "port": port, "proxy_host": proxy_host, "proxy_port": proxy_port}
        jobs.append(multiprocessing.Process(target=resendItem, kwargs=args))

    multiprocessor.runJobs(jobs, threads)

def resendItem(item, host = False, port = False, proxy_host = False, proxy_port = False):
    if host == False:
        host = burpexport.getItemHost(item)

    if port == False:
        port = burpexport.getItemPort(item)
        
    sendRequest(
        host, port,
        burpexport.getItemProtocol(item),
        burpexport.getItemRequest(item),
        False, proxy_host, proxy_port
    )

def sendRequest(host, port, protocol, request, updateHostHeader = False, proxy_host = False, proxy_port = False):
    debug = False

    if updateHostHeader:
        request = updateRequestHost(request, host, port)
    
    if proxy_host == False:
        print("[*] Connecting to host %s:%s" % (host, port))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, int(port)))
    else:
        print("[*] Connecting to proxy %s:%s" % (proxy_host, proxy_port))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((proxy_host, int(proxy_port)))
    
    sock.settimeout(5)

    if proxy_host != False:
        print("... Sending connect to %s:%s" % (host, port))
        conn_str = "CONNECT %s:%s HTTP/1.1\r\nConnection: close\r\n\r\n" % (host, port)
        sock.sendall(conn_str.encode("utf-8"))

        if debug:
            print("")
            print(conn_str)

        s = ""
        while s[-4:] != "\r\n\r\n":
            s += sock.recv(1).decode("utf-8")

        if debug:
            print(s)
    
    if protocol == 'https':
        if debug:
            print("... Establishing SSL Connection")

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        sock = context.wrap_socket(sock, server_hostname=host)

        if debug:
            print("... SSL version: %s" % sock.version())
    
    request = updateRequestContentLength(request)

    print("... Sending request content: %s ... (%s bytes)" % (
            request[:64].decode("utf-8").split("\n")[0].strip(), len(request)
    ))

    if debug:
        print("")   
        print(request.decode("utf-8"))
        print("")
    
    sock.setblocking(0)
    sock.settimeout(3)

    totalsent = 0
    while totalsent < len(request):
        try:
            sent = sock.send(request[totalsent:])
            if sent == 0:
                raise RuntimeError(".. [*] Socket connection broken")
            totalsent = totalsent + sent 
        except OSError:
            print('... [!] Error')

    sock.send("\r\n".encode("utf-8"))

    if sent == 0:
        raise RuntimeError(".. [*] Socket connection broken")

    print("... Sent %s bytes to %s:%s" % (totalsent, host, port))
    
    try:
        response = sock.recv()
        print("... Recieved %s bytes from %s:%s" % (len(response), host, port))
    except:
        print("... Response took too long")
    
    sock.close

def replaceXmlTagData(item, tag, data):
    item.getElementsByTagName(tag).item(0).firstChild.data = data

def replaceItemRequest(item, request):
    replaceXmlTagData(item, 'request', base64.b64encode(request))

def updateRequestHost(request, host, port):
    return re.sub(b'(Host:) (.*)', rb'\1 ' + host + b':' + bytes(str(port), "ascii") + b'\r\n', request)

def addRequestHeader(request, header, value):
    parts = request.split(b'\x0d\x0a\x0d\x0a')
    return parts[0][:-4] + b'\r\n' + header + b': ' + value + b'\r\n' + b'\x0d\x0a\x0d\x0a' + parts[1]

def updateRequestHeader(request, header, value):
    return re.sub(b'(' + header + b': ).*?\n', br'\1' + value + b'\r\n', request)

def updateRequestUserAgent(request, value):
    return re.sub(b'(User-Agent: ).*?\n', br'\1' + value + b'\r\n', request)

def updateRequestContentLength(request):
    return re.sub(b'(Content-Length: )(\\d+)', b'Content-Length: ' + bytes(str(len(request.split(b'\x0d\x0a\x0d\x0a')[1])), "ascii"), request)

def updateRequestAuthorization(request, name, value):
    return re.sub(b'(Authorization:.*?)(' + name + b' .*?)([;|\r\n])', br'\1' + name + b' ' + value + br'\3', request)

def updateRequestXCsrfToken(request, value):
    return re.sub(b'(X\\-CSRF\\-TOKEN: ).*?\n', br'\1' + value + b'\r\n', request)

def updateRequestCookie(request, cookie, value):
    return re.sub(b'(Cookie:.*?)(' + cookie + b'=.*?)([;|\n])', br'\1'+ cookie + b'=' + value + br'\3', request)

def updateRequestBody(request, data):
    return request.split(b'\x0d\x0a\x0d\x0a')[0] + b'\x0d\x0a\x0d\x0a' + data + b'\x0a'

def updateRequestSoapParameter(request, parameter, payload):
    return re.sub(b'(<' + parameter + b'>)(.*?)(</' + parameter + b'>)', br'\1' + urllib.quote(payload) + br'\3', request)
