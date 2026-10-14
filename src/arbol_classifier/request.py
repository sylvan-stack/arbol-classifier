"""The request on standard input, and the body that goes to Jev (CLS-0, "The request and the result").

Only what CLS-0 lists is checked before the call: one JSON object with a `state` and at
least one question, a `type` and `instructions` in every question, no `model`, and the
size of the body as it is sent. No question is interpreted, and nothing is cut.
"""

from .errors import Failure
from .json_types import Json, Object, dumps, loads


def read_request(data: bytes) -> Object:
    try:
        value = loads(data.decode("utf-8"))
    except (ValueError, RecursionError):
        raise Failure("invalid_input", "The request on standard input is not one JSON document.") from None
    if not isinstance(value, dict):
        raise Failure("invalid_input", "The request must be one JSON object.")
    if "model" in value:
        raise Failure(
            "invalid_input", "The request names a model. arbol-classifier asks for the Jev version of its settings."
        )
    if "state" not in value:
        raise Failure("invalid_input", "The request has no state, the text or the data to judge.")
    questions = value.get("questions")
    if not isinstance(questions, dict) or not questions:
        raise Failure("invalid_input", "The request needs questions: a JSON object with at least one named question.")
    for question in questions.values():
        if not isinstance(question, dict) or "type" not in question or "instructions" not in question:
            raise Failure("invalid_input", "Every question must be a JSON object with a type and instructions.")
    return value


def question_names(request: Object) -> list[str]:
    questions: Json = request["questions"]
    assert isinstance(questions, dict)
    return list(questions)


def body_for_jev(request: Object, model: str, max_bytes: int) -> bytes:
    """The request with `model` added, as it is sent; refused when it is larger than the limit."""
    try:
        body = dumps({**request, "model": model}).encode("utf-8")
    except UnicodeEncodeError:
        raise Failure("invalid_input", "The request holds text that is not valid Unicode.") from None
    except (ValueError, RecursionError):
        raise Failure("invalid_input", "The request holds a number too large to pass on.") from None
    if len(body) > max_bytes:
        raise Failure(
            "invalid_input",
            f"The request is {len(body)} bytes as it would be sent to Jev, more than the limit of {max_bytes}. "
            "Nothing was sent.",
        )
    return body
