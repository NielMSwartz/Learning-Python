"""Coding challenges with public examples and hidden behavioural tests."""

from .helpers import A, arguments_source, assertion_for, source

CHALLENGES = []


def C(
    slug, title, level, category, difficulty, description, signature,
    function, public_cases, hidden_cases, input_spec, output_spec,
    hints, concept, points=10, extra_tests=None,
):
    examples = [
        {"input": f"{function}({arguments_source(args)})", "output": source(expected)}
        for args, expected in public_cases
    ]
    tests = [
        A(f"Example {i + 1}", assertion_for(function, args, expected))
        for i, (args, expected) in enumerate(public_cases)
    ]
    tests += [
        A(f"Hidden {i + 1}", assertion_for(function, args, expected), hidden=True)
        for i, (args, expected) in enumerate(hidden_cases)
    ]
    tests += extra_tests or []
    CHALLENGES.append(dict(
        slug=slug, title=title, level=level, category=category, difficulty=difficulty,
        description=description, signature=signature, input_spec=input_spec,
        output_spec=output_spec, examples=examples, hints=hints,
        concept_explanation=concept, tests=tests, points=points,
        starter_code=f"def {function}{signature}:\n    # your solution here\n    pass\n",
    ))


# ---------------------------------------------------------------- Level 1 ---
C("sum-of-list", "Sum of a List", 1, "Algorithms", 1,
  "Return the sum of a list of numbers. Do not use Python's built-in `sum()` — write the loop yourself.",
  "(numbers)", "sum_numbers",
  [(( [1, 2, 3],), 6), (( [],), 0)],
  [(( [-4, 4, 10],), 10), (( [2.5, 2.5],), 5.0)],
  "A list of integers or floats, possibly empty.", "A number equal to the total; 0 for an empty list.",
  ["Start with a total of zero and add each value.", "An empty list should return the starting value."],
  "Accumulator loops are the foundation of aggregation. The variable that holds the running result starts "
  "at a neutral value (0 for sums) and is updated once per item.", 10)

C("fizzbuzz", "FizzBuzz", 1, "Problem Solving", 2,
  "Return a list of strings for the numbers 1 through n: 'Fizz' for multiples of 3, 'Buzz' for multiples "
  "of 5, 'FizzBuzz' for multiples of both, and the number as a string otherwise.",
  "(n)", "fizzbuzz",
  [((5,), ["1", "2", "Fizz", "4", "Buzz"]), ((0,), [])],
  [((15,), ["1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8", "Fizz", "Buzz", "11", "Fizz", "13", "14", "FizzBuzz"]), ((3,), ["1", "2", "Fizz"])],
  "An integer n >= 0.", "A list of n strings in order.",
  ["Check divisibility by 15 before checking 3 or 5.", "The modulo operator gives the remainder after division."],
  "Order matters when multiple conditions overlap. Checking the most specific case first avoids needing "
  "string concatenation tricks.", 10)

C("reverse-string", "Reverse a String", 1, "Strings", 1,
  "Return the input string with its characters in reverse order.",
  "(text)", "reversed_text",
  [(( "hello",), "olleh"), (( "",), "")],
  [(( "Python 3.12",), "21.3 nohtyP"), (( "a",), "a")],
  "A string, possibly empty.", "The reversed string.",
  ["Slicing accepts a step: text[start:stop:step].", "A step of -1 walks backwards from the end."],
  "Python's slice notation is a compact way to copy part of a sequence. With a negative step and omitted "
  "bounds it walks the whole sequence backwards.", 5)

C("count-vowels", "Count Vowels", 1, "Strings", 1,
  "Count the vowels (a, e, i, o, u) in a string, ignoring case.",
  "(text)", "count_vowels",
  [(( "Hello",), 2), (( "Python",), 1)],
  [(( "AEIOU",), 5), (( "bcdfg",), 0), (( "",), 0)],
  "A string.", "An integer count of vowels.",
  ["Normalise the text first with lower().", "Membership in a set is concise: ch in set('aeiou')."],
  "Counting with a set of allowed characters avoids a long chain of `or` comparisons and scales to any "
  "number of characters.", 5)

