"""Level 3 projects — web, databases, APIs, testing and data pipelines."""

from .helpers import A, P, calls

PROJECTS = [
    P(
        "flask-web-application", "Flask Web Application", 3,
        "Build a small HTTP application with routes, JSON responses and tests.",
        "This is your first web project. A Flask app is a collection of view functions registered as "
        "routes. You will create an app factory, expose a health check, greet a visitor and implement a "
        "tiny in-memory resource endpoint. The tests use Flask's test client, so you never need to open "
        "a browser to verify behaviour.",
        ["Use an application factory", "Register routes for GET and POST", "Return JSON with correct status codes",
         "Test views with the Flask test client"],
        ["Flask", "HTTP methods", "JSON APIs", "Test client"],
        [
            "Create the factory", "`create_app()` configures and returns a Flask application. Set `app.config['TESTING'] = True` inside the factory to keep errors visible.",
            "Add a health check", "`GET /health` returns JSON `{'status': 'ok'}` with status 200.",
            "Add a greeting", "`GET /greet/<name>` returns plain text `Hello, <name>!` with status 200.",
            "Create a resource", "`POST /items` reads JSON with a `name` field. A missing or blank name returns `{'error': 'name required'}` with status 400. A valid name returns the created item and status 201.",
            "Test everything", "Use `app.test_client()` to exercise each route. Keep state on the app object so tests are isolated.",
        ],
        [
            "`create_app()` returns a Flask application instance.",
            "`GET /health` is JSON `{'status': 'ok'}`; `GET /greet/Ada` returns `Hello, Ada!`.",
            "`POST /items` returns 201 with `{'id': int, 'name': str}` for valid input and 400 for blank/missing names.",
        ],
        [
            A("Health route", "client = solution.create_app().test_client()\nr = client.get('/health')\nassert r.status_code == 200 and r.json == {'status': 'ok'}"),
            A("Greeting route", "client = solution.create_app().test_client()\nr = client.get('/greet/Ada')\nassert r.status_code == 200 and r.text == 'Hello, Ada!'"),
            A("Create item", "client = solution.create_app().test_client()\nr = client.post('/items', json={'name': 'Notebook'})\nassert r.status_code == 201\nassert r.json['id'] == 1 and r.json['name'] == 'Notebook'"),
            A("Reject blank name", "client = solution.create_app().test_client()\nr = client.post('/items', json={'name': '   '})\nassert r.status_code == 400 and r.json == {'error': 'name required'}"),
        ],
        "from flask import Flask, jsonify, request\n\ndef create_app():\n    app = Flask(__name__)\n    # register routes here\n    return app\n",
        "You built an app factory, handled two HTTP methods with meaningful status codes, and verified "
        "routes using a test client.", 120,
    ),
    P(
        "database-management-system", "Database Management System", 3,
        "Persist and query users with safe SQL from Python.",
        "SQL is often the longest-lived part of a system, so learning to use it safely matters. With an "
        "in-memory SQLite connection you can experiment freely: create a table, insert with placeholders, "
        "and query results. Every query in this project must use parameters — a single f-string with user "
        "input would make the whole application vulnerable.",
        ["Create tables with SQL", "Use parameterised statements", "Fetch and shape results",
         "Handle duplicate data"],
        ["sqlite3", "SQL", "Parameters", "Transactions"],
        [
            "Create the schema", "`create_table(conn)` creates a `users` table with `id INTEGER PRIMARY KEY AUTOINCREMENT`, `name TEXT NOT NULL` and `email TEXT NOT NULL UNIQUE`.",
            "Insert safely", "`insert_user(conn, name, email)` inserts with placeholders and returns the new id. Duplicate emails raise `sqlite3.IntegrityError`.",
            "Query users", "`list_users(conn)` returns a list of `(name, email)` tuples ordered by name. `find_user(conn, email)` returns one tuple or None.",
            "Test isolation", "Use `sqlite3.connect(':memory:')` in every test so no data survives between cases.",
        ],
        [
            "All SQL uses `?` placeholders for values.",
            "`insert_user` returns an integer id and lets `sqlite3.IntegrityError` propagate for duplicates.",
            "`list_users` returns tuples ordered by name; `find_user` returns a tuple or None.",
        ],
        [
            A("Create and insert", "import sqlite3\nc = sqlite3.connect(':memory:')\nsolution.create_table(c)\nassert isinstance(solution.insert_user(c, 'Ada', 'ada@x.test'), int)\nassert solution.insert_user(c, 'Grace', 'grace@x.test') > 0"),
            A("Ordered listing", "import sqlite3\nc = sqlite3.connect(':memory:')\nsolution.create_table(c)\nsolution.insert_user(c, 'Zoe', 'z@x.test')\nsolution.insert_user(c, 'Ada', 'a@x.test')\nassert solution.list_users(c) == [('Ada', 'a@x.test'), ('Zoe', 'z@x.test')]"),
            A("Find user", "import sqlite3\nc = sqlite3.connect(':memory:')\nsolution.create_table(c)\nsolution.insert_user(c, 'Ada', 'ada@x.test')\nassert solution.find_user(c, 'ada@x.test') == ('Ada', 'ada@x.test')\nassert solution.find_user(c, 'nobody@x.test') is None"),
            A("Duplicate rejected", "import sqlite3, sqlite3 as db\nc = db.connect(':memory:')\nsolution.create_table(c)\nsolution.insert_user(c, 'Ada', 'ada@x.test')\ntry:\n    solution.insert_user(c, 'Other', 'ada@x.test')\nexcept db.IntegrityError:\n    pass\nelse:\n    raise AssertionError('expected IntegrityError')"),
            A("Injection safe", "import sqlite3\nc = sqlite3.connect(':memory:')\nsolution.create_table(c)\nsolution.insert_user(c, \"O'Brien\", 'ob@x.test')\nassert solution.find_user(c, 'ob@x.test')[0] == \"O'Brien\""),
        ],
        "import sqlite3\n\ndef create_table(conn):\n    pass\n\n\ndef insert_user(conn, name, email):\n    pass\n\n\ndef list_users(conn):\n    pass\n\n\ndef find_user(conn, email):\n    pass\n",
        "You wrote parameterised SQL, handled uniqueness constraints, and shaped query results into a "
        "clean interface — the core of safe database integration.", 120,
    ),
    P(
        "rest-api", "REST API", 3,
        "Design an in-memory API with predictable status codes and payloads.",
        "A REST API is a contract over HTTP: methods choose the operation, paths identify resources, and "
        "status codes describe the outcome. This project uses an in-memory store so you can focus on the "
        "contract itself. Think about idempotency (repeating a DELETE should not crash) and validation "
        "before state changes.",
        ["Model resources with paths and methods", "Return status codes and JSON bodies",
         "Validate before mutating", "Handle not-found cases"],
        ["REST", "HTTP semantics", "Dictionaries", "Validation"],
        [
            "Define the interface", "`handle_request(method, path, body=None)` returns `(status_code, payload)`.",
            "List and create", "`GET /items` returns `(200, {'items': [...]})`. `POST /items` requires a non-empty `name` in `body`, otherwise `(400, {'error': 'name required'})`. Valid posts return `(201, item)` where item is `{'id': int, 'name': str}`.",
            "Read and delete one", "`GET /items/<id>` returns the item or `(404, {'error': 'not found'})`. `DELETE /items/<id>` returns `(204, None)` on success and 404 when missing.",
            "Keep it deterministic", "Ids start at 1 and increase. State lives at module level so successive calls see earlier changes.",
        ],
        [
            "`handle_request` always returns a two-tuple of `(int, dict | None)`.",
            "Ids start at 1; invalid names never create items.",
            "Repeating a DELETE for the same id returns 404 rather than raising.",
        ],
        [
            A("Create and list", "status, item = solution.handle_request('POST', '/items', {'name': 'Pen'})\nassert status == 201 and item == {'id': 1, 'name': 'Pen'}\nstatus, data = solution.handle_request('GET', '/items')\nassert status == 200 and data['items'] == [{'id': 1, 'name': 'Pen'}]"),
            A("Validation", "status, payload = solution.handle_request('POST', '/items', {})\nassert status == 400 and payload == {'error': 'name required'}\nstatus, data = solution.handle_request('GET', '/items')\nassert data['items'] == []"),
            A("Read one and missing", "solution.handle_request('POST', '/items', {'name': 'Pen'})\nassert solution.handle_request('GET', '/items/1') == (200, {'id': 1, 'name': 'Pen'})\nassert solution.handle_request('GET', '/items/99') == (404, {'error': 'not found'})"),
            A("Delete is idempotent", "solution.handle_request('POST', '/items', {'name': 'Pen'})\nassert solution.handle_request('DELETE', '/items/1') == (204, None)\nassert solution.handle_request('DELETE', '/items/1') == (404, {'error': 'not found'})"),
        ],
        "def handle_request(method, path, body=None):\n    # return (status_code, payload)\n    pass\n",
        "You implemented a REST contract with validation, not-found handling and idempotent deletion — "
        "the same reasoning used by production APIs.", 120,
    ),
    P(
        "web-based-task-management", "Web-Based Task Management", 3,
        "Add filtering, assignment and statistics to a task store.",
        "Once a resource exists, the interesting work begins: filtering, ownership and reporting. This "
        "project extends a simple task list with assignment and completion metrics. Design the data shape "
        "first so every method returns consistent dictionaries, then write the operations around it.",
        ["Design a consistent record shape", "Filter by multiple criteria", "Compute derived statistics",
         "Protect state from mutation"],
        ["Classes", "Filtering", "Aggregation", "API design"],
        [
            "Define a task", "A task is `{'id': int, 'title': str, 'assignee': str, 'done': bool}`. Ids start at 1.",
            "Create tasks", "`TaskBoard()` starts empty. `add(title, assignee)` returns the created task dict; blank titles raise `ValueError`.",
            "Query tasks", "`list_all()` returns copies of all tasks in id order. `filter_by(assignee=None, done=None)` returns copies matching the supplied criteria (use `None` to mean 'any').",
            "Complete and report", "`complete(task_id)` marks a task done and returns it, or None if missing. `stats()` returns `{'total': int, 'done': int, 'pending': int}`.",
        ],
        [
            "Every returned task is a copy; mutating it must not change the board.",
            "`filter_by` treats `done=False` differently from `done=None`.",
            "`complete` returns None for unknown ids and does not change other tasks.",
        ],
        [
            A("Add and list", "b = solution.TaskBoard()\nt = b.add('Write docs', 'Ada')\nassert t == {'id': 1, 'title': 'Write docs', 'assignee': 'Ada', 'done': False}\nassert b.list_all() == [t]"),
            A("Validation", "b = solution.TaskBoard()\ntry:\n    b.add('  ', 'Ada')\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('expected ValueError')\nassert b.list_all() == []"),
            A("Filtering", "b = solution.TaskBoard()\nb.add('a', 'Ada'); b.add('b', 'Grace'); b.complete(1)\nassert [t['title'] for t in b.filter_by(assignee='Ada')] == ['a']\nassert [t['title'] for t in b.filter_by(done=False)] == ['b']\nassert len(b.filter_by(assignee='Ada', done=True)) == 1"),
            A("Copies", "b = solution.TaskBoard()\nb.add('a', 'Ada')\nb.list_all()[0]['title'] = 'changed'\nassert b.list_all()[0]['title'] == 'a'"),
            A("Stats", "b = solution.TaskBoard()\nb.add('a', 'Ada'); b.add('b', 'Ada'); b.complete(1)\nassert b.stats() == {'total': 2, 'done': 1, 'pending': 1}"),
        ],
        "class TaskBoard:\n    pass\n",
        "You designed a stable record shape, implemented multi-criteria filtering and derived statistics, "
        "and kept internal state protected.", 120,
    ),
    P(
        "automated-data-processing", "Automated Data Processing Tool", 3,
        "Clean, validate and aggregate rows from a messy data source.",
        "Real data arrives with missing values, inconsistent casing and numeric strings. A processing "
        "pipeline separates cleaning from aggregation so each step can be tested. You will drop invalid "
        "rows deliberately, normalise categories and produce a summary that never surprises the caller.",
        ["Validate and clean records", "Convert strings to numbers safely", "Aggregate by category",
         "Compose small pure functions"],
        ["Data cleaning", "Dictionaries", "Exceptions", "Pipelines"],
        [
            "Understand the input", "Each row is a dict such as `{'amount': '12.50', 'category': 'Food'}`. Values may be blank, malformed or missing.",
            "Clean rows", "`clean_rows(rows)` returns a list of `{'amount': float, 'category': str}` dicts for valid rows. A valid amount is a positive number or numeric string; category must be non-empty after stripping. Categories are title-cased.",
            "Summarise", "`summarise(rows)` accepts raw rows, cleans them, and returns `{'count': int, 'total': float, 'by_category': dict}` with totals rounded to two decimals.",
            "Document decisions", "Add docstrings explaining why a row is dropped. Silent data loss is a debugging nightmare.",
        ],
        [
            "Invalid rows are dropped, not converted to zero.",
            "Categories in the output are title-cased (`'food'` -> `'Food'`).",
            "Totals are rounded to two decimal places and `by_category` contains only categories that occur.",
        ],
        [
            A("Clean valid rows", "rows = [{'amount': '12.5', 'category': ' food '}, {'amount': 3, 'category': 'travel'}]\nassert solution.clean_rows(rows) == [{'amount': 12.5, 'category': 'Food'}, {'amount': 3.0, 'category': 'Travel'}]"),
            A("Drop invalid", "rows = [{'amount': 'nope', 'category': 'food'}, {'category': 'food'}, {'amount': 5, 'category': '  '}, {'amount': -2, 'category': 'food'}]\nassert solution.clean_rows(rows) == []"),
            A("Summary", "rows = [{'amount': '10.00', 'category': 'food'}, {'amount': 5, 'category': 'food'}, {'amount': '2', 'category': 'travel'}]\ns = solution.summarise(rows)\nassert s['count'] == 3\nassert s['total'] == 17.0\nassert s['by_category'] == {'Food': 15.0, 'Travel': 2.0}"),
            A("Empty input", "assert solution.summarise([]) == {'count': 0, 'total': 0.0, 'by_category': {}}"),
        ],
        "def clean_rows(rows):\n    pass\n\n\ndef summarise(rows):\n    pass\n",
        "You built a two-stage data pipeline with explicit validation rules and deterministic rounding — "
        "the shape of most automated reporting tools.", 120,
    ),
]
