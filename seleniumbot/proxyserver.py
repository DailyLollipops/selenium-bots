from .dummylogger import DummyLogger
from .proxyfactory import ProxyFactory
from .utils import stringutil

from logging import Logger

import http.server
import socketserver
import base64
import threading
import requests
import socket
import select


class ProxyServerException(Exception):
    pass


class Proxy(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, host=None, port=None, username=None, password=None, logger: Logger = None,  debug: bool = False, **kwargs):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.logger = logger or DummyLogger()
        self.debug = debug

        if self.username and self.password:
            self.credentials = base64.b64encode(f'{self.username}:{self.password}'.encode('utf-8')).decode('utf-8')
        else:
            self.credentials = None
        
        super().__init__(*args, **kwargs)



    def log_message(self, format, *args):
        if self.debug:
            self.logger.debug(format % args)



    def do_GET(self):
        self.send_proxy_request()



    def do_POST(self):
        self.send_proxy_request()



    def do_DELETE(self):
        self.send_proxy_request()



    def do_PATCH(self):
        self.send_proxy_request()


    
    def do_CONNECT(self):
        self.handle_connect()



    def send_proxy_request(self):
        target_url = self.path
        
        proxy_url = f"http://{self.host}:{self.port}"
        proxies = {
            "http": proxy_url,
            "https": proxy_url,
        }
        
        headers = {key: value for key, value in self.headers.items()}
        
        if self.credentials:
            headers['Proxy-Authorization'] = f'Basic {self.credentials}'
        
        try:
            if self.command == 'GET':
                response = requests.get(target_url, headers=headers, proxies=proxies)
            elif self.command == 'POST':
                length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(length)
                response = requests.post(target_url, headers=headers, data=post_data, proxies=proxies)
            elif self.command == 'DELETE':
                response = requests.delete(target_url, headers=headers, proxies=proxies)
            elif self.command == 'PATCH':
                length = int(self.headers['Content-Length'])
                patch_data = self.rfile.read(length)
                response = requests.patch(target_url, headers=headers, data=patch_data, proxies=proxies)
            else:
                self.logger.warning(f'Received unallowed method: {self.command}')
                self.send_response(405, 'Method Not Allowed')
                self.end_headers()
                return
            
            self.send_response(response.status_code)
            for key, value in response.headers.items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(response.content)
        except requests.exceptions.RequestException as e:
            self.logger.warning(f'Error during proxy request: {e}')
            self.send_response(500, 'Internal Server Error')
            self.end_headers()



    def handle_connect(self):
        target_host, target_port = self.path.split(':')
        target_port = int(target_port)

        try:
            with socket.create_connection((self.host, self.port)) as proxy_socket:
                connect_request = f'CONNECT {self.path} HTTP/1.1\r\n'
                connect_request += f'Host: {self.path}\r\n'
                if self.credentials:
                    connect_request += f'Proxy-Authorization: Basic {self.credentials}\r\n'
                connect_request += '\r\n'
                proxy_socket.sendall(connect_request.encode())

                response = proxy_socket.recv(4096).decode()

                if 'HTTP/1.1 402 ACCOUNT IS INACTIVE' in response.upper():
                    raise ProxyServerException('Proxy account inactive')
                
                if 'HTTP/1.1 200 CONNECTION ESTABLISHED' not in response.upper():
                    self.send_response(502, 'Bad Gateway')
                    self.end_headers()
                    if self.debug:
                        self.logger.debug(f'CONNECT response from proxy: {response}')
                    return

                self.send_response(200, 'Connection Established')
                self.send_header('Proxy-Connection', 'Keep-Alive')
                self.end_headers()

                self.relay_data(self.connection, proxy_socket)
        except ProxyServerException as e:
            self.send_response(500, 'Internal Server Error')
            self.end_headers()
            self.logger.warning(f'Error in CONNECT method: {e}')
        except ConnectionRefusedError as e:
            self.logger.warning('Error in CONNECT method: Connection refused')



    def relay_data(self, client_socket, proxy_socket):
        try:
            while True:
                readable, _, _ = select.select([client_socket, proxy_socket], [], [])
                if client_socket in readable:
                    data = client_socket.recv(4096)
                    if not data:
                        break
                    proxy_socket.sendall(data)
                if proxy_socket in readable:
                    data = proxy_socket.recv(4096)
                    if not data:
                        break
                    client_socket.sendall(data)
        except socket.error as e:
            if e.errno == 104:
                self.logger.warning('Socket error during data relay: [Errno 104] Connection reset by peer')
            else:
                self.logger.warning(f'Socket error during data relay: {e}')
        finally:
            client_socket.close()
            proxy_socket.close()


class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    """Handle requests in a separate thread."""


class ProxyServer:
    def __init__(self, url: str, logger: Logger = None, debug: bool = False) -> None:
        """
        Initialize a proxy server to given proxy url.  \n
        Proxy url can be authenticated.

        Valid url formats:
        - {password}:{host}
        - http://{password}:{host}
        - http://{username}:{password}@{host}:port

        :param url: proxy url
        """
        proxy_info = stringutil.decompose_proxy_url(url)
        self.debug = debug
        self.proxy_host = proxy_info['host']
        self.proxy_port = proxy_info['port']
        self.proxy_username = proxy_info['username']
        self.proxy_password = proxy_info['password']
        self.server_url = ''
        self.httpd: ThreadedHTTPServer = None
        self.server_thread: threading.Thread = None
        self.logger = logger or DummyLogger()
        self.logger.info(proxy_info)
        self.logger.info(f'Debug: {debug}')



    def start(self, port=0):
        """
        Start proxy server

        :param port: Port to bind to (default to 0)
        """
        if isinstance(self.httpd, ThreadedHTTPServer):
            return
        
        handler = lambda *args, **kwargs: Proxy(*args, 
                                                host=self.proxy_host, 
                                                port=self.proxy_port, 
                                                username=self.proxy_username,
                                                password=self.proxy_password,
                                                logger=self.logger,
                                                debug=self.debug,
                                                **kwargs
                                               )
        server_address = ('', port)
        self.httpd = ThreadedHTTPServer(server_address, handler)
        
        self.server_thread = threading.Thread(target=self.httpd.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        assigned_port = self.httpd.server_address[1]
        self.logger.info(f'Proxy server started on port {assigned_port}')
        return assigned_port



    def stop(self):
        """
        Stop proxy server
        """
        if not self.httpd:
            return
        
        self.logger.info('Stopping proxy server')
        self.httpd.shutdown()
        self.httpd.server_close()
        self.logger.info('Proxy server stopped')
        self.httpd = None
        self.server_thread.join()
