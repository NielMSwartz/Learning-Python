"""Level 4 — Professional development knowledge-library topics."""

from .helpers import T, calls, ex

TOPICS = [
    T(
        "clean-code", "Clean Code", 4, "Professional",
        "Names, functions and structure that make code easy to change.",
        "Code is read far more often than written. Choose names that reveal intent (`days_since_last_login`, "
        "not `d`), keep functions short and focused on one level of abstraction, and avoid surprising side "
        "effects. A good comment explains *why* something is done; code should explain *what*.\n\n"
        "Prefer early returns to deep nesting, keep related concepts close together, and treat duplication "
        "as a signal to look for the abstraction — but do not force one prematurely. Consistent formatting "
        "with Black and linting with Ruff remove argument about style from reviews.",
        [
            {"code": "# harder to read\nif user:\n    if user.active:\n        if user.has_license:\n            return True\nreturn False\n\n# clearer\nreturn bool(user and user.active and user.has_license)",
             "explanation": "Flattening the conditions exposes the single decision being made."},
            {"code": "def is_eligible(user, minimum_age=18):\n    \"\"\"Return True when the user meets the age and activity rules.\"\"\"\n    return user.active and user.age >= minimum_age",
             "explanation": "A descriptive name and docstring replace a comment that would go stale."},
        ],
        [
            "Adding comments to explain confusing code instead of making the code clear.",
            "Functions that both calculate results and write files and send email.",
            "Abbreviations that only make sense to the original author.",
        ],
        "Professional work is mostly changing existing code. Clean code lowers the cost of every future "
        "change.",
        ex("describe-order", "Write `describe_order(order)` returning 'Order <id>: <total> items' from a dict with 'id' and 'total'.",
           "def describe_order(order):\n    pass\n",
           calls("describe_order", [({"id": 7, "total": 3}, "Order 7: 3 items"), ({"id": "A", "total": 0}, "Order A: 0 items")])),
    ),
    T(
        "design-patterns", "Design Patterns", 4, "Professional",
        "Reusable solutions to recurring design problems — used thoughtfully.",
        "Patterns are vocabulary, not recipes to force everywhere. Strategy replaces conditionals with "
        "interchangeable algorithms; Factory centralises object creation; Observer lets subjects notify "
        "subscribers; Repository separates data access from business logic; Dependency Injection passes "
        "collaborators in rather than constructing them internally.\n\n"
        "Each pattern solves a specific tension. Start with the simplest code that works and introduce a "
        "pattern when the pain is real — for example, when adding a third payment provider means editing "
        "a growing `if/elif` chain.",
        [
            {"code": "class EmailNotifier:\n    def send(self, message):\n        return f'email: {message}'\n\nclass NotificationService:\n    def __init__(self, notifier):\n        self.notifier = notifier  # strategy injected\n    def notify(self, message):\n        return self.notifier.send(message)",
             "explanation": "The notifier can be swapped without touching NotificationService."},
            {"code": "ADAPTERS = {'json': lambda data: str(data), 'csv': lambda data: ','.join(data)}\n\ndef render(kind, data):\n    return ADAPTERS[kind](data)",
             "explanation": "A registry acts as a lightweight strategy selector."},
        ],
        [
            "Applying every pattern you know to a small script.",
            "Creating abstract factories for objects that will never have alternatives.",
            "Confusing a pattern with a framework feature and fighting the framework.",
        ],
        "Patterns help you discuss architecture precisely and recognise when a design is becoming hard "
        "to extend.",
        ex("strategy-total", "Write `total_with_strategy(prices, strategy)` where strategy is a callable applied to the sum. Example: `lambda x: round(x)`.",
           "def total_with_strategy(prices, strategy):\n    pass\n",
           calls("total_with_strategy", [(([1.2, 2.3], round), 3), (([1, 2], abs), 3), (([], sum), 0)])),
    ),
    T(
        "software-architecture", "Software Architecture", 4, "Professional",
        "Structuring an application into layers with clear boundaries and dependencies.",
        "Architecture is the set of decisions that are expensive to change later. A common web layout is "
        "routes (HTTP) -> services (use cases) -> repositories (persistence) -> database. Dependencies "
        "point inward: services should not import Flask request objects, so they can be tested without a "
        "web server.\n\n"
        "Separate configuration from code, keep domain rules independent of frameworks, and define "
        "stable interfaces between components. Document the important decisions with short ADRs "
        "(Architecture Decision Records): context, decision, consequences.",
        [
            {"code": "# routes.py\n@app.post('/items')\ndef create_item():\n    data = request.get_json()\n    item = service.add_item(data['name'])\n    return jsonify(item.to_dict()), 201",
             "explanation": "The route handles HTTP; the service owns the rule for adding an item."},
            {"code": "# services.py\ndef add_item(name, repository):\n    if not name.strip():\n        raise ValueError('name required')\n    return repository.save({'name': name})",
             "explanation": "Business logic has no HTTP dependencies and is easy to unit test."},
        ],
        [
            "Putting SQL queries directly into templates or route handlers of a large app.",
            "Designing the database schema before understanding the domain rules.",
            "Letting every module import every other module.",
        ],
        "Good architecture lets you replace a database, add a mobile client or change a UI without "
        "rewriting the whole system.",
        ex("service-layer", "Write `register_user(name, repository)` that strips the name, rejects blanks with ValueError, and returns repository.save({'name': clean}).",
           "def register_user(name, repository):\n    pass\n",
           [{"name": "Saves stripped name", "assertion": "saved = []\nsolution.register_user('  Ada  ', lambda d: saved.append(d) or d)\nassert saved == [{'name': 'Ada'}]"},
            {"name": "Rejects blank", "assertion": "try:\n    solution.register_user('   ', lambda d: d)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('expected ValueError')"}]),
    ),
    T(
        "git-and-github", "Git and GitHub", 4, "Professional",
        "Version control workflows that keep changes reviewable and recoverable.",
        "Git records snapshots (commits) of your work. The everyday loop is `git status`, `git add`, "
        "`git commit -m '...'`, `git push`. Branches isolate work; `git switch -c feature/x` creates one, "
        "and a pull request is a request to merge it. Rebase or merge deliberately, and resolve conflicts "
        "by understanding both sides rather than discarding changes.\n\n"
        "Write commit messages in the imperative ('Add expense tracker tests'). Keep `.env`, secrets and "
        "generated files out of the repository with `.gitignore`. Tags mark release points; GitHub "
        "Actions can run tests on every push.",
        [
            {"code": "git switch -c feature/weather-app\ngit add app/weather.py tests/test_weather.py\ngit commit -m 'Add weather parsing with tests'\ngit push -u origin feature/weather-app",
             "explanation": "A focused branch and commit make review and rollback straightforward."},
            {"code": "git status --short\ngit diff --stat\ngit log --oneline -5",
             "explanation": "These three commands answer 'what changed?' most of the time."},
        ],
        [
            "Committing credentials 'temporarily'.",
            "Making huge commits that mix unrelated changes.",
            "Rewriting shared history without telling collaborators.",
        ],
        "Version control is the safety net for every other skill here. It makes experimentation cheap "
        "and collaboration possible.",
        ex("commit-message", "Write `is_good_commit_message(message)` returning True when it is at most 72 characters, non-empty, and starts with a capital letter.",
           "def is_good_commit_message(message):\n    pass\n",
           calls("is_good_commit_message", [("Add tests", True), ("add tests", False), ("", False), ("A" * 73, False)])),
    ),
    T(
        "debugging-and-security", "Debugging and Security", 4, "Professional",
        "Finding root causes systematically and writing code that resists attack.",
        "Debugging is a loop: reproduce, form a hypothesis, test it, repeat. Read the whole traceback, "
        "inspect values with a debugger (`breakpoint()` or `pdb`) or small prints, and reduce the input to "
        "the smallest failing case. Fix the cause, not the symptom, and add a regression test.\n\n"
        "Security starts with never trusting input. Validate types and lengths, use parameterised SQL, "
        "escape output, hash passwords with a slow KDF, keep secrets in the environment, apply least "
        "privilege, set timeouts on network calls and keep dependencies patched. Never execute untrusted "
        "code in your application process — this academy sends it to a locked-down sandbox.",
        [
            {"code": "def load_profile(user_id, db):\n    if not isinstance(user_id, int) or user_id < 1:\n        raise ValueError('invalid id')\n    return db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()",
             "explanation": "Validation plus a parameterised query closes two common holes."},
            {"code": "breakpoint()  # drop into pdb at this line, inspect with 'p variable', continue with 'c'",
             "explanation": "A debugger shows real state instead of guesses."},
        ],
        [
            "Catching an exception and returning a default without understanding why it happened.",
            "Building SQL, shell commands or HTML by raw string concatenation with user input.",
            "Running untrusted code with the same privileges and environment as the web server.",
        ],
        "Every feature you add is a potential bug or vulnerability. A systematic mindset protects both "
        "your data and your users.",
        ex("validate-port", "Write `valid_port(value)` returning True only when value is an int in range 1-65535.",
           "def valid_port(value):\n    pass\n",
           calls("valid_port", [(80, True), (0, False), (65536, False), ("80", False)])),
    ),
    T(
        "deployment-and-docker", "Deployment and Docker", 4, "Professional",
        "Packaging applications so they run the same way everywhere.",
        "A container image is a reproducible filesystem plus a command. A `Dockerfile` starts from a "
        "base image, installs dependencies, copies code and defines the entry point. Compose coordinates "
        "multiple containers (web, executor, database) with networks, volumes and environment "
        "variables. Images should run as a non-root user with a read-only filesystem where possible.\n\n"
        "Production uses a real WSGI server such as Gunicorn, a reverse proxy for TLS, health checks, "
        "structured logs, backups and a rollback plan. Twelve-factor apps keep configuration in the "
        "environment and treat processes as disposable.",
        [
            {"code": "FROM python:3.12-slim\nWORKDIR /app\nCOPY requirements.txt .\nRUN pip install --no-cache-dir -r requirements.txt\nCOPY . .\nRUN useradd -m appuser\nUSER appuser\nCMD [\"gunicorn\", \"-b\", \"0.0.0.0:8000\", \"wsgi:app\"]",
             "explanation": "Dependencies are cached in their own layer, and the final process is not root."},
            {"code": "docker compose up -d --build\ndocker compose logs -f web\ndocker compose exec web flask db upgrade",
             "explanation": "Build, observe and migrate are separate, repeatable operations."},
        ],
        [
            "Baking secrets into an image.",
            "Running the Flask development server in production.",
            "Assuming a container restart preserves SQLite data without a volume.",
        ],
        "Deployment is what turns code on your machine into a tool you can open from your phone. This "
        "academy ships with containers and a compose file you can study.",
        ex("env-config", "Write `database_url(env)` returning env['DATABASE_URL'] when present and non-empty, otherwise 'sqlite:///local.db'.",
           "def database_url(env):\n    pass\n",
           calls("database_url", [({"DATABASE_URL": "postgres://x"}, "postgres://x"), ({}, "sqlite:///local.db"), ({"DATABASE_URL": ""}, "sqlite:///local.db")])),
    ),
    T(
        "cicd", "CI/CD", 4, "Professional",
        "Automated checks and delivery pipelines that catch problems before users do.",
        "Continuous Integration runs tests, linters and type checks on every push. Continuous Delivery "
        "keeps a deployable artifact ready; Continuous Deployment automatically ships main branch "
        "changes. A typical GitHub Actions workflow checks out code, sets up Python, installs "
        "dependencies and runs `pytest`.\n\n"
        "Keep the pipeline fast (parallel jobs, cached dependencies), fail loudly on broken tests, and "
        "never store production credentials in a public repository — use encrypted secrets or OIDC. "
        "Migrations should be backward compatible so a rolling deploy never breaks the old app.",
        [
            {"code": "name: tests\non: [push, pull_request]\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n      - uses: actions/setup-python@v5\n        with: {python-version: '3.12'}\n      - run: pip install -r requirements.txt\n      - run: pytest -q",
             "explanation": "Every push now proves the code still passes the test suite."},
            {"code": "# expand-first migration: add nullable column, deploy code, then backfill and constrain\nALTER TABLE users ADD COLUMN display_name VARCHAR(80);",
             "explanation": "Expand-then-contract keeps old and new application versions compatible."},
        ],
        [
            "A pipeline that runs tests but nobody reads the failures.",
            "Skipping migrations because 'the ORM will handle it'.",
            "Deploying from a developer's laptop instead of a repeatable artifact.",
        ],
        "Automation removes the question 'did we remember to check?'. It is the foundation of reliable "
        "releases.",
        ex("pipeline-status", "Write `pipeline_ok(results)` where results is a list of booleans; return True only if all are True (and an empty list is OK).",
           "def pipeline_ok(results):\n    pass\n",
           calls("pipeline_ok", [([True, True], True), ([True, False], False), ([], True)])),
    ),
    T(
        "large-codebases", "Working with Larger Codebases", 4, "Professional",
        "Navigating, changing and testing code you did not write yesterday.",
        "Start with the entry point and follow imports outward. Use your editor's search, 'go to "
        "definition' and call hierarchy instead of reading files top to bottom. Look for tests as "
        "executable documentation, and run the smallest relevant test set before a change.\n\n"
        "Make changes in small, reversible commits. Add a test that fails before the fix, then make it "
        "pass. Watch for implicit contracts — ordering, mutation, global state and timing — because these "
        "are what break when code grows. Document decisions where the code alone cannot explain them.",
        [
            {"code": "# find the source of a route\nrg \"@app\\.(get|post)\" -n app/\n# find every use of a helper\nrg \"format_money\" -n .",
             "explanation": "Fast search replaces guessing where something lives."},
            {"code": "# before changing behaviour\npytest tests/test_invoices.py -q\ngit switch -c fix/rounding",
             "explanation": "Establish a baseline and isolate the change."},
        ],
        [
            "Reformatting unrelated code in the same commit as a bug fix.",
            "Assuming a function's name tells the whole story.",
            "Deleting code you do not understand because it looks unused.",
        ],
        "This academy itself is a modular codebase. Learning to navigate one is a skill that transfers "
        "to every professional Python job.",
        ex("locate-symbol", "Write `find_symbol(lines, name)` returning a list of 1-based line numbers containing `name` as a whole word (case-sensitive).",
           "import re\n\ndef find_symbol(lines, name):\n    pass\n",
           calls("find_symbol", [
               ((["def alpha():", "    alpha()", "alphabet = 1"], "alpha"), [1, 2]),
               (([], "x"), []),
           ])),
    ),
]