C("is-palindrome", "Palindrome Check", 1, "Strings", 2,
  "Return True when a phrase reads the same forwards and backwards, ignoring case, spaces and punctuation.",
  "(text)", "is_palindrome",
  [(( "A man, a plan, a canal: Panama",), True), (( "hello",), False)],
  [(( "Never odd or even",), True), (( "",), True), (( "racecar",), True)],
  "A string containing letters, digits and punctuation.", "A boolean.",
  ["str.isalnum() identifies letters and digits.", "Build a cleaned version before comparing it with its reverse."],
  "Normalisation separates presentation from the comparison. Filtering first makes the palindrome rule "
  "simple: cleaned == cleaned[::-1].", 10)

C("max-difference", "Maximum Difference", 1, "Algorithms", 2,
  "Return the difference between the largest and smallest numbers in a list, or 0 for an empty list.",
  "(numbers)", "max_difference",
  [(( [3, 1, 9, 4],), 8), (( [],), 0)],
  [(( [-5, -2, -10],), 8), (( [7],), 0)],
  "A list of numbers, possibly empty.", "A number >= 0.",
  ["Handle the empty list before calling min() or max().", "min() and max() work on any non-empty iterable."],
  "Guard clauses keep special cases out of the main logic. Here an early return prevents min() from "
  "raising on an empty sequence.", 10)

# ---------------------------------------------------------------- Level 2 ---
C("anagrams", "Anagram Check", 2, "Strings", 2,
  "Return True when two strings contain exactly the same characters in a different order. Ignore case and spaces.",
  "(left, right)", "are_anagrams",
  [(( "listen", "silent"), True), (( "hello", "world"), False)],
  [(( "Dormitory", "dirty room"), True), (( "a", "a "), True), (( "abc", "abcc"), False)],
  "Two strings.", "A boolean.",
  ["Sorting both strings gives a simple comparison.", "Counting characters with a Counter also works."],
  "Sorting is O(n log n); counting with collections.Counter is O(n). Both are correct — think about which "
  "one you would choose for very long strings.", 10)

C("flatten-list", "Flatten a Nested List", 2, "Data Structures", 2,
  "Flatten an arbitrarily nested list of integers into a single list preserving order.",
  "(values)", "flatten",
  [(( [1, [2, [3]], 4],), [1, 2, 3, 4]), (( [],), [])],
  [(( [[[]]],), []), (( [1, [], [2, [3, 4]]],), [1, 2, 3, 4])],
  "A list whose elements are integers or lists of integers.", "A flat list of integers.",
  ["Check isinstance(item, list) and recurse.", "A recursive function calls itself with a smaller input."],
  "Recursion is natural for nested structures. Every recursive solution needs a base case — here, "
  "iterating an empty list simply produces nothing.", 15)

C("word-frequency", "Word Frequency", 2, "Data Structures", 2,
  "Count how often each word appears in a string. Treat words as lowercase, ignore punctuation, and split on whitespace.",
  "(text)", "word_frequency",
  [(( "one two two",), {"one": 1, "two": 2}), (( "",), {})],
  [(( "Hello, hello! WORLD",), {"hello": 2, "world": 1}), (( "a a a b",), {"a": 3, "b": 1})],
  "A string of words separated by whitespace.", "A dictionary mapping lowercase words to counts.",
  ["str.translate or a small character filter can remove punctuation.", "dict.get(key, 0) lets you increment a missing key."],
  "Tokenisation plus a counter is the standard shape of text analysis. Normalise tokens before counting "
  "so 'Hello' and 'hello' are one word.", 15)

C("running-total", "Running Total", 2, "Algorithms", 2,
  "Given a list of numbers, return a new list where each position contains the total up to and including that position.",
  "(numbers)", "running_total",
  [(( [1, 2, 3],), [1, 3, 6]), (( [],), [])],
  [(( [-1, 5, 2],), [-1, 4, 6]), (( [10],), [10])],
  "A list of numbers.", "A list of the same length containing cumulative totals.",
  ["Keep a total variable and append after each addition.", "The first value is the total after one step."],
  "Prefix sums turn repeated range-sum questions into constant-time lookups. This is a small but widely "
  "used algorithmic pattern.", 10)

