import json
import random
import threading
import urllib.parse
import logic
from network_packet import RequestPacket
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

logic_obj = logic.Logic()

class ApiServer:
    class RequestHandler(BaseHTTPRequestHandler):

        def parser(self, method : str) -> RequestPacket:
            result = RequestPacket()

            result.headers = self.headers
            result.method = method

            used_proxy = self.headers.get("X-Forwarded-For") is not None
            if used_proxy:
                result.proxy_ip = self.client_address[0]
                result.client_ip = self.headers.get("X-Forwarded-For")
            else:
                result.client_ip = self.client_address[0]

            result.full_url = self.path

            if "Content-Length" in self.headers:
                length = int(self.headers.get('Content-Length'))
                result.body = self.rfile.read(length)

            if "Content-Type" in self.headers and "application/json" in self.headers.get("Content-Type"):
                result.json_root = json.loads(result.body.decode())

            if "User-Agent" in self.headers:
                result.user_agent = self.headers.get('User-Agent')

            if "?" in result.full_url:
                query = result.full_url[result.full_url.find("?") + 1:]
                data = dict(urllib.parse.parse_qsl(query))
                result.json_root = result.json_root | data

                result.api_endpoint = result.full_url[:result.full_url.find("?")]
            else:
                result.api_endpoint = result.full_url[result.full_url.find("/"):]

            if result.json_root is not None and "indent" in result.json_root:
                result.requested_indent = int(result.json_root.get("indent", 4))

            return result

        def handler(self, method):
            try:
                request = self.parser(method)
            except Exception as e:
                self.send_error(400)
                self.end_headers()
                return

            if "Bot" in request.user_agent:
                self.send_error(403)
                self.end_headers()
                return

            i = random.randint(10, 99)
            print(i, "new request from " + request.client_ip + ":", request.api_endpoint, request.json_root)

            try:
                answer = logic_obj.work_packet(request)
            except Exception as e:
                print(e)
                self.send_error(500)
                self.end_headers()
                raise e # todo: remove after debug
                return

            if answer is None:
                self.send_error(501)
                self.end_headers()
                return

            print(i, "answer for " + request.client_ip + ":", answer)

            if answer.get("_backend", "") != "":
                if answer["_backend"]["act"] == "redirect":
                    self.send_response(307)
                    self.send_header("Location", answer["_backend"]["loc"])
                    self.end_headers()
                if answer["_backend"]["act"] == "error":
                    self.send_error(answer["_backend"]["code"])
                    self.end_headers()

            else:
                self.send_response(200)
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()

                answer = json.dumps(answer, indent=request.requested_indent)
                answer = answer.encode(encoding="utf-8")
                self.wfile.write(answer)


        def do_GET(self):
            self.handler("get")

        def do_POST(self):
            self.handler("post")

    def start_server(self, host, port, blocking = True):
        if blocking:
            self.__internal_start_server(host, port)
        else:
            threading.Thread(target=self.__internal_start_server, args=(host, port), name="main_server_thread").start()

    def __internal_start_server(self, host, port):
        server = ThreadingHTTPServer((host, port), self.RequestHandler)
        server.serve_forever()

