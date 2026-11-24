"""Level 1 — Beginner knowledge-library topics."""

from .helpers import T, calls, ex

TOPICS = [
    T(
        "variables-and-data-types", "Variables and Data Types", 1, "Fundamentals",
        "Names that hold values, and the different kinds of values Python understands.",
        "A variable is a name bound to an object. You create one with `=`, and Python decides the type "
        "at runtime. Rebinding a name to a different type is allowed, which is useful but can hide bugs.\n\n"
        "The core built-in types are `int`, `float`, `str`, `bool`, `list`, `tuple`, `dict` and `set`. "
        "`type(value)` tells you what you have, and `isinstance(value, int)` checks membership in a type "
        "hierarchy (a `bool` is a subclass of `int`, so use `type(x) is bool` when that matters).",
        [
            {"code": "age = 27\nname = 'Niel'\nis_learning = True\nprint(type(age), type(name), type(is_learning))",
             "explanation": "Each assignment binds a name to an object. The printed types are int, str and bool."},
            {"code": "a = 10\na = a + 5\nprint(a)  # 15\na = 'now a string'\nprint(type(a))  # <class 'str'>",
             "explanation": "Names can be rebound to any type. Read your own code carefully when a name changes meaning."},
        ],
        [
            "Thinking of variables as boxes that permanently keep one type — Python names are labels, not typed boxes.",
            "Using `isinstance(True, int)` and being surprised that it returns True.",
            "Naming a variable `list`, `str` or `dict`, which shadows the built-in you may need later.",
        ],
        "Every program manipulates data. Knowing which type you hold determines which operations are valid and "
        "which bugs are possible.",
        ex("total-price", "Write `total_price(quantity, unit_price)` that returns the cost as a number.",
           "def total_price(quantity, unit_price):\n    # return quantity multiplied by unit_price\n    pass\n",
           calls("total_price", [((3, 2.5), 7.5), ((0, 9.99), 0), ((2, 3), 6)])),
    ),
    T(
        "strings-and-numbers", "Strings and Numbers", 1, "Fundamentals",
        "Building, slicing and formatting text; doing arithmetic without surprises.",
        "Strings are immutable sequences of characters. Indexing starts at zero, slices use `[start:stop]` "
        "where `stop` is exclusive, and methods such as `.strip()`, `.split()`, `.replace()` and `.join()` "
        "return **new** strings. F-strings (`f'{value=}'`) are the clearest way to interpolate values.\n\n"
        "Python has arbitrary-precision integers and `float` for decimal approximations. Floats can be "
        "imprecise (`0.1 + 0.2 != 0.3`); use `round()` for display and `decimal.Decimal` when exact decimal "
        "arithmetic matters (money, for example). Floor division `//` and modulo `%` are essential tools for "
        "splitting values into groups.",
        [
            {"code": "name = '  python academy  '\nclean = name.strip().title()\nprint(clean)  # Python Academy\nprint(clean[:6])  # Python",
             "explanation": "strip() removes outer whitespace, title() capitalises words, and the slice takes the first six characters."},
            {"code": "total = 17\nprint(f'{total // 5} groups, {total % 5} left over')\nprint(f'{total / 5:.2f}')",
             "explanation": "Floor division and modulo split into whole groups and a remainder; :.2f formats to two decimals."},
        ],
        [
            "Expecting `s.upper()` to change `s` in place — strings cannot be mutated.",
            "Confusing `/` (float division) with `//` (floor division).",
            "Comparing floats directly instead of using a tolerance or rounding.",
        ],
        "User input arrives as text, output is text, and logs are text. String and number manipulation is "
        "the daily bread of every Python program.",
        ex("initials", "Write `initials(full_name)` returning uppercase initials separated by a dot, e.g. 'Ada Lovelace' -> 'A.L'.",
           "def initials(full_name):\n    pass\n",
           calls("initials", [("Ada Lovelace", "A.L"), ("Grace Hopper", "G.H"), ("alan", "A")])),
    ),
    T(
        "lists-tuples-and-dictionaries", "Lists, Tuples and Dictionaries", 1, "Data Structures",
        "The three workhorses: ordered mutable lists, fixed tuples and key-to-value dictionaries.",
        "A `list` is ordered and mutable: `append`, `insert`, `pop`, slicing and sorting are everyday tools. "
        "A `tuple` is ordered but immutable; use it for records that should not change and as dictionary keys. "
        "A `dict` maps hashable keys to values, with O(1) average lookup — choose it when you need to find "
        "items by a name or ID.\n\n"
        "Beware of aliasing: `b = a` makes two names for the same list, while `b = a.copy()` or `a[:]` makes a "
        "shallow copy. Nested structures need `copy.deepcopy()`. Mutating a list while iterating over it "
        "usually causes skipped items; build a new list or iterate over a copy instead.",
        [
            {"code": "tasks = ['write tests', 'review code']\ntasks.append('commit')\nfirst, *rest = tasks\nprint(first, rest)",
             "explanation": "append mutates the list; starred unpacking collects everything after the first item."},
            {"code": "person = {'name': 'Ada', 'skills': ['math', 'code']}\nprint(person.get('age', 'unknown'))\nfor key, value in person.items():\n    print(key, value)",
             "explanation": "get() avoids KeyError, and items() iterates over key/value pairs."},
        ],
        [
            "Using a list for lookups by ID when a dictionary would be far faster.",
            "Calling `sorted(items)` expecting the original list to be sorted — sorted() returns a new list.",
            "Removing items from a list inside a `for` loop over that same list.",
        ],
        "Almost every project in this academy stores its state in a list of dictionaries or a dictionary "
        "of lists. Mastering them removes a whole category of bugs.",
        ex("most-common", "Write `most_common(items)` returning the value that appears most often (ties go to the first value seen).",
           "def most_common(items):\n    pass\n",
           calls("most_common", [([1, 2, 2, 3], 2), (['a', 'b', 'a', 'b'], 'a'), ([], None)])),
    ),
    T(
        "sets", "Sets", 1, "Data Structures",
        "Unordered collections of unique values, built for membership tests and set algebra.",
        "A `set` stores unique, hashable values. `in` is average O(1), so sets are the right tool for 'have "
        "I seen this before?' checks. Use `add`, `remove`/`discard`, and operators `|` (union), `&` "
        "(intersection), `-` (difference) and `^` (symmetric difference). A `frozenset` is an immutable "
        "set that can be used as a dictionary key.\n\n"
        "Set literals cannot be empty — `{}` is a dictionary, so use `set()`. Iteration order is not "
        "guaranteed; sort the set when you need stable output.",
        [
            {"code": "seen = set()\nfor word in ['a', 'b', 'a']:\n    if word not in seen:\n        seen.add(word)\nprint(seen)  # {'a', 'b'}",
             "explanation": "Membership testing against a set avoids duplicates efficiently."},
            {"code": "python = {'loops', 'functions', 'classes'}\nknown = {'loops', 'variables'}\nprint(sorted(python - known))  # ['classes', 'functions']",
             "explanation": "Difference answers 'what is in python but not in known'; sorted() makes output predictable."},
        ],
        [
            "Writing `{}` and expecting an empty set.",
            "Putting a list inside a set — members must be hashable.",
            "Assuming sets preserve insertion order when producing output.",
        ],
        "Deduplication, tag filtering and 'does this exist?' checks appear in almost every application. "
        "Sets make those operations both shorter and faster.",
        ex("unique_tags", "Write `unique_tags(tags)` returning a sorted list of unique tags.",
           "def unique_tags(tags):\n    pass\n",
           calls("unique_tags", [(['b', 'a', 'b'], ['a', 'b']), (['x'], ['x']), ([], [])])),
    ),
    T(
        "conditionals", "Conditional Statements", 1, "Control Flow",
        "Making decisions with if / elif / else, truthiness and short-circuit logic.",
        "`if` runs a branch when its condition is truthy. Python's truthiness rules matter: `0`, `''`, "
        "`[]`, `{}`, `set()` and `None` are falsey; most other objects are truthy. Use `and`/`or` with "
        "short-circuit evaluation to guard unsafe operations, for example `if items and items[0] > 5`."
        "\n\nPrefer expressions over nested branches where it improves clarity: `status = 'pass' if score "
        ">= 50 else 'fail'`. The `match` statement (Python 3.10+) is useful when comparing one value "
        "against several structural patterns.",
        [
            {"code": "score = 72\nif score >= 90:\n    grade = 'A'\nelif score >= 70:\n    grade = 'B'\nelse:\n    grade = 'C'\nprint(grade)  # B",
             "explanation": "Only the first matching branch runs, so order conditions from most to least specific."},
            {"code": "name = input('Name: ').strip()\nif name and name[0].isupper():\n    print('Looks like a proper name')",
             "explanation": "`name and ...` prevents an IndexError when the input is empty."},
        ],
        [
            "Using `if x == True` instead of `if x`.",
            "Stacking `elif` after an `else`.",
            "Forgetting that `and`/`or` return one of their operands, not necessarily a bool.",
        ],
        "Validation, game rules, routing and error handling all begin with a conditional. Clear conditions "
        "make a program easy to reason about.",
        ex("grade", "Write `grade(score)` returning 'A' for 90+, 'B' for 70+, 'C' for 50+ and 'F' below.",
           "def grade(score):\n    pass\n",
           calls("grade", [(95, 'A'), (70, 'B'), (50, 'C'), (49, 'F')])),
    ),
    T(
        "loops", "Loops", 1, "Control Flow",
        "Repeating work with for and while, plus break, continue and enumerate.",
        "Use a `for` loop when you know the collection you are walking; use `while` when a condition "
        "controls the repetition. `range(n)` yields 0..n-1, `enumerate(items)` gives index/value pairs, "
        "and `zip(a, b)` walks two sequences in parallel. `break` leaves the loop, `continue` skips to "
        "the next iteration, and the optional `else` clause runs only when no `break` occurred.\n\n"
        "Accumulate results in a new list or a running total. Avoid using `len(range(...))` patterns and "
        "indexing when iterating over the values themselves is clearer.",
        [
            {"code": "for index, name in enumerate(['Ada', 'Grace']):\n    print(index + 1, name)",
             "explanation": "enumerate avoids manual counter management."},
            {"code": "for n in range(2, 10):\n    if n % 2 == 0:\n        continue\n    print(n)  # 3 5 7 9",
             "explanation": "continue jumps to the next iteration without running the rest of the body."},
        ],
        [
            "Writing `for i in range(len(items))` when `for item in items` is enough.",
            "Modifying the list you are iterating over.",
            "Creating an infinite `while` loop with no exit condition.",
        ],
        "Batch processing, simulations, searching and data cleanup are all loops. Writing clean loops is "
        "the first step towards comprehensions and generators.",
        ex("sum_evens", "Write `sum_evens(numbers)` returning the sum of the even values.",
           "def sum_evens(numbers):\n    pass\n",
           calls("sum_evens", [([1, 2, 3, 4], 6), ([], 0), ([7, 9], 0)])),
    ),
    T(
        "functions", "Functions", 1, "Code Organisation",
        "Reusable blocks with parameters, return values, scope and default arguments.",
        "Functions turn a repeated procedure into a named operation with a clear contract: arguments in, "
        "return value out. Use docstrings to describe that contract. A function should return its result "
        "rather than printing it whenever the caller may need to test or reuse that result.\n\n"
        "Default arguments are evaluated **once** when the function is defined, so never use a mutable "
        "default such as `def add(item, items=[])`. Use `None` and create the list inside the function. "
        "Arguments can be positional, keyword-only after `*`, or variadic with `*args` and `**kwargs`.",
        [
            {"code": "def add_item(item, items=None):\n    if items is None:\n        items = []\n    items.append(item)\n    return items",
             "explanation": "A fresh list is created for each call that omits `items`."},
            {"code": "def describe(name, *, excited=False):\n    return f'Hello {name}{chr(33) if excited else chr(46)}'",
             "explanation": "The `*` makes `excited` keyword-only, which keeps call sites readable."},
        ],
        [
            "Using a mutable default argument.",
            "Printing a result instead of returning it, making it impossible to test.",
            "Expecting variables created inside a function to be visible outside it.",
        ],
        "Functions are the unit of testing in Python. Every project and challenge in this academy evaluates "
        "functions you write, so designing good signatures is a practical skill.",
        ex("rectangle_area", "Write `rectangle_area(width, height=1)` returning the area.",
           "def rectangle_area(width, height=1):\n    pass\n",
           calls("rectangle_area", [((3, 4), 12), ((5,), 5), ((2.5, 2), 5.0)])),
    ),
    T(
        "user-input-and-errors", "User Input and Error Handling", 1, "Robustness",
        "Reading input, validating it, and handling failures with try / except.",
        "`input(prompt)` always returns a string, so convert explicitly with `int()` or `float()`. Wrap "
        "conversions in `try`/`except ValueError` to recover from bad input. `except Exception` catches "
        "almost everything but hides bugs — catch the specific exception you expect.\n\n"
        "Use `else` for code that should run only when no exception occurred, and `finally` for cleanup. "
        "Raise your own errors with a clear message when a function receives invalid data. Tracebacks read "
        "from bottom to top: the final line tells you the exception, the lines above show the call path.",
        [
            {"code": "try:\n    age = int(input('Age: '))\nexcept ValueError:\n    print('Please enter a whole number')\nelse:\n    print(f'Next year you will be {age + 1}')",
             "explanation": "The conversion can fail; else keeps the success path separate from the error path."},
            {"code": "def withdraw(balance, amount):\n    if amount <= 0:\n        raise ValueError('amount must be positive')\n    if amount > balance:\n        raise ValueError('insufficient funds')\n    return balance - amount",
             "explanation": "Raising precise errors makes callers handle invalid states explicitly."},
        ],
        [
            "Catching bare `except:` and silently ignoring every problem.",
            "Assuming `input()` returns a number.",
            "Ignoring the message at the bottom of a traceback.",
        ],
        "Real users type unexpected things and real files are missing. Defensive code turns crashes into "
        "helpful feedback.",
        ex("safe_divide", "Write `safe_divide(a, b)` returning the quotient, or None when b is zero or values are not numbers.",
           "def safe_divide(a, b):\n    pass\n",
           calls("safe_divide", [((10, 2), 5.0), ((10, 0), None), (('x', 2), None)])),
    ),
]