C("unique-in-order", "Unique Values in Order", 2, "Data Structures", 2,
  "Remove duplicates from a list while preserving the order of first appearance.",
  "(items)", "unique_in_order",
  [(( [3, 1, 3, 2, 1],), [3, 1, 2]), (( [],), [])],
  [(( ["a", "b", "a", "c", "b"],), ["a", "b", "c"]), (( [1, 1, 1],), [1])],
  "A list of hashable values.", "A list with duplicates removed, first occurrences kept.",
  ["A set tracks what you have already seen.", "Appending to a result list preserves order."],
  "Combining a set for membership with a list for ordering gives O(n) deduplication — better than "
  "checking `if item not in result` for every item.", 10)

C("caesar-cipher", "Caesar Cipher", 2, "Strings", 3,
  "Shift each letter of a string by a fixed number of positions through the alphabet, wrapping from z to a. "
  "Preserve case and leave non-letters unchanged.",
  "(text, shift)", "caesar",
  [(( "abc", 1), "bcd"), (( "Xyz", 3), "Abc")],
  [(( "hello, world!", 13), "uryyb, jbeyq!"), (( "abc", 26), "abc"), (( "abc", -1), "zab")],
  "A string and an integer shift (may be negative or larger than 26).", "The shifted string.",
  ["Normalise the shift with the modulo operator.", "char.isupper() and ord()/chr() let you build the new letter."],
  "Character arithmetic with ord() and chr() works because letters have consecutive Unicode code points. "
  "Modulo handles wrapping and negative shifts.", 15)

# ---------------------------------------------------------------- Level 3 ---
C("two-sum", "Two Sum", 3, "Algorithms", 3,
  "Return the indices of two numbers that add up to a target. Assume exactly one answer exists and each input "
  "has at most one solution. Return the indices in ascending order.",
  "(numbers, target)", "two_sum",
  [(( [2, 7, 11, 15], 9), [0, 1]), (( [3, 2, 4], 6), [1, 2])],
  [(( [3, 3], 6), [0, 1]), (( [-1, -2, -3, -4], -7), [2, 3]), (( [0, 4, 3, 0], 0), [0, 3])],
  "A list of integers and an integer target.", "A list of two indices in ascending order.",
  ["Store each number and its index in a dictionary as you scan.", "Check whether target - number is already in the dictionary before inserting."],
  "The one-pass hash-map solution trades memory for speed: O(n) time instead of the O(n²) nested-loop "
  "approach.", 20)

C("balanced-brackets", "Balanced Brackets", 3, "Data Structures", 3,
  "Return True when every bracket in a string is correctly paired and nested. Support (), [] and {}.",
  "(text)", "is_balanced",
  [(( "(a + b)",), True), (( "([)]",), False)],
  [(( "",), True), (( "{[()]}",), True), (( "(((",), False), (( "())",), False)],
  "A string possibly containing brackets and other characters.", "A boolean.",
  ["A stack tracks the opening brackets you have seen.", "When you meet a closing bracket, it must match the most recent opening one."],
  "Stacks model nested structure: the last opener must be the first closed. This pattern appears in "
  "parsers, expression evaluators and HTML validation.", 20)

C("merge-intervals", "Merge Intervals", 3, "Algorithms", 4,
  "Merge overlapping intervals and return a sorted list of non-overlapping intervals. Touching intervals "
  "(end == next start) count as overlapping.",
  "(intervals)", "merge_intervals",
  [(( [(1, 3), (2, 6), (8, 10), (15, 18)],), [(1, 6), (8, 10), (15, 18)]), (( [],), [])],
  [(( [(1, 4), (4, 5)],), [(1, 5)]), (( [(2, 3), (1, 10)],), [(1, 10)]), (( [(1, 2)],), [(1, 2)])],
  "A list of (start, end) tuples in any order.", "A list of merged tuples sorted by start.",
  ["Sort by the start value first.", "Keep the current interval and extend its end while the next start is <= that end."],
  "Sorting plus a single sweep turns a seemingly complex problem into a linear scan. Choose the interval "
  "end carefully: max(previous_end, next_end) is safer than always taking next_end.", 25)

