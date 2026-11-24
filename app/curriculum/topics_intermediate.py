"""Level 2 — Intermediate knowledge-library topics."""

from .helpers import T, calls, ex

TOPICS = [
    T(
        "object-oriented-programming", "Object-Oriented Programming", 2, "OOP",
        "Classes, objects, attributes and methods — modelling state and behaviour together.",
        "A class is a blueprint; an instance is one object built from it. `__init__` sets initial state, "
        "and methods are functions that receive `self`, the instance. Attributes store state; methods "
        "change or report that state. Keep invariants inside the class: if a balance may never be "
        "negative, enforce that in the method that changes it.\n\n"
        "Python does not enforce privacy, but a leading underscore signals 'internal use'. Properties "
        "(`@property`) let you expose a computed value or validate assignment without changing the "
        "calling syntax. Use `@dataclass` for classes that mainly carry data — it generates `__init__`, "
        "`__repr__` and equality for you.",
        [
            {"code": "class Counter:\n    def __init__(self, start=0):\n        self.value = start\n    def click(self):\n        self.value += 1\n\nc = Counter(4)\nc.click()\nprint(c.value)  # 5",
             "explanation": "`self` refers to the instance; click mutates that instance's state."},
            {"code": "from dataclasses import dataclass\n\n@dataclass\nclass Point:\n    x: float\n    y: float\n\nprint(Point(1, 2))  # Point(x=1, y=2)",
             "explanation": "dataclass removes boilerplate for simple value objects."},
        ],
        [
            "Forgetting `self` as the first parameter of an instance method.",
            "Storing mutable class attributes on the class itself, so all instances share them.",
            "Writing getters/setters for everything instead of using plain attributes and properties where needed.",
        ],
        "Projects with state — carts, trackers, contact books — are naturally modelled as objects. OOP "
        "keeps related data and rules in one place.",
        ex("counter-class", "Define a `Counter` class with `value` starting at 0 and a `click()` method that adds one and returns the new value.",
           "class Counter:\n    pass\n",
           [{"name": "Counter starts at zero", "assertion": "assert solution.Counter().value == 0"},
            {"name": "click returns and increments", "assertion": "c = solution.Counter()\nassert c.click() == 1\nassert c.click() == 2"}]),
    ),
    T(
        "inheritance-and-polymorphism", "Inheritance and Polymorphism", 2, "OOP",
        "Reusing behaviour through base classes and overriding it where needed.",
        "Inheritance lets a subclass reuse a parent's methods while adding or overriding behaviour. Call "
        "`super().__init__()` to initialise the parent part of the object. Polymorphism means code can "
        "work with a common interface without knowing the concrete class: a `list` of `Shape` objects can "
        "call `.area()` on each one.\n\n"
        "Favour composition ('has a') over inheritance ('is a') unless the relationship truly is a "
        "specialisation. Multiple inheritance is powerful but creates method-resolution complexity; "
        "understand Python's MRO before relying on it.",
        [
            {"code": "class Animal:\n    def speak(self):\n        return '...'\n\nclass Dog(Animal):\n    def speak(self):\n        return 'woof'\n\nprint(Dog().speak())  # woof",
             "explanation": "The subclass overrides the parent method; callers use the same interface."},
            {"code": "class Employee:\n    def __init__(self, name, rate):\n        self.name = name\n        self.rate = rate\n\nclass Contractor(Employee):\n    def __init__(self, name, rate, hours):\n        super().__init__(name, rate)\n        self.hours = hours",
             "explanation": "super() delegates shared initialisation to the base class."},
        ],
        [
            "Overriding a method without preserving the expected return type.",
            "Using inheritance just to share two lines of code where composition is clearer.",
            "Forgetting to call `super().__init__()` and losing parent state.",
        ],
        "Framework code — including Flask's view classes and pytest's fixtures — relies on inheritance "
        "and polymorphism. Understanding them makes frameworks predictable.",
        ex("shapes", "Define `Rectangle(w, h)` and `Triangle(w, h)` classes, both with an `area()` method returning the correct area.",
           "class Rectangle:\n    pass\n\nclass Triangle:\n    pass\n",
           [{"name": "Rectangle area", "assertion": "assert solution.Rectangle(3, 4).area() == 12"},
            {"name": "Triangle area", "assertion": "assert solution.Triangle(3, 4).area() == 6"}]),
    ),
    T(
        "modules-and-packages", "Modules and Packages", 2, "Code Organisation",
        "Splitting code into importable files with clear public interfaces.",
        "Any `.py` file is a module; a directory with `__init__.py` is a package (namespace packages "
        "without one also work). `import json` binds the module name; `from json import dumps` binds one "
        "attribute. Python caches imports in `sys.modules`, so module-level code runs once.\n\n"
        "A module's `__name__` is `'__main__'` when executed directly, which is why `if __name__ == "
        "'__main__':` guards scripts. Avoid circular imports by moving shared code deeper into the "
        "dependency graph or importing inside a function. Use `__all__` to define the public API of a "
        "package.",
        [
            {"code": "# maths_utils.py\ndef double(x):\n    return x * 2\n\n# app.py\nfrom maths_utils import double\nprint(double(21))  # 42",
             "explanation": "The import makes the function available in another module."},
            {"code": "if __name__ == '__main__':\n    print('runs only when this file is executed')",
             "explanation": "Importing the module does not execute the guarded block."},
        ],
        [
            "Naming a module the same as a standard-library module, e.g. `json.py`.",
            "Running a script from a directory that shadows an installed package.",
            "Circular imports between two modules that import each other at the top level.",
        ],
        "Real projects are too large for one file. Modules and packages let you grow code without losing "
        "your way.",
        ex("module-function", "In your submitted module, define `triple(x)` returning three times the input, and `SCALE = 3`.",
           "SCALE = 0\n\ndef triple(x):\n    pass\n",
           [{"name": "SCALE constant", "assertion": "assert solution.SCALE == 3"},
            {"name": "triple function", "assertion": "assert solution.triple(7) == 21"}]),
    ),
    T(
        "file-handling", "File Handling", 2, "Data",
        "Reading and writing files safely with the `with` statement and correct encodings.",
        "`open(path, mode, encoding='utf-8')` returns a file object. Modes include `'r'` (read), `'w'` "
        "(write, truncates), `'a'` (append) and `'x'` (create exclusively). Always use `with` so the file "
        "is closed even if an error occurs. Text mode translates newlines; binary mode (`'rb'`, `'wb'`) "
        "works with bytes.\n\n"
        "For large files, iterate line by line instead of calling `.read()` — streaming keeps memory "
        "usage flat. Use `pathlib.Path` for paths: `Path('data') / 'file.txt'` is portable and `read_text()` / "
        "`write_text()` cover simple cases. Handle `FileNotFoundError` and `PermissionError` explicitly.",
        [
            {"code": "from pathlib import Path\np = Path('notes.txt')\np.write_text('hello', encoding='utf-8')\nprint(p.read_text(encoding='utf-8'))",
             "explanation": "Path handles joining and common read/write operations."},
            {"code": "with open('log.txt', encoding='utf-8') as f:\n    for line in f:\n        if 'ERROR' in line:\n            print(line.strip())",
             "explanation": "Streaming line by line avoids loading the whole file into memory."},
        ],
        [
            "Using `'w'` when you meant to append — the existing file is erased.",
            "Relying on the platform default encoding instead of specifying UTF-8.",
            "Calling `.read()` on a huge log file and exhausting memory.",
        ],
        "Exports, imports, logs and configuration are all files. Safe file handling is required by "
        "almost every project from Level 2 upwards.",
        ex("count-lines", "Write `count_lines(text)` returning the number of non-empty lines after stripping whitespace.",
           "def count_lines(text):\n    pass\n",
           calls("count_lines", [("a\n\n b \n", 2), ("", 0), ("only\n", 1)])),
    ),
    T(
        "json-and-csv", "JSON and CSV", 2, "Data",
        "Serialising structured data and working with tabular files.",
        "`json.dumps(obj)` produces a JSON string and `json.loads(text)` parses one; `json.dump` / "
        "`json.load` work with file objects. JSON supports dicts, lists, strings, numbers, booleans and "
        "None — not arbitrary Python objects. Use `default=str` or convert objects explicitly.\n\n"
        "The `csv` module handles quoting and dialects correctly. Use `csv.DictReader` to get dictionaries "
        "keyed by header and `csv.DictWriter` with `writeheader()`. Never build CSV by joining strings with "
        "commas: values containing commas or newlines will break it.",
        [
            {"code": "import json\npayload = {'name': 'Ada', 'scores': [9, 8]}\ntext = json.dumps(payload)\nprint(json.loads(text)['scores'][0])  # 9",
             "explanation": "A round trip through JSON preserves the basic Python data types."},
            {"code": "import csv, io\ndata = csv.DictReader(io.StringIO('name,age\\nAda,36'))\nprint(list(data))  # [{'name': 'Ada', 'age': '36'}]",
             "explanation": "CSV values arrive as strings and must be converted when needed."},
        ],
        [
            "Assuming JSON preserves tuples as tuples — they become lists.",
            "Forgetting that csv.DictReader returns strings, not numbers.",
            "Passing a Python set directly to json.dumps().",
        ],
        "APIs speak JSON and spreadsheets speak CSV. These two formats move data between your programs "
        "and the rest of the world.",
        ex("json-summary", "Write `json_summary(payload)` that accepts a JSON string and returns a dict with 'count' (number of items) and 'names' (list of name values).",
           "import json\n\ndef json_summary(payload):\n    pass\n",
           calls("json_summary", [('[{"name": "Ada"}, {"name": "Grace"}]', {"count": 2, "names": ["Ada", "Grace"]}), ('[]', {"count": 0, "names": []})])),
    ),
    T(
        "comprehensions-and-lambdas", "Comprehensions and Lambdas", 2, "Pythonic Style",
        "Concise list/dict/set construction and small anonymous functions.",
        "A comprehension builds a collection from an iterable: `[expr for item in items if condition]`. "
        "Dict and set comprehensions use `{key: value for ...}` and `{expr for ...}`. They are often "
        "clearer than an empty list plus a loop, but nested comprehensions with several conditions can "
        "hurt readability — a normal loop is fine.\n\n"
        "A `lambda` is a small anonymous function: `lambda x: x * 2`. Lambdas are useful as arguments to "
        "`sorted(..., key=...)`, `map` and `filter`. If the expression grows complicated or needs a "
        "docstring, write a named function instead.",
        [
            {"code": "squares = [n * n for n in range(6) if n % 2 == 0]\nprint(squares)  # [0, 4, 16]",
             "explanation": "The optional `if` filters values before the expression is evaluated."},
            {"code": "names = ['Ada', 'Grace', 'Bob']\nprint(sorted(names, key=lambda n: n[-1]))",
             "explanation": "The lambda supplies a sorting key — the last character of each name."},
        ],
        [
            "Using a comprehension purely for side effects such as `print()`.",
            "Reusing a loop variable after a comprehension (in Python 3 it does not leak).",
            "Writing unreadable nested lambdas instead of a named function.",
        ],
        "Comprehensions and lambdas appear constantly in professional Python. They make data "
        "transformations shorter once you can read them fluently.",
        ex("squares-dict", "Write `squares_dict(n)` returning `{number: number ** 2}` for numbers 1 through n.",
           "def squares_dict(n):\n    pass\n",
           calls("squares_dict", [(3, {1: 1, 2: 4, 3: 9}), (0, {}), (1, {1: 1})])),
    ),
    T(
        "iterators-and-generators", "Iterators and Generators", 2, "Advanced Fundamentals",
        "Lazy sequences that produce values one at a time instead of building lists.",
        "An iterator implements `__iter__` and `__next__`. A generator function uses `yield`; calling it "
        "returns a lazy iterator that resumes where it stopped. Generators can represent infinite "
        "sequences and keep memory flat because they do not store every value.\n\n"
        "Generator expressions `(x for x in items)` are the lazy cousin of list comprehensions. "
        "Consumers such as `sum()`, `list()` and `for` loops drive the generator. Remember that a "
        "generator is single-use: once exhausted it stays empty. The `itertools` module supplies "
        "batteries such as `chain`, `groupby` and `islice`.",
        [
            {"code": "def evens(limit):\n    for n in range(limit):\n        if n % 2 == 0:\n            yield n\n\nprint(list(evens(6)))  # [0, 2, 4]",
             "explanation": "yield pauses the function until the next value is requested."},
            {"code": "import itertools\nprint(list(itertools.islice(itertools.count(1), 5)))  # [1, 2, 3, 4, 5]",
             "explanation": "count() is infinite; islice takes a finite prefix."},
        ],
        [
            "Calling `len()` on a generator — it has no known length.",
            "Expecting a generator to be reusable after `list()` consumes it.",
            "Using `yield` and `return value` interchangeably in a generator (return sets StopIteration.value).",
        ],
        "Streaming logs, large CSV files and pipelines all depend on lazy evaluation. Generators let you "
        "process data larger than memory.",
        ex("fibonacci", "Write a generator function `fibonacci(n)` yielding the first n Fibonacci numbers starting with 0, 1.",
           "def fibonacci(n):\n    # yield values lazily\n    pass\n",
           [{"name": "First five", "assertion": "assert list(solution.fibonacci(5)) == [0, 1, 1, 2, 3]"},
            {"name": "Zero values", "assertion": "assert list(solution.fibonacci(0)) == []"}]),
    ),
    T(
        "apis-and-external-libraries", "APIs and External Libraries", 2, "Integration",
        "Calling HTTP APIs, installing packages and keeping credentials out of code.",
        "The `requests` library sends HTTP calls: `requests.get(url, params=..., timeout=10)` returns a "
        "response with `.status_code`, `.json()` and `.text`. Always set a timeout, check the status code "
        "with `raise_for_status()`, and expect the network to fail — catch `requests.RequestException` and "
        "decide whether to retry.\n\n"
        "External packages are installed with pip into a virtual environment (`python -m venv .venv`) so "
        "projects do not fight over versions; record them in `requirements.txt`. Credentials belong in "
        "environment variables, never in source code. Treat third-party data as untrusted: validate its "
        "shape before using it.",
        [
            {"code": "import requests\ntry:\n    r = requests.get('https://api.example.com/items', params={'page': 1}, timeout=5)\n    r.raise_for_status()\n    items = r.json()\nexcept requests.RequestException as exc:\n    items = []\n    print('Request failed:', exc)",
             "explanation": "Timeout, status check and error handling are all part of one robust call."},
            {"code": "import os\ntoken = os.environ['API_TOKEN']\nheaders = {'Authorization': f'Bearer {token}'}",
             "explanation": "The secret comes from the environment, not from a checked-in file."},
        ],
        [
            "Omitting `timeout=` and letting a request hang forever.",
            "Committing API keys to a repository.",
            "Assuming an API always returns the expected JSON shape.",
        ],
        "Weather apps, scrapers and integrations live or die by their API code. This skill also underpins "
        "the way this academy talks to its own execution service.",
        ex("build-url", "Write `build_url(base, path, params)` returning a URL like 'https://x.test/items?page=2&sort=asc' using urllib.parse.urlencode.",
           "from urllib.parse import urlencode\n\ndef build_url(base, path, params):\n    pass\n",
           calls("build_url", [(("https://x.test", "items", {"page": 2, "sort": "asc"}), "https://x.test/items?page=2&sort=asc")])),
    ),
]
