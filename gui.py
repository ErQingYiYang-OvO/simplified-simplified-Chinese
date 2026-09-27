"""Local, read-only dictionary viewer. Python standard library only."""
from __future__ import annotations

import argparse
import json
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

from library import CATALOGS, ROOT, CatalogError, Library


class Viewer(BaseHTTPRequestHandler):
    library = Library()

    def log_message(self, format, *args):
        pass

    def respond(self, status, content, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; object-src 'none'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(content)

    def json_response(self, status, value):
        self.respond(status, json.dumps(value, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def do_GET(self):
        request = urlsplit(self.path)
        params = parse_qs(request.query)
        try:
            if request.path in ("/", "/app.js", "/style.css"):
                filename, mime = {
                    "/": ("index.html", "text/html; charset=utf-8"),
                    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
                    "/style.css": ("style.css", "text/css; charset=utf-8"),
                }[request.path]
                self.respond(200, (ROOT / "viewer" / filename).read_bytes(), mime)
            elif request.path == "/api/catalog":
                kind = params.get("kind", ["dictionary"])[0]
                if kind not in CATALOGS:
                    self.json_response(400, {"error": "未知目录"})
                    return
                self.json_response(200, {
                    "entries": self.library.search(kind, params.get("q", [""])[0], params.get("method", [""])[0]),
                    "counts": self.library.validate(),
                    "methods": self.library.methods(),
                })
            elif request.path == "/asset":
                kind = params.get("kind", [""])[0]
                identity = params.get("id", [""])[0]
                if kind not in ("components", "glyphs", "dictionary"):
                    self.json_response(404, {"error": "未找到轮廓"})
                    return
                record = next((item for item in self.library.search(kind) if item["id"] == identity), None)
                if record is None:
                    self.json_response(404, {"error": "未找到轮廓"})
                    return
                folder = "components" if kind == "components" else "glyphs"
                self.respond(200, self.library.asset(record["outline"], folder).read_bytes(), "image/svg+xml")
            else:
                self.json_response(404, {"error": "未找到页面"})
        except CatalogError as error:
            self.json_response(422, {"error": str(error)})
        except OSError:
            self.json_response(500, {"error": "无法读取界面或轮廓文件"})

    def reject_write(self):
        self.json_response(405, {"error": "此字典只提供查询，不允许修改"})

    do_POST = do_PUT = do_PATCH = do_DELETE = reject_write


def main():
    parser = argparse.ArgumentParser(description="启动本机只读字典 GUI")
    parser.add_argument("--open", action="store_true", help="自动打开浏览器")
    parser.add_argument("--port", type=int, default=0, help="指定本机端口，默认自动选择空闲端口")
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Viewer)
    url = f"http://127.0.0.1:{server.server_port}/"
    print(f"再简字字典：{url}\n此界面只读。关闭此窗口或按 Ctrl+C 停止服务。", flush=True)
    if args.open:
        threading.Timer(0.3, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
