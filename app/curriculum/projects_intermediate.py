"""Level 2 projects — state, files, data formats and integration."""

from .helpers import A, P, calls

PROJECTS = [
    P(
        "expense-tracker", "Expense Tracker", 2,
        "Track spending by category with a class that protects its own invariants.",
        "Personal finance tools are a natural fit for objects: expenses arrive one at a time, need to be "
        "grouped, and must never contain impossible values. Build a tracker that rejects invalid amounts, "
        "sums correctly with floats, and can report totals per category. Resist the urge to print inside "
        "the class — reports should be data the caller can display.",
        ["Encapsulate state in a class", "Validate values at the boundary", "Aggregate with dictionaries",
         "Round money values deliberately"],
        ["Classes", "Validation", "Dictionaries", "Floats"],
        [
            "Define the tracker", "`ExpenseTracker()` starts empty with a total of 0.",
            "Record expenses", "`add_expense(category, amount)` accepts a non-empty category and a positive number, stores the expense and returns the stored amount. Invalid input raises `ValueError`.",
            "Report totals", "`total()` returns the sum of all amounts; `by_category()` returns a dictionary of category totals; `count()` returns the number of expenses.",
            "Handle floating point", "Round reported totals to two decimal places so `0.1 + 0.2` does not leak into your output.",
        ],
        [
            "`ExpenseTracker` provides `add_expense`, `total`, `by_category` and `count`.",
            "Amounts must be positive numbers (int or float, not bool); invalid categories or amounts raise `ValueError`.",
            "Reported totals are rounded to two decimal places.",
        ],
        [
            A("Empty tracker", "t = solution.ExpenseTracker()\nassert t.total() == 0 and t.count() == 0 and t.by_category() == {}"),
            A("Add and total", "t = solution.ExpenseTracker()\nassert t.add_expense('food', 12.5) == 12.5\nassert t.add_expense('food', 7.25) == 7.25\nassert t.add_expense('transport', 10) == 10\nassert t.total() == 29.75\nassert t.count() == 3"),
            A("By category", "t = solution.ExpenseTracker()\nt.add_expense('food', 2)\nt.add_expense('food', 3)\nt.add_expense('travel', 4)\nassert t.by_category() == {'food': 5, 'travel': 4}"),
            A("Invalid input", "t = solution.ExpenseTracker()\nfor args in [('', 5), ('food', 0), ('food', -2), ('food', '5')]:\n    try:\n        t.add_expense(*args)\n    except ValueError:\n        pass\n    else:\n        raise AssertionError(f'accepted {args}')\nassert t.count() == 0"),
        ],
        "class ExpenseTracker:\n    pass\n",
        "You combined encapsulation, validation and aggregation, and learned to control floating-point "
        "output instead of hoping it behaves.", 90,
    ),
    P(
        "weather-application", "Weather Application", 2,
        "Turn a messy API payload into a clean, predictable data structure.",
        "Real APIs return nested dictionaries with inconsistent fields. Before you can display anything you "
        "need an adapter that extracts what you care about and defines sensible defaults. This project "
        "uses a representative payload so you can focus on parsing rather than network access, but the "
        "skill transfers directly to live requests.",
        ["Parse nested JSON-like data", "Provide defaults for missing fields", "Convert units",
         "Validate third-party data"],
        ["Dictionaries", "API data", "Defaults", "Validation"],
        [
            "Study the payload", "A payload looks like `{'name': 'Cape Town', 'main': {'temp': 21.3}, 'weather': [{'description': 'cloudy'}]}`.",
            "Extract the essentials", "`parse_weather(payload)` returns `{'city': str, 'temperature': float, 'condition': str}`. Missing name/description becomes `'unknown'`; a missing temp becomes 0.0.",
            "Add conversions", "`celsius_to_fahrenheit(value)` returns the Fahrenheit equivalent rounded to one decimal place.",
            "Format a report", "`weather_report(payload)` returns `'Cape Town: 21.3 C, cloudy'` using the parsed values.",
        ],
        [
            "`parse_weather` always returns the three named keys, even when fields are missing.",
            "`celsius_to_fahrenheit(0)` is 32.0 and `celsius_to_fahrenheit(100)` is 212.0.",
            "`weather_report` returns exactly `'<city>: <temperature> C, <condition>'`.",
        ],
        [
            A("Full payload", "p = {'name': 'Cape Town', 'main': {'temp': 21.3}, 'weather': [{'description': 'cloudy'}]}\nassert solution.parse_weather(p) == {'city': 'Cape Town', 'temperature': 21.3, 'condition': 'cloudy'}"),
            A("Missing fields", "assert solution.parse_weather({}) == {'city': 'unknown', 'temperature': 0.0, 'condition': 'unknown'}"),
            calls("celsius_to_fahrenheit", [((0,), 32.0), ((100,), 212.0), ((-40,), -40.0)]),
            A("Report", "p = {'name': 'Cape Town', 'main': {'temp': 21.3}, 'weather': [{'description': 'cloudy'}]}\nassert solution.weather_report(p) == 'Cape Town: 21.3 C, cloudy'"),
        ],
        "def parse_weather(payload):\n    pass\n\n\ndef celsius_to_fahrenheit(value):\n    pass\n\n\ndef weather_report(payload):\n    pass\n",
        "You built an adapter around untrusted third-party data, with defaults and conversions that make "
        "the rest of an application simpler.", 90,
    ),
    P(
        "web-scraper", "Web Scraper", 2,
        "Extract structured information from HTML without relying on fragile string tricks.",
        "Scraping means turning documents written for humans into data your program can use. Regular "
        "expressions are tempting but break on attribute ordering, quotes and nesting. Use `html.parser` "
        "from the standard library to walk anchor tags properly, and normalise the results so callers get "
        "a clean list.",
        ["Parse HTML safely", "Handle missing and repeated attributes", "Deduplicate results",
         "Respect structure over regex"],
        ["HTMLParser", "Strings", "Sets", "Data cleaning"],
        [
            "Build a parser", "Subclass `html.parser.HTMLParser` and implement `handle_starttag` to record the `href` of `<a>` tags.",
            "Extract links", "`extract_links(html)` returns a list of non-empty href values in document order, with duplicates removed.",
            "Ignore noise", "Anchors without `href`, or with an empty href, contribute nothing.",
            "Optional politeness layer", "Write a `fetch_links(url)` function using `requests` with a timeout and a User-Agent header. The tests only check `extract_links`.",
        ],
        [
            "`extract_links(html)` returns a list of strings, preserving first-seen order.",
            "Duplicate links appear only once; href values are stripped of outer whitespace.",
            "Malformed or empty HTML returns an empty list rather than raising.",
        ],
        [
            A("Basic links", "html = '<a href=\"/about\">About</a><a href='/contact'>Contact</a>'\nassert solution.extract_links(html) == ['/about', '/contact']"),
            A("Deduplicate and skip empty", "html = '<a href=\"x\">a</a><a>x</a><a href=\"  \">b</a><a href=\" x \">c</a>'\nassert solution.extract_links(html) == ['x']"),
            A("Empty document", "assert solution.extract_links('') == []\nassert solution.extract_links('<p>no links</p>') == []"),
            A("Mixed attributes", "html = '<a class=\"big\" href=\"one\">1</a><a href=\"two\" id=\"t\">2</a>'\nassert solution.extract_links(html) == ['one', 'two']"),
        ],
        "from html.parser import HTMLParser\n\ndef extract_links(html):\n    pass\n",
        "You used a real parser instead of a regex, preserved ordering while deduplicating, and handled "
        "imperfect markup — the same habits used in production scrapers.", 90,
    ),
    P(
        "contact-management-system", "Contact Management System", 2,
        "Build a small persistent address book with a clear class interface.",
        "Contacts need to be created, searched, updated and saved. This project adds persistence to the "
        "class-based skills from Level 1: your `ContactBook` must survive a save/load round trip and reject "
        "duplicates by email. Think carefully about what a returned dictionary means — always return "
        "copies so callers cannot corrupt your store by accident.",
        ["Design a CRUD interface", "Persist data as JSON", "Prevent duplicates", "Return defensive copies"],
        ["Classes", "JSON", "Validation", "Copying data"],
        [
            "Create the store", "`ContactBook()` starts empty. `add(name, email, phone='')` returns True on success and False if the email already exists.",
            "Find and list", "`find(name)` returns the first matching contact dict (case-insensitive substring match) or None. `all_contacts()` returns a list of copies sorted by name.",
            "Remove", "`remove(email)` deletes by exact email (case-insensitive) and returns True if something was removed.",
            "Persist", "`save(path)` writes JSON to a path; `ContactBook.load(path)` returns a new instance. Missing files should load as empty.",
        ],
        [
            "`add` rejects duplicate emails case-insensitively and empty names/emails.",
            "`find` is case-insensitive and matches substrings of the name.",
            "`all_contacts` returns copies sorted by name.",
            "Save/load preserves all contacts across a round trip.",
        ],
        [
            A("Add and find", "b = solution.ContactBook()\nassert b.add('Ada Lovelace', 'ada@example.com', '123') is True\nc = b.find('ada')\nassert c['email'] == 'ada@example.com'\nassert b.find('nobody') is None"),
            A("Duplicate rejected", "b = solution.ContactBook()\nb.add('Ada', 'ada@example.com')\nassert b.add('Ada Two', 'ADA@example.com') is False\nassert len(b.all_contacts()) == 1"),
            A("Sorted copies", "b = solution.ContactBook()\nb.add('Zoe', 'z@x.test'); b.add('Ada', 'a@x.test')\ncontacts = b.all_contacts()\nassert [c['name'] for c in contacts] == ['Ada', 'Zoe']\ncontacts[0]['name'] = 'hacked'\nassert b.all_contacts()[0]['name'] == 'Ada'"),
            A("Remove", "b = solution.ContactBook()\nb.add('Ada', 'ada@x.test')\nassert b.remove('ADA@x.test') is True\nassert b.remove('ada@x.test') is False"),
            A("Round trip", "import tempfile, os\nb = solution.ContactBook()\nb.add('Ada', 'ada@x.test', '123')\np = os.path.join(tempfile.mkdtemp(), 'contacts.json')\nb.save(p)\nloaded = solution.ContactBook.load(p)\nassert loaded.all_contacts() == b.all_contacts()"),
        ],
        "class ContactBook:\n    pass\n",
        "You implemented full CRUD behaviour, protected your store from outside mutation, and added "
        "persistence with a JSON round-trip test.", 120,
    ),
    P(
        "file-organiser", "File Organiser", 2,
        "Classify files by type and plan a safe, reversible organisation strategy.",
        "Before moving real files you need a reliable classification function and a dry run. This project "
        "keeps the tests on pure functions (so nothing touches your disk unexpectedly) while asking you to "
        "think through the filesystem step. Consider name collisions, case sensitivity and unknown "
        "extensions.",
        ["Work with paths and suffixes", "Group data by category", "Handle unknown values",
         "Plan safe filesystem changes"],
        ["pathlib", "Dictionaries", "File extensions", "Dry runs"],
        [
            "Define categories", "images: png/jpg/jpeg/gif/webp; documents: pdf/doc/docx/txt/md; code: py/js/html/css/json; archives: zip/tar/gz; everything else: other.",
            "Classify one file", "`categorise(filename)` returns the lowercase category name. Comparison is case-insensitive: `Photo.PNG` is an image.",
            "Group many files", "`group_by_category(filenames)` returns `{category: [filenames...]}` preserving input order within each category; omit empty categories.",
            "Plan the move", "`plan_moves(filenames, target_dir)` returns a dict mapping each original filename to the planned destination path string (use `pathlib` so separators are correct).",
        ],
        [
            "Categories are exactly the five names listed above.",
            "`categorise` handles uppercase extensions and files with no suffix.",
            "`group_by_category` preserves order and never includes empty lists.",
            "`plan_moves` does not touch the filesystem; it only computes paths.",
        ],
        calls("categorise", [("photo.PNG", "images"), ("notes.pdf", "documents"), ("main.py", "code"), ("backup.zip", "archives"), ("README", "other")])
        + [
            A("Grouping", "result = solution.group_by_category(['a.py', 'b.png', 'c.py', 'x.unknown'])\nassert result == {'code': ['a.py', 'c.py'], 'images': ['b.png'], 'other': ['x.unknown']}"),
            A("Empty grouping", "assert solution.group_by_category([]) == {}"),
        ],
        "from pathlib import Path\n\ndef categorise(filename):\n    pass\n\n\ndef group_by_category(filenames):\n    pass\n\n\ndef plan_moves(filenames, target_dir):\n    pass\n",
        "You built a classification layer, grouped data deterministically, and separated planning from "
        "mutating the filesystem — a key safety pattern.", 90,
    ),
    P(
        "personal-habit-tracker", "Personal Habit Tracker", 2,
        "Measure consistency with date strings and streak calculations.",
        "Habits are about consistency, not totals. Storing completions as date strings in a set makes "
        "membership checks trivial, but calculating a streak requires careful date arithmetic. You will "
        "write code that handles gaps, unsorted entries and empty histories without resorting to live "
        "clock reads, which makes it fully testable.",
        ["Model events by date", "Use datetime arithmetic", "Compute streaks", "Avoid hidden time dependencies"],
        ["datetime module", "Sets", "Algorithms", "Validation"],
        [
            "Create the tracker", "`HabitTracker(name)` stores the habit name. `mark_done(day)` accepts a `'YYYY-MM-DD'` string and returns True when newly recorded.",
            "Query days", "`done_on(day)` returns a boolean; invalid date strings raise `ValueError`.",
            "Calculate streaks", "`streak(today)` returns the number of consecutive days ending at `today` (inclusive) that are marked done. If today is not marked, return 0.",
            "Summarise", "`summary(today)` returns `{'name': ..., 'total': int, 'streak': int}`.",
        ],
        [
            "Dates use the ISO format `YYYY-MM-DD` and invalid strings raise `ValueError`.",
            "`mark_done` returns False for a day that was already recorded.",
            "`streak(today)` counts backwards from today and stops at the first gap.",
            "No function calls `datetime.now()` — all dates come from arguments.",
        ],
        [
            A("Mark and query", "h = solution.HabitTracker('Read')\nassert h.mark_done('2026-01-01') is True\nassert h.mark_done('2026-01-01') is False\nassert h.done_on('2026-01-01') is True\nassert h.done_on('2026-01-02') is False"),
            A("Invalid date", "h = solution.HabitTracker('Read')\ntry:\n    h.done_on('01/01/2026')\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('expected ValueError')"),
            A("Streak counts back", "h = solution.HabitTracker('Read')\nfor d in ['2026-01-01', '2026-01-02', '2026-01-03']:\n    h.mark_done(d)\nassert h.streak('2026-01-03') == 3\nassert h.streak('2026-01-04') == 0"),
            A("Gap breaks streak", "h = solution.HabitTracker('Read')\nh.mark_done('2026-01-01'); h.mark_done('2026-01-03')\nassert h.streak('2026-01-03') == 1"),
            A("Summary", "h = solution.HabitTracker('Read')\nh.mark_done('2026-01-03')\nassert h.summary('2026-01-03') == {'name': 'Read', 'total': 1, 'streak': 1}"),
        ],
        "from datetime import date, timedelta\n\nclass HabitTracker:\n    pass\n",
        "You worked with dates deterministically, enforced a format contract and implemented a streak "
        "algorithm that handles gaps — a common real-world data problem.", 90,
    ),
]
