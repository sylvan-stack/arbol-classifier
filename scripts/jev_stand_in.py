"""A stand-in for Jev on this Mac, for the contract check (CLS-0, "Checks, and when a Build counts as working").

A small HTTP server on the loopback address, in a thread of the check. It answers every
request by a script, a function from what it was sent to what it answers, and records
everything it was sent: the method, the path, the headers, the body and when it arrived.
A script can also close the connection without an answer (`DROP`), hold the answer until
the stand-in ends (`hold`), or send it one byte at a time (`drip`): the ways a slow Jev
looks to the classifier.
"""

from __future__ import annotations

import json
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any


@dataclass(frozen=True)
class Received:
    method: str
    path: str
    headers: list[tuple[str, str]]
    body: bytes
    at: float  # time.monotonic() when it arrived

    def json(self) -> Any:
        return json.loads(self.body)


@dataclass(frozen=True)
class Reply:
    status: int
    body: bytes
    headers: tuple[tuple[str, str], ...] = ()
    drip: float = 0.0  # seconds between two bytes of the body; 0 sends it at once

    @staticmethod
    def of(value: object, status: int = 200, headers: tuple[tuple[str, str], ...] = ()) -> Reply:
        return Reply(status, json.dumps(value).encode("utf-8"), headers)


DROP = Reply(0, b"")  # close the connection without an answer

type Script = Callable[[Received], Reply]


def answer_for(question: dict[str, Any]) -> dict[str, Any]:
    """An answer in the form Jev gives for the kind of the question (CLS-0, "The request and the result")."""
    kind = question.get("type")
    if kind == "choice":
        options = list(question.get("criteria") or {})
        probabilities = {option: (0.9 if index == 0 else 0.1 / (len(options) - 1)) for index, option in
                         enumerate(options)}
        return {"type": "choice", "choice": options[0] if options else None, "confidence": 0.87,
                "probabilities": probabilities}
    if kind == "noul":
        return {"type": "noul", "noul": 0.93}
    if kind == "score":
        levels = list(question["criteria"])
        return {"type": "score", "score": len(levels) - 1, "legend": {str(index): level for index, level in
                enumerate(levels)}, "probabilities": {str(index): 1 / len(levels) for index in range(len(levels))},
                "confidence": 0.71}
    return {"type": kind}


def like_jev(received: Received) -> Reply:
    """Answer every question asked, with the model that was asked for, as Jev would."""
    request = received.json()
    answers = {name: answer_for(question) for name, question in request["questions"].items()}
    return Reply.of({"model": request["model"], "answers": answers, "usage": {"input_tokens": 212, "output_tokens": 30}})


class StandIn:
    def __init__(self, script: Script = like_jev) -> None:
        self.script = script
        self.received: list[Received] = []
        self.replies: list[Reply] = []
        self.ended = threading.Event()
        lock = threading.Lock()
        stand_in = self

        class Handler(BaseHTTPRequestHandler):
            def answer(self) -> None:
                length = int(self.headers.get("Content-Length") or 0)
                received = Received(self.command, self.path, list(self.headers.items()), self.rfile.read(length),
                                    time.monotonic())
                with lock:
                    stand_in.received.append(received)
                    script = stand_in.script
                reply = script(received)
                with lock:
                    stand_in.replies.append(reply)
                if reply is DROP:
                    self.close_connection = True
                    return
                self.send_response(reply.status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(reply.body)))
                for name, value in reply.headers:
                    self.send_header(name, value)
                self.end_headers()
                if not reply.drip:
                    self.wfile.write(reply.body)
                    return
                for index in range(len(reply.body)):
                    if stand_in.ended.is_set():
                        return
                    self.wfile.write(reply.body[index:index + 1])
                    self.wfile.flush()
                    time.sleep(reply.drip)

            do_POST = do_GET = do_PUT = do_DELETE = answer

            def log_message(self, format: str, *args: Any) -> None:
                pass

        class Server(ThreadingHTTPServer):
            def handle_error(self, request: Any, client_address: Any) -> None:
                pass  # a classifier that gave up on a held answer closed its end; that is expected

        self.server = Server(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.server.server_address[1]}/v1/systemone"

    def __enter__(self) -> StandIn:
        self.thread.start()
        return self

    def hold(self, reply: Reply) -> Script:
        """A script that answers only when the stand-in ends: a Jev that does not answer in time."""
        def held(received: Received) -> Reply:
            self.ended.wait(30)
            return reply

        return held

    def __exit__(self, *details: object) -> None:
        self.ended.set()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)
