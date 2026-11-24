"""Level 1 projects — small, complete programs with behavioural tests."""

from .helpers import A, P, calls

PROJECTS = [
    P(
        "calculator", "Calculator", 1,
        "Build a dependable calculator whose operations can be tested independently.",
        "A calculator looks trivial until you try to make it reliable. In this project you will separate "
        "four mathematical operations into small functions, decide what should happen when someone divides "
        "by zero, and write code that behaves predictably for integers and floats. The discipline of "
        "making each operation independently testable is the real lesson.",
        ["Write focused functions with clear contracts", "Handle invalid operations explicitly",
         "Use assertions to verify behaviour", "Separate logic from presentation"],
        ["Functions", "Numbers", "Exceptions", "Return values"],
        [
            "Write the four operations", "Create `add`, `subtract`, `multiply` and `divide`. Each takes two numbers and returns the result. Do not print inside these functions.",
            "Guard division", "Decide how `divide` behaves when the divisor is zero. Raising `ZeroDivisionError` with a helpful message is the expected behaviour here.",
            "Test the edges", "Check negative numbers, zero, floats and large values by running the project tests.",
            "Optional command line", "If you have time, add an `if __name__ == '__main__':` block that reads two numbers and an operator from input and prints the result. The tests ignore this block.",
        ],
        [
            "`add(a, b)` returns the sum; `subtract(a, b)` returns a - b; `multiply(a, b)` returns the product.",
            "`divide(a, b)` returns a / b and raises `ZeroDivisionError` when b is 0.",
            "No function prints; every function returns its result.",
        ],
        calls("add", [((2, 3), 5), ((-2, 3), 1), ((2.5, 0.5), 3.0)])
        + calls("subtract", [((10, 4), 6), ((4, 10), -6)])
        + calls("multiply", [((3, 4), 12), ((0, 5), 0)])
        + [A("Multiply floats", "assert abs(solution.multiply(2.5, 4) - 10) < 1e-9")]
        + calls("divide", [((10, 2), 5.0), ((9, 4), 2.25)])
        + [A("Division by zero raises", "try:\n    solution.divide(1, 0)\nexcept ZeroDivisionError:\n    pass\nelse:\n    raise AssertionError('expected ZeroDivisionError')")],
        "def add(a, b):\n    pass\n\n\ndef subtract(a, b):\n    pass\n\n\ndef multiply(a, b):\n    pass\n\n\ndef divide(a, b):\n    pass\n",
        "You practised pure functions, numeric edge cases and explicit exception handling — the habit of "
        "making each operation testable in isolation.", 60,
    ),
    P(
        "number-guessing-game", "Number Guessing Game", 1,
        "Implement the rules of a guessing game before worrying about the interface.",
        "Games are a friendly way to practise conditionals. The core of a guessing game is a decision: "
        "is the guess too low, too high or exactly right? By putting that decision in a pure function you "
        "can test every branch without playing the game manually. Then wrap it in a loop with input and "
        "limited attempts.",
        ["Implement game rules as a testable function", "Compare values with conditionals",
         "Use a loop with an exit condition", "Give useful feedback"],
        ["Conditionals", "Comparison", "Functions", "While loops"],
        [
            "Decide the contract", "`evaluate_guess(secret, guess)` must return exactly one of `'too low'`, `'too high'` or `'correct'`.",
            "Cover every branch", "Test guesses below, above and equal to the secret, including negative secrets.",
            "Add the game loop", "Write `play(secret, guesses)` that evaluates a list of guesses and returns the number of attempts used, stopping early on a correct guess. Return -1 if none are correct.",
            "Optional interface", "Use `input()` to ask a human for guesses, validate the input and show a remaining-attempts counter.",
        ],
        [
            "`evaluate_guess(secret, guess)` returns the lowercase strings `'too low'`, `'too high'` or `'correct'`.",
            "`play(secret, guesses)` returns the 1-based index of the correct guess, or -1 if the list contains no correct guess.",
            "The game stops evaluating guesses after the first correct one.",
        ],
        calls("evaluate_guess", [((50, 20), "too low"), ((50, 80), "too high"), ((50, 50), "correct"), ((-3, -5), "too low")])
        + calls("play", [((50, [10, 90, 50, 50]), 3), ((50, [1, 2]), -1), ((7, [7]), 1)]),
        "def evaluate_guess(secret, guess):\n    pass\n\n\ndef play(secret, guesses):\n    pass\n",
        "You modelled rules as a pure function, covered all branches with tests, and combined it with "
        "stateful loop logic.", 60,
    ),
    P(
        "todo-list", "To-Do List", 1,
        "Manage a collection of tasks with a small class and predictable state changes.",
        "A to-do list is the classic first stateful program. You will design a `TodoList` class that owns "
        "its tasks, returns useful values from every mutation, and never exposes broken state. Think about "
        "what should happen when someone removes a task that does not exist — a strong contract makes "
        "your code easy to use and easy to test.",
        ["Model state with a class", "Define clear return values", "Handle missing items gracefully",
         "Track completion separately from removal"],
        ["Classes", "Lists", "Methods", "State"],
        [
            "Create the class", "`TodoList()` starts with no tasks and no completed tasks.",
            "Add tasks", "`add(task)` appends a non-empty task string and returns its 0-based index. Ignore empty strings and return -1 for them.",
            "Remove and inspect", "`remove(index)` removes and returns the task at that index, or None when the index is invalid. `tasks()` returns a copy of the remaining task strings.",
            "Complete tasks", "`complete(index)` moves a task into the completed list and returns it, or None for an invalid index. `completed()` returns a copy of that list.",
        ],
        [
            "`TodoList` provides `add`, `remove`, `tasks`, `complete` and `completed` as described.",
            "Returned lists are copies — mutating them must not change the internal state.",
            "Invalid indexes and empty task strings never raise an exception.",
        ],
        [
            A("Initial state", "t = solution.TodoList()\nassert t.tasks() == [] and t.completed() == []"),
            A("Add returns index", "t = solution.TodoList()\nassert t.add('write tests') == 0\nassert t.add('commit') == 1\nassert t.add('   ') == -1"),
            A("Remove", "t = solution.TodoList()\nt.add('one'); t.add('two')\nassert t.remove(0) == 'one'\nassert t.tasks() == ['two']\nassert t.remove(99) is None"),
            A("Complete", "t = solution.TodoList()\nt.add('one'); t.add('two')\nassert t.complete(0) == 'one'\nassert t.completed() == ['one']\nassert t.tasks() == ['two']"),
            A("Copies are safe", "t = solution.TodoList()\nt.add('one')\nx = t.tasks(); x.append('hack')\nassert t.tasks() == ['one']"),
        ],
        "class TodoList:\n    pass\n",
        "You designed a class contract, protected internal state with copies, and handled invalid input "
        "without exceptions escaping.", 75,
    ),
    P(
        "password-generator", "Password Generator", 1,
        "Generate strong passwords and explain what makes them strong.",
        "Randomness is easy to call and easy to misuse. This project asks you to build a generator that "
        "always includes the character classes it promises, uses the `secrets` module (not `random`), and "
        "can report a simple strength rating. Tests check properties of many generated passwords rather "
        "than one fixed string.",
        ["Use cryptographically secure randomness", "Guarantee character-class requirements",
         "Validate input", "Write property-based assertions"],
        ["Strings", "secrets module", "Validation", "Sets"],
        [
            "Choose secure randomness", "Use `secrets.choice` and the string constants in `string.ascii_letters` / `string.digits` / `string.punctuation`.",
            "Build the generator", "`generate_password(length, use_symbols=True)` returns a string of exactly `length` characters containing at least one letter, one digit, and — when symbols are enabled — one symbol. Reject lengths below 4 with `ValueError`.",
            "Add a strength rating", "`password_strength(password)` returns `'weak'` for fewer than 8 characters or fewer than 3 distinct character classes, otherwise `'strong'`.",
            "Explore properties", "Generate 100 passwords and check the guarantees hold every time. Randomness that fails once is broken.",
        ],
        [
            "`generate_password(length, use_symbols=True)` returns a string with exactly `length` characters.",
            "It always contains at least one letter and one digit; with `use_symbols=True` it also contains at least one character from `string.punctuation`.",
            "Lengths below 4 raise `ValueError`.",
            "`password_strength(password)` returns `'weak'` or `'strong'` as described.",
        ],
        [
            A("Length and classes", "p = solution.generate_password(16)\nassert len(p) == 16\nassert any(c.isalpha() for c in p)\nassert any(c.isdigit() for c in p)\nimport string\nassert any(c in string.punctuation for c in p)"),
            A("No symbols requested", "p = solution.generate_password(12, use_symbols=False)\nimport string\nassert not any(c in string.punctuation for c in p)"),
            A("Reject short lengths", "try:\n    solution.generate_password(3)\nexcept ValueError:\n    pass\nelse:\n    raise AssertionError('expected ValueError')"),
            A("Strength rating", "assert solution.password_strength('abc') == 'weak'\nassert solution.password_strength('Abcdef12!xyz') == 'strong'"),
            A("Repeatable guarantees", "import string\nfor _ in range(40):\n    p = solution.generate_password(10)\n    assert len(p) == 10 and any(c.isdigit() for c in p) and any(c in string.punctuation for c in p)"),
        ],
        "import string\n\ndef generate_password(length, use_symbols=True):\n    pass\n\n\ndef password_strength(password):\n    pass\n",
        "You used secure randomness, enforced invariants under repetition, and validated input — habits "
        "that matter far beyond this project.", 60,
    ),
    P(
        "quiz-application", "Quiz Application", 1,
        "Grade answers and report results without printing inside your logic.",
        "A quiz needs two separate concerns: deciding whether answers are correct, and presenting the "
        "result. In this project you will keep grading pure so it can be tested with many answer sets, "
        "then add formatting and a simple command-line runner. Pay attention to case sensitivity and "
        "missing answers — real quizzes are full of them.",
        ["Compare data structures", "Normalise user answers", "Separate logic from formatting",
         "Handle missing responses"],
        ["Dictionaries", "Lists", "String methods", "Functions"],
        [
            "Define the data shape", "Answers are strings in a list, in question order. The key is a list of correct strings.",
            "Grade answers", "`grade_answers(answers, key)` returns the number of correct answers. Normalise by stripping whitespace and lowercasing both sides. Missing answers count as wrong.",
            "Format the result", "`format_result(score, total)` returns exactly `'Score: <score>/<total>'`.",
            "Add the runner", "Ask each question with `input()`, collect answers, then print the formatted result. Keep this in a `main()` function.",
        ],
        [
            "`grade_answers(answers, key)` returns an integer count; comparison is case-insensitive and ignores outer whitespace.",
            "A shorter answers list is handled without an `IndexError`.",
            "`format_result(score, total)` returns `'Score: 3/5'` style output with no extra text.",
        ],
        calls("grade_answers", [((["A", "b", "C"], ["a", "B", "C"]), 3), (([" a ", "wrong"], ["a", "b"]), 1), (([], ["a"]), 0)])
        + calls("format_result", [((3, 5), "Score: 3/5"), ((0, 0), "Score: 0/0")]),
        "def grade_answers(answers, key):\n    pass\n\n\ndef format_result(score, total):\n    pass\n\n\ndef main():\n    pass\n",
        "You normalised messy input, graded without side effects, and separated presentation from logic — "
        "a pattern every larger application uses.", 75,
    ),
]