C("longest-unique-substring", "Longest Unique Substring", 3, "Strings", 4,
  "Return the length of the longest contiguous substring with no repeated characters.",
  "(text)", "longest_unique",
  [(( "abcabcbb",), 3), (( "bbbbb",), 1)],
  [(( "",), 0), (( "pwwkew",), 3), (( "abcdef",), 6)],
  "A string.", "An integer length.",
  ["Use a sliding window with a start pointer and a dictionary of last-seen positions.", "When a character repeats, jump the start just past its previous position."],
  "The sliding-window technique keeps a window that satisfies a rule and moves its boundaries instead of "
  "rechecking every substring. It runs in O(n).", 25)

C("binary-search", "Binary Search", 3, "Algorithms", 3,
  "Return the index of a target in a sorted list, or -1 when it is absent. Implement the search yourself.",
  "(numbers, target)", "binary_search",
  [(( [1, 3, 5, 7, 9], 7), 3), (( [1, 3, 5], 2), -1)],
  [(( [], 1), -1), (( [5], 5), 0), (( [1, 2, 3, 4], 1), 0), (( [1, 2, 3, 4], 4), 3)],
  "A sorted list of numbers and a target number.", "The target index, or -1.",
  ["Track low and high indices.", "Stop when low > high; otherwise compare the middle value."],
  "Binary search halves the search space each step, giving O(log n). The classic bug is an infinite loop "
  "from not moving low or high past the midpoint.", 20)

C("group-anagrams", "Group Anagrams", 3, "Data Structures", 4,
  "Group words that are anagrams of each other. Return a dictionary where each key is the sorted letters of "
  "the group and each value is the list of words from the input, in input order.",
  "(words)", "group_anagrams",
  [(( ["eat", "tea", "tan"],), {"aet": ["eat", "tea"], "ant": ["tan"]}), (( [],), {})],
  [(( ["", ""],), {"": ["", ""]}), (( ["a", "b", "a"],), {"a": ["a", "a"], "b": ["b"]})],
  "A list of lowercase strings.", "A dictionary of sorted-letter keys to word lists.",
  ["sorted(word) produces a canonical key for anagrams.", "Use setdefault or defaultdict(list) to append to a group."],
  "Choosing a canonical representation lets a hash map do the grouping in O(n·k), where k is word length. "
  "This 'normalise then group' pattern is everywhere in data processing.", 25)

# ---------------------------------------------------------------- Level 4 ---
C("most-frequent-k", "Most Frequent K", 4, "Algorithms", 4,
  "Return the k most frequent values from a list, ordered by frequency descending and then by first "
  "appearance for ties.",
  "(items, k)", "most_frequent_k",
  [(( ["a", "b", "a", "c", "b", "a"], 2), ["a", "b"]), (( [], 3), [])],
  [(( ["x", "y", "x", "y"], 2), ["x", "y"]), (( ["b", "a", "b", "a"], 1), ["b"]), (( ["a"], 0), [])],
  "A list of hashable values and a non-negative integer k.", "A list of up to k values.",
  ["Count frequencies and remember the first index of each value.", "sorted() accepts a key tuple and reverse=True."],
  "Stable tie-breaking requires keeping extra information (first index) in the sort key. Python's sort is "
  "stable, but explicit keys make the rule unambiguous.", 25)

