"""Level 3 — Advanced knowledge-library topics."""

from .helpers import T, calls, ex

TOPICS = [
    T(
        "decorators", "Decorators", 3, "Advanced Python",
        "Wrapping functions to add behaviour without changing their bodies.",
        "A decorator is a callable that receives a function and returns a replacement. The `@timer` "
        "syntax is shorthand for `fn = timer(fn)`. Use `functools.wraps(original)` inside the wrapper so "
        "the function keeps its name, docstring and signature metadata.\n\n"
        "Decorators are ideal for cross-cutting concerns: authentication, logging, caching, timing and "
        "validation. Decorators that take arguments need three nested functions (decorator factory -> "
        "decorator -> wrapper). Keep the wrapper transparent: pass `*args, **kwargs` through and return "
        "the original result.",
        [
            {"code": "from functools import wraps\n\ndef logged(fn):\n    @wraps(fn)\n    def wrapper(*args, **kwargs):\n        print('calling', fn.__name__)\n        return fn(*args, **kwargs)\n    return wrapper\n\n@logged\ndef greet(name):\n    return f'Hi {name}'",
             "explanation": "wraps preserves greet's metadata while the wrapper adds logging."},
            {"code": "from functools import lru_cache\n\n@lru_cache(maxsize=128)\ndef fib(n):\n    return n if n < 2 else fib(n - 1) + fib(n - 2)",
             "explanation": "A library decorator caches results and turns exponential work into linear work."},
        ],
        [
            "Forgetting `wraps`, which breaks introspection and some frameworks.",
            "Writing a wrapper that forgets to `return fn(...)`.",
            "Applying a decorator that only works with zero-argument functions to a function with arguments.",
        ],
        "Flask routes, pytest fixtures and Click commands are decorators. Understanding them lets you "
        "read and write framework code confidently.",
        ex("retry-decorator", "Write a decorator `double_result` that wraps a function and returns twice its result.",
           "from functools import wraps\n\ndef double_result(fn):\n    pass\n",
           [{"name": "Doubles result", "assertion": "@solution.double_result\ndef f(x):\n    return x + 1\nassert f(3) == 8"},
            {"name": "Preserves name", "assertion": "@solution.double_result\ndef named():\n    return 1\nassert named.__name__ == 'named'"}]),
    ),
    T(
        "context-managers", "Context Managers", 3, "Advanced Python",
        "Reliable setup and cleanup using `with` and the context manager protocol.",
        "A context manager implements `__enter__` (returns the resource) and `__exit__` (cleans up, and "
        "can suppress an exception by returning True). The `with` statement guarantees cleanup even if "
        "the body raises. Files, locks and database connections are common context managers.\n\n"
        "For simple cases use `contextlib.contextmanager` and a generator with one `yield`: code before "
        "the yield is setup, code after it is teardown. `contextlib.suppress(ExceptionType)` is a precise "
        "alternative to a bare try/except/pass.",
        [
            {"code": "from contextlib import contextmanager\n\n@contextmanager\ndef timer():\n    start = 0\n    try:\n        yield start\n    finally:\n        print('cleanup runs even on error')",
             "explanation": "The finally block guarantees teardown when the with-body exits."},
            {"code": "from contextlib import suppress\n\nwith suppress(FileNotFoundError):\n    open('missing.txt')",
             "explanation": "Only the named exception is ignored; others still propagate."},
        ],
        [
            "Forgetting `yield` in a @contextmanager generator.",
            "Believing `__exit__` runs only on success — it runs on exceptions too.",
            "Returning a value from `__exit__` expecting it to become the with-statement result.",
        ],
        "Resource leaks are a common source of production outages. Context managers make correct cleanup "
        "the default.",
        ex("context-class", "Define a class `Timer` usable as `with Timer() as t:` where `t` is the Timer instance and exiting sets `t.finished = True`.",
           "class Timer:\n    pass\n",
           [{"name": "Context protocol", "assertion": "with solution.Timer() as t:\n    assert t.finished is False\nassert t.finished is True"},
            {"name": "Cleanup on error", "assertion": "try:\n    with solution.Timer() as t:\n        raise ValueError('x')\nexcept ValueError:\n    pass\nassert t.finished is True"}]),
    ),
    T(
        "advanced-oop", "Advanced OOP", 3, "OOP",
        "Dunder methods, abstract base classes, properties and composition patterns.",
        "Special ('dunder') methods make your objects work with Python syntax: `__repr__` for developer "
        "output, `__str__` for user output, `__eq__` for equality, `__len__`, `__getitem__`, `__iter__` "
        "and arithmetic methods such as `__add__`. Implement them consistently with the language's "
        "expectations.\n\n"
        "An `abc.ABC` with `@abstractmethod` defines an interface that subclasses must implement. "
        "Composition — storing collaborator objects instead of inheriting from them — keeps classes "
        "smaller and easier to change. SOLID principles, especially single responsibility and dependency "
        "inversion, guide larger class designs.",
        [
            {"code": "class Money:\n    def __init__(self, amount):\n        self.amount = amount\n    def __add__(self, other):\n        return Money(self.amount + other.amount)\n    def __repr__(self):\n        return f'Money({self.amount})'",
             "explanation": "Dunder methods let Money participate in `+` and repr() like a built-in type."},
            {"code": "from abc import ABC, abstractmethod\n\nclass Storage(ABC):\n    @abstractmethod\n    def save(self, data):\n        ...\n",
             "explanation": "Subclasses must provide save(); Storage itself cannot be instantiated."},
        ],
        [
            "Implementing `__eq__` without also thinking about hashability.",
            "Using inheritance to share behaviour between unrelated classes.",
            "Making a god class that owns every responsibility in the application.",
        ],
        "Large codebases stay maintainable when classes have narrow responsibilities and explicit "
        "interfaces. These patterns are what 'professional Python' looks like in practice.",
        ex("money-class", "Define a `Money` class with `amount`, `__add__` that adds amounts and returns a new Money, and `__eq__` comparing amounts.",
           "class Money:\n    pass\n",
           [{"name": "Addition", "assertion": "assert (solution.Money(3) + solution.Money(4)).amount == 7"},
            {"name": "Equality", "assertion": "assert solution.Money(2) == solution.Money(2)\nassert solution.Money(2) != solution.Money(3)"}]),
    ),
    T(
        "database-integration", "Database Integration", 3, "Data",
        "Using SQL safely from Python with sqlite3 and PostgreSQL drivers.",
        "`sqlite3.connect(path)` gives you a connection; use a cursor to execute SQL and always pass "
        "parameters as a tuple (`cursor.execute('... WHERE id = ?', (id,))`). String formatting SQL with "
        "user input creates SQL injection vulnerabilities. Commit writes, and use `with connection:` or "
        "try/finally to close resources.\n\n"
        "For PostgreSQL use a driver such as `psycopg` with a connection string from an environment "
        "variable. Connection pooling (built into SQLAlchemy or Neon's pooled endpoint) avoids opening a "
        "new TCP connection per request. Transactions group related writes so a failure leaves no partial "
        "state.",
        [
            {"code": "import sqlite3\nconn = sqlite3.connect(':memory:')\nconn.execute('CREATE TABLE users (name TEXT)')\nconn.execute('INSERT INTO users VALUES (?)', ('Ada',))\nprint(conn.execute('SELECT name FROM users').fetchall())",
             "explanation": "The placeholder prevents injection and handles quoting correctly."},
            {"code": "import os, psycopg\nconn = psycopg.connect(os.environ['DATABASE_URL'])\nwith conn.transaction():\n    conn.execute('INSERT INTO events (kind) VALUES (%s)', ('login',))",
             "explanation": "Credentials come from the environment and the transaction commits atomically."},
        ],
        [
            "Building SQL strings with f-strings containing user input.",
            "Forgetting to commit or close a connection.",
            "Using a direct (non-pooled) Neon connection for every web request.",
        ],
        "Nearly every useful application persists data. Safe database access is a non-negotiable "
        "professional skill.",
        ex("insert-and-list", "Given `conn` (an sqlite3 connection) with a table `users (name TEXT)`, write `insert_user(conn, name)` and `list_users(conn)` returning a list of names.",
           "def insert_user(conn, name):\n    pass\n\ndef list_users(conn):\n    pass\n",
           [{"name": "Insert and list", "assertion": "import sqlite3\nc = sqlite3.connect(':memory:')\nc.execute('CREATE TABLE users (name TEXT)')\nsolution.insert_user(c, 'Ada')\nassert solution.list_users(c) == ['Ada']"},
            {"name": "Parameterised", "assertion": "import sqlite3\nc = sqlite3.connect(':memory:')\nc.execute('CREATE TABLE users (name TEXT)')\nsolution.insert_user(c, \"O'Brien\")\nassert solution.list_users(c) == [\"O'Brien\"]"}]),
    ),
    T(
        "flask-and-rest-apis", "Flask and REST APIs", 3, "Web Development",
        "Building HTTP endpoints with Flask, JSON payloads and proper status codes.",
        "A Flask app registers routes that map URL patterns and HTTP methods to view functions. Return a "
        "dict (Flask 2+) or `jsonify(...)` for JSON responses, and use `request.get_json()` to read a "
        "JSON body. Status codes communicate the result: 200 for success, 201 for creation, 400 for bad "
        "input, 401/403 for authentication problems, 404 for missing resources.\n\n"
        "Keep business logic out of views: validate input, call a service function, then shape the "
        "response. Use blueprints to split large apps into modules. Test with `app.test_client()` instead "
        "of running a live server.",
        [
            {"code": "from flask import Flask, jsonify, request\napp = Flask(__name__)\n\n@app.get('/health')\ndef health():\n    return jsonify(status='ok')\n\n@app.post('/echo')\ndef echo():\n    return jsonify(request.get_json() or {})",
             "explanation": "Route decorators register views; jsonify produces a JSON response."},
            {"code": "with app.test_client() as client:\n    response = client.get('/health')\n    assert response.status_code == 200\n    assert response.json == {'status': 'ok'}",
             "explanation": "The test client exercises the app without opening a socket."},
        ],
        [
            "Returning a Python string from an API endpoint when the client expects JSON.",
            "Trusting request JSON without validating required fields.",
            "Using GET requests to change server state.",
        ],
        "This academy's own backend is a Flask REST API. Building one yourself makes the architecture "
        "transparent rather than mysterious.",
        ex("health-route", "Write `create_app()` returning a Flask app with `GET /status` that returns JSON {'ok': True} and status 200.",
           "from flask import Flask, jsonify\n\ndef create_app():\n    app = Flask(__name__)\n    # register your route here\n    return app\n",
           [{"name": "Status endpoint", "assertion": "client = solution.create_app().test_client()\nr = client.get('/status')\nassert r.status_code == 200 and r.json == {'ok': True}"}]),
    ),
    T(
        "testing-with-pytest", "Testing with pytest", 3, "Quality",
        "Writing focused tests with fixtures, parameterisation and mocking.",
        "pytest discovers functions named `test_*`. Use plain `assert` statements; failures show the "
        "intermediate values automatically. Fixtures (`@pytest.fixture`) provide setup and teardown, and "
        "can be scoped to a function, module or session. `@pytest.mark.parametrize` runs the same test "
        "against many inputs.\n\n"
        "Test behaviour, not implementation: call the public function and check the result or side "
        "effect. Use `monkeypatch` to replace slow or non-deterministic dependencies (time, network). "
        "Aim for a fast test suite you actually run — speed is a feature.",
        [
            {"code": "import pytest\n\n@pytest.mark.parametrize('a,b,expected', [(1, 2, 3), (0, 0, 0)])\ndef test_add(a, b, expected):\n    assert add(a, b) == expected",
             "explanation": "One test function covers several representative cases."},
            {"code": "@pytest.fixture\ndef client():\n    app = create_app()\n    app.config['TESTING'] = True\n    return app.test_client()",
             "explanation": "The fixture centralises app setup for every endpoint test."},
        ],
        [
            "Testing private helpers instead of observable behaviour.",
            "Asserting only that 'no exception was raised' without checking the result.",
            "Writing tests that depend on the current date or live network responses.",
        ],
        "Automated tests are how you prove a project works — including here. Every project in this "
        "academy is graded by behavioural tests, just like production code.",
        ex("test-friendly", "Write `normalise(text)` that strips whitespace and lowercases text, so that tests like `normalise('  Ada ' ) == 'ada'` pass.",
           "def normalise(text):\n    pass\n",
           calls("normalise", [("  Ada ", "ada"), ("PYTHON", "python"), ("", "")])),
    ),
    T(
        "async-and-concurrency", "Async and Concurrency", 3, "Performance",
        "Choosing between threads, processes and asyncio for concurrent work.",
        "Threads share memory and are useful for I/O-bound work (network, disk) because they can wait "
        "together. The GIL means CPU-bound Python threads do not run in parallel; use `multiprocessing` "
        "or `concurrent.futures.ProcessPoolExecutor` for CPU-heavy tasks. `asyncio` uses an event loop and "
        "`async`/`await` to handle many I/O operations with few threads.\n\n"
        "Shared mutable state needs locks (`threading.Lock`) or queues. Deadlocks arise when two tasks "
        "wait on each other's locks; keep lock scopes small and consistent. Never block the event loop "
        "with a long CPU computation — offload it with `asyncio.to_thread()`.",
        [
            {"code": "from concurrent.futures import ThreadPoolExecutor\nimport requests\n\nwith ThreadPoolExecutor(max_workers=5) as pool:\n    results = list(pool.map(lambda u: requests.get(u, timeout=5).status_code, urls))",
             "explanation": "Independent network calls overlap, cutting total wall-clock time."},
            {"code": "import asyncio\n\nasync def main():\n    await asyncio.sleep(0.1)\n    return 'done'\n\nprint(asyncio.run(main()))",
             "explanation": "asyncio.run starts the event loop and waits for the coroutine."},
        ],
        [
            "Using threads to speed up pure-Python CPU loops.",
            "Forgetting to await a coroutine, which creates a coroutine object but does not run it.",
            "Sharing a list between threads without a lock for compound operations.",
        ],
        "Responsive APIs and fast data pipelines need concurrency. Picking the right model avoids both "
        "slow code and subtle races.",
        ex("parallel-safe-count", "Write `count_words(texts)` returning a dict of word counts. Use whatever approach you like; it must handle an empty list.",
           "def count_words(texts):\n    pass\n",
           calls("count_words", [(["a b", "a c"], {"a": 2, "b": 1, "c": 1}), ([], {}), (["hi hi"], {"hi": 2})])),
    ),
    T(
        "logging-and-performance", "Logging and Performance", 3, "Operations",
        "Instrumenting applications and finding bottlenecks before users do.",
        "Use the `logging` module rather than print: levels (DEBUG, INFO, WARNING, ERROR, CRITICAL), "
        "handlers and formatters let you control output per environment. Configure it once at the "
        "application entry point, and include context (`logger.info('login %s', username)`) instead of "
        "f-strings so formatting is lazy.\n\n"
        "Profile before optimising: `cProfile` shows which functions consume time, and `timeit` measures "
        "small expressions. Common wins come from choosing the right data structure, avoiding repeated "
        "work in loops, streaming large inputs and caching expensive pure computations. Measure again "
        "after each change.",
        [
            {"code": "import logging\nlogger = logging.getLogger(__name__)\nlogger.info('Processing %d records', len(records))\nlogger.error('Failed to save %s', path, exc_info=True)",
             "explanation": "Lazy formatting and exc_info keep logs informative without building strings unnecessarily."},
            {"code": "import cProfile, pstats\nprofiler = cProfile.Profile()\nprofiler.enable()\ndo_work()\nprofiler.disable()\npstats.Stats(profiler).sort_stats('cumtime').print_stats(10)",
             "explanation": "cProfile reveals the ten most time-consuming call paths."},
        ],
        [
            "Logging sensitive data such as passwords or tokens.",
            "Optimising code you have never profiled.",
            "Catching an exception and logging it without `exc_info`, losing the traceback.",
        ],
        "When something breaks at 2 a.m., logs and metrics are your only witnesses. Building them in "
        "early is much cheaper than adding them later.",
        ex("log-message", "Write `format_log(level, message)` returning 'LEVEL: message' with the level uppercased.",
           "def format_log(level, message):\n    pass\n",
           calls("format_log", [(("info", "started"), "INFO: started"), (("error", "boom"), "ERROR: boom")])),
    ),
]
