"""Level 4 projects — production-shaped systems and professional practices."""

from .helpers import A, P, calls

PROJECTS = [
    P(
        "full-stack-web-application", "Full-Stack Web Application", 4,
        "Serve a real page and a JSON API from one layered Flask application.",
        "Professional web applications have both a human interface and a machine interface. In this "
        "project a single Flask app serves an HTML form and a JSON API over the same in-memory store. "
        "Keep the store in a separate class so the HTTP layer stays thin — that separation is what lets "
        "a team replace the UI without rewriting business rules.",
        ["Serve HTML and JSON from one app", "Keep a distinct service layer", "Validate at every boundary",
         "Test pages and endpoints separately"],
        ["Flask", "Layered architecture", "HTML forms", "REST"],
        [
            "Build the store", "Create an `ItemStore` class with `add(name)` and `all()` methods. Names are stripped; blank names raise `ValueError`. Ids start at 1.",
            "Create the app factory", "`build_app()` returns a Flask app with the store attached as `app.config['STORE']`.",
            "Serve the interface", "`GET /` returns an HTML page containing a `<form>` with method `post` and an input named `name`.",
            "Serve the API", "`GET /api/items` returns `{'items': [...]}`; `POST /api/items` accepts JSON, returns 201 with the item or 400 with `{'error': 'name required'}`.",
            "Test both surfaces", "Use the test client to assert the page contains a form and the API behaves correctly.",
        ],
        [
            "`build_app()` returns a Flask application with `GET /`, `GET /api/items` and `POST /api/items`.",
            "The HTML page contains `<form` and `name=\"name\"`.",
            "The API returns 201 for valid names and 400 for invalid ones; ids start at 1.",
        ],
        [
            A("Page is served", "client = solution.build_app().test_client()\nr = client.get('/')\nassert r.status_code == 200\nassert '<form' in r.text and 'name=\"name\"' in r.text"),
            A("List is empty", "client = solution.build_app().test_client()\nassert client.get('/api/items').json == {'items': []}"),
            A("Create via API", "client = solution.build_app().test_client()\nr = client.post('/api/items', json={'name': '  Lamp  '})\nassert r.status_code == 201 and r.json == {'id': 1, 'name': 'Lamp'}\nassert client.get('/api/items').json['items'][0]['name'] == 'Lamp'"),
            A("Invalid name", "client = solution.build_app().test_client()\nr = client.post('/api/items', json={'name': ' '})\nassert r.status_code == 400 and r.json == {'error': 'name required'}"),
        ],
        "from flask import Flask, jsonify, request\n\nclass ItemStore:\n    pass\n\n\ndef build_app():\n    app = Flask(__name__)\n    return app\n",
        "You separated persistence from HTTP, served both HTML and JSON, and validated input on the API "
        "boundary — the foundation of a maintainable full-stack app.", 180,
    ),
    P(
        "inventory-management-system", "Inventory Management System", 4,
        "Track stock, sales and valuation with domain rules in one class.",
        "Inventory systems fail when rules leak into the UI: a negative stock level or a sale below cost "
        "is a business error, not a formatting issue. This project asks you to enforce those rules in a "
        "domain class and expose read-only reports. Think about atomicity: a successful sale must change "
        "both stock and revenue information together.",
        ["Model domain rules in a class", "Maintain consistent state", "Report derived values",
         "Handle insufficient stock"],
        ["Domain modelling", "Validation", "Dictionaries", "Rounding"],
        [
            "Define the store", "`Inventory()` starts empty. `add_sku(sku, quantity, price)` adds or increases stock and returns the new quantity. Price must be positive.",
            "Sell items", "`sell(sku, quantity)` reduces stock and returns the sale value (quantity * price, rounded to 2 decimals). Unknown SKUs or insufficient stock raise `ValueError` and change nothing.",
            "Report stock", "`stock(sku)` returns the quantity or 0. `low_stock(threshold=5)` returns a sorted list of SKUs at or below the threshold.",
            "Report value", "`value()` returns the total value of remaining stock rounded to two decimals.",
        ],
        [
            "Invalid operations never partially change state.",
            "SKUs are compared case-insensitively and returned in uppercase.",
            "All monetary values are rounded to two decimals.",
        ],
        [
            A("Add and stock", "inv = solution.Inventory()\nassert inv.add_sku('abc', 10, 2.5) == 10\nassert inv.add_sku('ABC', 5, 2.5) == 15\nassert inv.stock('abc') == 15"),
            A("Sell", "inv = solution.Inventory()\ninv.add_sku('abc', 10, 2.5)\nassert inv.sell('ABC', 4) == 10.0\nassert inv.stock('abc') == 6"),
            A("Insufficient stock", "inv = solution.Inventory()\ninv.add_sku('abc', 2, 5)\ntry:\n    inv.sell('abc', 3)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('expected ValueError')\nassert inv.stock('abc') == 2"),
            A("Low stock and value", "inv = solution.Inventory()\ninv.add_sku('b', 4, 1.5); inv.add_sku('a', 20, 2)\nassert inv.low_stock(5) == ['B']\nassert inv.value() == 46.0"),
            A("Invalid price", "inv = solution.Inventory()\ntry:\n    inv.add_sku('x', 1, 0)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('expected ValueError')"),
        ],
        "class Inventory:\n    pass\n",
        "You enforced business invariants in one place, kept operations atomic, and produced reliable "
        "derived reports — the essence of domain-driven design.", 150,
    ),
    P(
        "web-analytics-dashboard", "Web Analytics Dashboard", 4,
        "Turn raw event streams into the numbers a dashboard would display.",
        "Dashboards are only as trustworthy as their aggregation layer. You will compute headline metrics "
        "and a moving average from event data, with explicit rules for empty inputs and window sizes. "
        "Keep the calculations pure so you can unit test them and reuse them behind any UI.",
        ["Aggregate event data", "Compute rolling statistics", "Handle edge cases explicitly",
         "Write pure reporting functions"],
        ["Aggregation", "Statistics", "Pure functions", "Data visualisation prep"],
        [
            "Summarise events", "`summarise(events)` accepts dicts with `user` and `value` keys and returns `{'events': int, 'users': int, 'total': float}` with total rounded to two decimals. Missing values count as 0.",
            "Moving average", "`moving_average(values, window)` returns a list of averages for each position, each rounded to two decimals. The first positions use the values available so far.",
            "Validate the window", "A window smaller than 1 raises `ValueError`; an empty values list returns an empty list.",
            "Prepare chart data", "`daily_totals(events)` returns a dict of `date -> total` from events with a `date` string key.",
        ],
        [
            "No function mutates its input.",
            "Averages are rounded to two decimals and never divide by zero.",
            "`daily_totals` ignores events without a date.",
        ],
        [
            A("Summary", "events = [{'user': 'a', 'value': 10}, {'user': 'a', 'value': 5}, {'user': 'b', 'value': 2.5}]\nassert solution.summarise(events) == {'events': 3, 'users': 2, 'total': 17.5}"),
            A("Empty summary", "assert solution.summarise([]) == {'events': 0, 'users': 0, 'total': 0.0}"),
            A("Moving average", "assert solution.moving_average([1, 2, 3, 4], 2) == [1.0, 1.5, 2.5, 3.5]\nassert solution.moving_average([], 3) == []"),
            A("Invalid window", "try:\n    solution.moving_average([1], 0)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('expected ValueError')"),
            A("Daily totals", "events = [{'date': '2026-01-01', 'value': 2}, {'date': '2026-01-01', 'value': 3}, {'value': 99}]\nassert solution.daily_totals(events) == {'2026-01-01': 5}"),
        ],
        "def summarise(events):\n    pass\n\n\ndef moving_average(values, window):\n    pass\n\n\ndef daily_totals(events):\n    pass\n",
        "You produced trustworthy aggregates from imperfect data, handled edge cases, and prepared data "
        "that a real chart component could consume.", 150,
    ),
    P(
        "business-automation-tool", "Automated Business Management Tool", 4,
        "Apply business rules to orders and produce a reliable report.",
        "Automation code is Where business policy becomes executable. The danger is hiding rules in "
        "scattered conditionals. Here you will centralise discount and cancellation rules, compute a "
        "report, and test the boundary cases that cost companies money: empty orders, cancelled orders "
        "and thresholds.",
        ["Encode business rules explicitly", "Aggregate monetary values", "Handle thresholds and empty data",
         "Return structured reports"],
        ["Business rules", "Aggregation", "Decimal rounding", "Reporting"],
        [
            "Understand the rules", "Each order has `customer`, `status` and `items` (a list of `{'price': number, 'qty': int}`). Only `status == 'paid'` orders count toward revenue.",
            "Apply a discount", "Paid orders with a subtotal over 100 receive a 10% discount. Round the final revenue for each order to two decimals.",
            "Produce a report", "`process_orders(orders)` returns `{'orders': int, 'revenue': float, 'discounted': int, 'by_customer': dict}` where `orders` counts paid orders.",
            "Explain decisions", "Include a docstring listing the rules. If a colleague changes a rule, the test failures should point at the right place.",
        ],
        [
            "Cancelled or pending orders contribute nothing to revenue or counts.",
            "Discount applies once per order when subtotal > 100.",
            "All monetary values are rounded to two decimals.",
        ],
        [
            A("Single paid order", "orders = [{'customer': 'Ada', 'status': 'paid', 'items': [{'price': 10, 'qty': 2}]}]\nr = solution.process_orders(orders)\nassert r == {'orders': 1, 'revenue': 20.0, 'discounted': 0, 'by_customer': {'Ada': 20.0}}"),
            A("Discount rule", "orders = [{'customer': 'Ada', 'status': 'paid', 'items': [{'price': 60, 'qty': 2}]}]\nr = solution.process_orders(orders)\nassert r['revenue'] == 108.0 and r['discounted'] == 1"),
            A("Ignore non-paid", "orders = [{'customer': 'Ada', 'status': 'cancelled', 'items': [{'price': 60, 'qty': 2}]}, {'customer': 'Grace', 'status': 'pending', 'items': [{'price': 5, 'qty': 1}]}]\nassert solution.process_orders(orders) == {'orders': 0, 'revenue': 0.0, 'discounted': 0, 'by_customer': {}}"),
            A("Several customers", "orders = [\n {'customer': 'Ada', 'status': 'paid', 'items': [{'price': 5, 'qty': 1}]},\n {'customer': 'Grace', 'status': 'paid', 'items': [{'price': 5, 'qty': 2}]},\n {'customer': 'Ada', 'status': 'paid', 'items': [{'price': 5, 'qty': 3}]},\n]\nr = solution.process_orders(orders)\nassert r['orders'] == 3 and r['revenue'] == 30.0\nassert r['by_customer'] == {'Ada': 20.0, 'Grace': 10.0}"),
            A("Empty input", "assert solution.process_orders([]) == {'orders': 0, 'revenue': 0.0, 'discounted': 0, 'by_customer': {}}"),
        ],
        "def process_orders(orders):\n    \"\"\"Rules: only paid orders count; subtotal > 100 gets a 10% discount.\"\"\"\n    pass\n",
        "You encoded business policy in one testable place and produced a structured report — the shape "
        "of most back-office automation work.", 150,
    ),
    P(
        "multi-user-application", "Multi-User Application with Permissions", 4,
        "Implement authentication data and role-based access control correctly.",
        "Multi-user systems must make access decisions in one trusted place. This project models users, "
        "password hashes and permissions without a web framework, so you can focus on the security "
        "logic. Never store plaintext passwords, never return them from an API, and deny by default when "
        "a role or permission is unknown.",
        ["Hash passwords with a slow KDF", "Model roles and permissions", "Deny by default",
         "Return safe copies of user data"],
        ["Authentication", "Authorization", "werkzeug.security", "Least privilege"],
        [
            "Create the store", "`UserStore()` starts empty. `add_user(name, email, password, role='viewer')` returns a public user dict without the password hash. Duplicate emails raise `ValueError`.",
            "Verify credentials", "`check_login(email, password)` returns the public user dict on success and None on failure. Use `werkzeug.security.generate_password_hash` and `check_password_hash`.",
            "Check permissions", "`can(email, permission)` returns True only when the user's role grants it: admin grants all, editor grants `read` and `write`, viewer grants `read`. Unknown users or permissions return False.",
            "List users safely", "`users()` returns copies without password hashes; mutating them must not change the store.",
        ],
        [
            "No method ever returns a password or password hash.",
            "Unknown roles and permissions are denied.",
            "Passwords are stored as hashes, not plaintext.",
        ],
        [
            A("Add and login", "store = solution.UserStore()\nu = store.add_user('Ada', 'ada@x.test', 'strong-pass', 'admin')\nassert 'password' not in u and 'password_hash' not in u\nassert store.check_login('ada@x.test', 'strong-pass')['name'] == 'Ada'\nassert store.check_login('ada@x.test', 'wrong') is None"),
            A("Stored as hash", "store = solution.UserStore()\nstore.add_user('Ada', 'ada@x.test', 'strong-pass')\nassert store.check_login('ada@x.test', 'strong-pass') is not None"),
            A("Permissions", "store = solution.UserStore()\nstore.add_user('Admin', 'a@x.test', 'p', 'admin')\nstore.add_user('Editor', 'e@x.test', 'p', 'editor')\nstore.add_user('Viewer', 'v@x.test', 'p', 'viewer')\nassert store.can('a@x.test', 'delete') is True\nassert store.can('e@x.test', 'write') is True\nassert store.can('e@x.test', 'delete') is False\nassert store.can('v@x.test', 'write') is False\nassert store.can('nobody@x.test', 'read') is False"),
            A("Duplicate and safe copies", "store = solution.UserStore()\nstore.add_user('Ada', 'ada@x.test', 'p')\ntry:\n    store.add_user('Other', 'ADA@x.test', 'p')\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('expected ValueError')\nstore.users()[0]['name'] = 'hacked'\nassert store.users()[0]['name'] == 'Ada'"),
        ],
        "from werkzeug.security import generate_password_hash, check_password_hash\n\nclass UserStore:\n    pass\n",
        "You implemented password hashing, role-based access control with deny-by-default, and safe user "
        "objects — the security core of any multi-user application.", 180,
    ),
]