C("rotate-matrix", "Rotate Matrix", 4, "Algorithms", 4,
  "Return a new matrix rotated 90 degrees clockwise. Do not mutate the input.",
  "(matrix)", "rotate_matrix",
  [(( [[1, 2], [3, 4]],), [[3, 1], [4, 2]]), (( [[1]],), [[1]])],
  [(( [[1, 2, 3], [4, 5, 6]],), [[4, 1], [5, 2], [6, 3]]), (( [],), [])],
  "A list of equally sized rows (or an empty list).", "A new rotated list of rows.",
  ["The rotated row i is the column i of the original read bottom to top.", "zip(*matrix) transposes rows and columns."],
  "A transpose followed by reversing each row gives a 90-degree rotation. Building a new matrix avoids "
  "aliasing bugs from mutating the input in place.", 25)

C("top-k-scores", "Top K Scores", 4, "Algorithms", 3,
  "Return the k highest unique scores in descending order.",
  "(scores, k)", "top_k_scores",
  [(( [10, 5, 20, 5, 15], 2), [20, 15]), (( [], 3), [])],
  [(( [1, 2, 3], 5), [3, 2, 1]), (( [4, 4, 4], 1), [4]), (( [1, 2], 0), [])],
  "A list of numbers and a non-negative integer k.", "A list of the k largest distinct numbers.",
  ["Convert to a set to remove duplicates.", "sorted(..., reverse=True) then slice."],
  "Removing duplicates before sorting makes the contract clear. For huge datasets a heap "
  "(`heapq.nlargest`) avoids sorting everything.", 20)

C("can-transform", "Word Transformation", 4, "Problem Solving", 5,
  "Given a start word, a target word and a set of valid words, return True when you can transform start into "
  "target by changing one letter at a time, with every intermediate word in the set.",
  "(start, target, words)", "can_transform",
  [(( "hit", "cog", {"hot", "dot", "dog", "lot", "log", "cog"}), True),
   (( "hit", "cog", {"hot", "dot", "dog", "lot", "log"}), False)],
  [(( "a", "c", {"a", "b", "c"}), True), (( "a", "d", {"a", "b", "c"}), False),
   (( "same", "same", set()), True)],
  "Two equal-length strings and an iterable of valid words.", "A boolean.",
  ["Build a graph of words differing by one letter — or generate neighbours on the fly.", "Breadth-first search finds whether a path exists."],
  "BFS explores shortest paths first and stops as soon as the target is found. Generating neighbours by "
  "trying each position and each letter avoids an expensive all-pairs comparison.", 30)

C("allow-request", "Rate Limiter", 4, "System Design", 4,
  "A request is allowed when fewer than `limit` requests from the same client occurred in the last `window` "
  "seconds (strictly greater than now - window). Given the list of past timestamps, return True if a new "
  "request at `now` is allowed.",
  "(timestamps, now, limit, window)", "allow_request",
  [(( [1, 2, 3], 4, 3, 10), False), (( [1, 2], 12, 3, 10), True)],
  [(( [], 100, 1, 5), True), (( [96, 97, 98], 100, 3, 5), False), (( [90, 91, 92], 100, 3, 5), True)],
  "A list of numeric timestamps, the current timestamp, a positive limit and a positive window.", "A boolean.",
  ["Filter the timestamps to those inside the window before counting.", "The boundary is exclusive: timestamp > now - window."],
  "Rate limiting is a real system-design primitive. A pure function lets you test boundary conditions — "
  "off-by-one errors here can block legitimate users or allow abuse.", 25)

C("simplify-path", "Simplify a Unix Path", 4, "Problem Solving", 4,
  "Return the canonical version of an absolute POSIX path: collapse repeated slashes, resolve '.' and '..', "
  "and keep the result rooted at '/'.",
  "(path)", "simplify_path",
  [(( "/a/b/../c",), "/a/c"), (( "/a//b/./c/",), "/a/b/c")],
  [(( "/",), "/"), (( "/../../a",), "/a"), (( "/a/../../b",), "/b"), (( "",), "/")],
  "An absolute POSIX path string.", "The simplified absolute path string.",
  ["Split on '/' and treat empty and '.' segments as no-ops.", "Use a list as a stack; '..' pops only when the stack is non-empty."],
  "Path normalisation is a stack problem with explicit rules for the root boundary. The same pattern "
  "appears in URL routers and file-sandbox implementations.", 25)
