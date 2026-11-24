"""JSON API blueprint collection."""

from flask import Blueprint

api_bp = Blueprint("api", __name__, url_prefix="/api")

# Imports register the endpoints on the shared blueprint.
from . import account  # noqa: E402,F401
from . import auth  # noqa: E402,F401
from . import execution  # noqa: E402,F401
from . import ide  # noqa: E402,F401
from . import learning  # noqa: E402,F401
from . import snippets  # noqa: E402,F401
