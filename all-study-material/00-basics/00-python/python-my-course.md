<!--
Source: python-my-course.html
Title: Python My Course | TechToday
Description: Fast-track Python essentials for everyday programming — variables, type hints, keywords, strings, operators, loops, lists, dictionaries, sorting, tuples, sets, unpacking & destructuring, comprehensions, functions, async/await, OOP, error handling, modules & imports, and virtual environments.
-->

Navigation: [TechToday](../../../index.html) · [← Programming Languages](../programming-languages.html)

<a id="python-my-course"></a>

# Python My Course

The high-yield Python course reference: common everyday syntax, type hints, keywords, core collections, functions, async/await concurrency, practical OOP solutions, error handling, modules & imports, and virtual environments.

<a id="table-of-contents"></a>

## Table of Contents

1. [Variables, Types & Casting](#1-variables-types-and-casting)
2. [Type Hints](#2-type-hints)
3. [Keywords in Python](#3-keywords-in-python)
4. [Everyday Error Handling](#4-everyday-error-handling)
5. [Everyday String Operations](#5-everyday-string-operations)
6. [Operators, Truthiness & Conditionals](#6-operators-truthiness-and-conditionals)
7. [Loops & Iteration](#7-loops-and-iteration)
8. [Lists & Slicing](#8-lists-and-slicing)
9. [Dictionaries](#9-dictionaries)
10. [Tuples & Sets](#10-tuples-and-sets)
11. [Sorting in Python](#11-sorting-in-python)
12. [Unpacking & Destructuring](#12-unpacking-and-destructuring)
13. [List Comprehensions](#13-list-comprehensions)
14. [Functions & Arguments](#14-functions-and-arguments)
15. [Async / Await](#15-async-and-await)
16. [Object-Oriented Programming (OOP)](#16-object-oriented-programming)
17. [Modules & Imports](#17-modules-and-imports)
18. [Virtual Environments](#18-virtual-environments)

---

<a id="unit-1"></a>

## Unit 1 — Daily Syntax & Logic

The daily syntax: declaring variables, type hints, reserved keywords, error handling, strings, operators, truthiness, and loops.

<a id="1-variables-types-and-casting"></a>

## 1. Variables, Types & Casting

- **Core Primitives** `str, int, float, bool, None` <!-- great -->
- **Type Conversion** `Explicit casting functions` <!-- great -->
- **Type Checking** `isinstance(val, type)` <!-- good -->

In Python, variables are names that point to values in memory. You don't specify variable types when declaring them; Python figures out the type automatically at runtime. Converting between types is done explicitly with functions like `str()`, `int()`, `float()`, and `bool()`.

> **Analogy** 🎬
>
> **Picture it — Sticky Notes on Jars**
>
> A variable is simply a sticky note label you slap onto a jar. If you write `count = 5`, the label `count` is stuck to a jar holding the number 5. You can move that label to another jar anytime (`count = "five"`).

Key everyday functions:
1. `type(x)`: Returns the type of variable `x`
2. `isinstance(x, int)`: Returns `True` if `x` is an integer (preferred over `type(x) == int`)
3. `int("42")`: Converts string to integer (throws `ValueError` if text is not numeric)
4. `float("3.14")`: Converts string to floating-point number
5. `str(100)`: Converts any value into its string representation
6. `bool(x)`: Converts value to `True` or `False`

```python
# Variables
user_name = "Pankaj"
user_age = 30
user_height = 5.10
user_active = True
user_session = None
print(f"\nUser details are as follows: \nName: {user_name}, Age: {user_age}, Height: {user_height}\n")
# User details are as follows: 
# Name: Pankaj, Age: 30, Height: 5.1

# Types
print(f"user_name: {type(user_name)}")        # user_name: <class 'str'>
print(f"user_age: {type(user_age)}")          # user_age: <class 'int'>
print(f"user_height: {type(user_height)}")    # user_height: <class 'float'>
print(f"user_active: {type(user_active)}")    # user_active: <class 'bool'>
print(f"user_session: {type(user_session)}")  # user_session: <class 'NoneType'>

# Type Conversion
print(str(user_age), type(str(user_age)))          # "30" <class 'str'>
print(int(user_height), type(int(user_height)))    # 5 <class 'int'>
print(float(user_age), type(float(user_age)))      # 30.0 <class 'float'>
print(bool(user_session), type(bool(user_session))) # False <class 'bool'>

# Recommended type checking
if isinstance(user_age, int):
    print("user_age is an integer")  # user_age is an integer
```

- **Strength — Fast Prototyping** Dynamic typing lets you assign and manipulate values without repetitive type declarations.
- **Weakness — Runtime Type Mismatches** Adding incompatible types like `"Score: " + 10` raises a `TypeError` at runtime instead of converting automatically.

**Interview question**

*Given a mixed list of values containing numbers, numeric strings, and non-numeric strings, compute the sum of all valid integers.*

Iterate over the list, try converting each value to an integer using `int()`, and add valid integers to a running total while ignoring invalid inputs.

**Answer — Sum Valid Integers**

```python
def sum_valid_integers(items: list) -> int:
    total = 0
    for item in items:
        try:
            total += int(item)
        except (ValueError, TypeError):
            continue
    return total

# Test cases
print(sum_valid_integers([10, "20", "abc", 5, None, "30"]))  # 65
print(sum_valid_integers(["1", "2", "3"]))                    # 6
print("Sum valid integers passed!")  # Sum valid integers passed!
```

> **Key idea**
>
> To check an object's type, always use `isinstance(obj, ExpectedType)` rather than comparing `type(obj) == ExpectedType`.

---

<a id="2-type-hints"></a>

## 2. Type Hints

- **Variable & Return Hints** `x: int = 1, def fn() -> str:` <!-- great -->
- **Built-in Generics (3.9+)** `list[str], dict[str, int]` <!-- great -->
- **Union & Optional (3.10+)** `str | None, int | float` <!-- good -->

Python is dynamically typed, but modern Python (PEP 484 and Python 3.9+) supports **type hints** (type annotations). Type hints do not change runtime behavior—Python will not throw an error if types don't match—but they make code self-documenting, provide rich IDE autocomplete, and allow static analysis tools like `mypy` or `pyright` to catch bugs before runtime.

> **Analogy** 🎬
>
> **Picture it — Blueprint Annotations on Plumbing Pipes**
>
> Without type hints, all pipes in a building look identical from the outside; water, gas, or electrical wiring could be routed through any pipe until something leaks or sparks at runtime. Adding type hints is like stenciling labels on the pipes ("Cold Water Only", "Natural Gas", "Max 120V"). The pipes still carry whatever is pumped through them, but inspectors (static type checkers) and technicians (your IDE) immediately catch dangerous mismatches before opening the valve.

Key everyday concepts and syntax:
1. Basic variable annotations: `name: str = "Pankaj"`, `age: int = 30`, `is_active: bool = True`
2. Function parameter and return types: `def greet(name: str) -> str:` and `def process() -> None:`
3. Built-in generic collections (Python 3.9+): `list[int]`, `dict[str, str]`, `set[int]`, `tuple[float, float]` directly without importing from `typing`
4. Modern Union and Optional syntax (Python 3.10+): `int | str`, `int | None` replaces legacy `Union[int, str]` and `Optional[int]`
5. Type Aliases (Python 3.12+): `Point = tuple[float, float]` to give meaningful names to complex composite types
6. Specialized types from `typing`: `Callable[[int], int]` (function arguments), `Literal["json", "text"]` (exact allowed values)

```python
from __future__ import annotations
from typing import Callable, Any, Literal

## 1. Basic variable annotations
user_name: str = "Pankaj"
user_age: int = 30
user_height: float = 5.10
user_active: bool = True
user_session: None = None

## 2. Basic function annotations
# Function return type annotation
def greet(name: str) -> str:
    return f"Hello, {name}!"
print(greet("Pankaj"))  # Hello, Pankaj!

# Function with no return value annotation
def process() -> None:
    print("Processing...")  # Processing...
process()

## 3. Built-in collection and generic type annotations (Python 3.9+)
numbers: list[int] = [1, 2, 3, 4, 5]
user_info: dict[str, str] = {"name": "Pankaj", "city": "New York"}
coordinates: tuple[float, float] = (40.7128, 74.0060)
unique_numbers: set[int] = {1, 2, 3, 4, 5}

## 4. Union and optional type annotations (Python 3.10+)
value: int | str = 42
value = "Hello"
optional_value: int | None = None

## 5. Type alias to give meaningful names to complex composite types
Point = tuple[float, float]
location: Point = (40.7128, 74.0060)

## 6. Literal and Callable type annotations
def find_user(user_id: int, format: Literal["json", "text"] = "json") -> dict[str, str] | None:
    if user_id == 101:
        return {"name": "Alice", "role": "engineer"}
    return None

def apply_operation(values: list[int], operation: Callable[[int], int]) -> list[int]:
    return [operation(x) for x in values]

squared = apply_operation([1, 2, 3], lambda x: x ** 2)
print(squared)  # [1, 4, 9]

user = find_user(101)
if user is not None:
    print(f"Found: {user['name']}")  # Found: Alice
```

- **Strength — Catch Bugs Early & Instant IDE Autocomplete** Static analysis tools catch `NoneType` errors, wrong argument counts, and invalid types before code runs, while IDEs provide instant auto-completion and safe refactoring.
- **Weakness — No Runtime Validation by Default** Type hints are ignored by Python's runtime interpreter; passing an integer where a string is annotated will not raise an exception unless explicitly checked with `isinstance()` or Pydantic.

**Interview question**

*Write a type-annotated function `parse_record(raw: dict[str, Any]) -> tuple[str, int, float] | None` that safely validates and extracts a user's name (`str`), age (`int`), and account balance (`float`). If any key is missing or conversion fails, return `None`.*

Access required dictionary keys inside a `try / except (KeyError, ValueError, TypeError)` block, cast each field to its expected type, and return the validated tuple. Return `None` if an exception occurs.

**Answer — Validate and Parse Record**

```python
from typing import Any

def parse_record(raw: dict[str, Any]) -> tuple[str, int, float] | None:
    try:
        name = str(raw["name"])
        age = int(raw["age"])
        balance = float(raw["balance"])
        return (name, age, balance)
    except (KeyError, ValueError, TypeError):
        return None

# Test cases
record_ok = {"name": "Charlie", "age": "29", "balance": "150.50"}
parsed = parse_record(record_ok)
print(parsed)  # ('Charlie', 29, 150.5)

record_bad = {"name": "Bob", "balance": "invalid"}
print(parse_record(record_bad))  # None

empty_record = {}
print(parse_record(empty_record))  # None
print("Parse record with type hints passed!")  # Parse record with type hints passed!
```

> **Key idea**
>
> Type hints do not enforce types at runtime. Use tools like `mypy` or `ruff` in your CI pipeline, and use validation libraries like Pydantic when handling untrusted user input.

---

<a id="3-keywords-in-python"></a>

## 3. Keywords in Python

- **Core Reserved Words** `35 keywords in keyword.kwlist` <!-- great -->
- **Control & Logic** `if, for, while, def, return, and, or` <!-- great -->
- **Inspection & Testing** `import keyword; keyword.iskeyword()` <!-- good -->

Python keywords are special reserved words that have predefined meanings and purposes within the language. Because they define the syntax and structure of Python programs, they cannot be used as identifiers (such as names for variables, functions, or classes). Doing so triggers a `SyntaxError`. Keywords are strictly case-sensitive (e.g. `True` is a keyword, but `true` is not), and they are always available built-in without needing to be imported.

> **Analogy** 🎬
>
> **Picture it — Traffic Control Signs on City Roads**
>
> Keywords are like official municipal traffic signs: STOP, ONE WAY, DO NOT ENTER, SPEED LIMIT, YIELD. A resident cannot paint their mailbox to look like a STOP sign or use traffic sign words as a street name because the traffic system relies on them having fixed, unambiguous rules. When Python's parser sees `def`, `if`, `while`, or `return`, it knows exactly what grammar rule to enforce without hesitation.

### Classification of Python Keywords

Python features 35 standard keywords and a few soft keywords (such as `match`, `case`, `_`, and `type`, which act as keywords only in specific contexts like pattern matching or type statements, while remaining valid variable names elsewhere). They are grouped by their functionality:

1. **Value Keywords (`True`, `False`, `None`):** Represent boolean states and the absence of a value (singletons).
2. **Control Flow (`if`, `elif`, `else`):** Used for conditional branching logic.
3. **Loops & Iteration (`for`, `while`, `break`, `continue`, `pass`):** Manage loops, exit loops prematurely (`break`), skip to the next iteration (`continue`), or provide null placeholders (`pass`).
4. **Logical Operators (`and`, `or`, `not`):** Standard boolean operators used to evaluate expressions.
5. **Structural & Definitions (`def`, `class`, `lambda`, `return`, `yield`):** Define functions, classes, anonymous functions, and manage return output or generator streams.
6. **Exception Handling (`try`, `except`, `finally`, `raise`, `assert`):** Intercept and manage runtime errors, run debug assertions (`assert`), and guarantee cleanup (`finally`).
7. **Namespace & Scope (`global`, `nonlocal`, `del`):** Alter variable scope rules or delete objects and variable bindings (`del`).
8. **Imports (`import`, `from`, `as`):** Pull in external modules, selective functions, or create shorthand aliases.
9. **Pattern & Identity (`in`, `is`):** Check for membership inside collections or evaluate object identity in memory.
10. **Context & Concurrency (`with`, `async`, `await`):** Clean up resource allocations (context managers) and write asynchronous, non-blocking coroutines.

```python
import keyword

# 1. Inspecting reserved and soft keywords dynamically
print(f"All standard keywords: {keyword.kwlist}")
# All standard keywords: ['False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await', 'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except', 'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try', 'while', 'with', 'yield']
print(f"Total standard keywords: {len(keyword.kwlist)}")      # 35
print(f"Soft keywords: {keyword.softkwlist}")                # ['_', 'case', 'match', 'type']

# 2. Checking if a string is a keyword
print(f"Is 'def' a keyword? {keyword.iskeyword('def')}")     # True
print(f"Is 'match' a keyword? {keyword.iskeyword('match')}") # False (soft keyword)
print(keyword.iskeyword('True'))                             # True
print(keyword.iskeyword('true'))                             # False

# 3. Checking if a string is a soft keyword
print(keyword.issoftkeyword('case'))                         # True
print(keyword.issoftkeyword('def'))                          # False

# 4. Handling keyword collisions with trailing underscore
class_name = "Mathematics"
type_ = "geometry"
print(f"Variables: {class_name}, {type_}")  # Variables: Mathematics, geometry
```

- **Strength — Compact, Readable Grammar** Python's concise keyword vocabulary reads like structured English, making control flow, error handling, and asynchronous code predictable and readable.
- **Weakness — SyntaxError on Keyword Identifiers** Attempting to name a variable or JSON key after a keyword (e.g. `class = "math"` or `def = 5`) causes a fatal `SyntaxError`. In such cases, append a trailing underscore by convention (e.g. `class_ = "math"`).

> **Key idea**
>
> Python has 35 reserved keywords and a few context-sensitive soft keywords (`match`, `case`, `_`, `type`). Standard keywords can never be used as variable, function, or class names. Use `keyword.iskeyword(name)` to verify programmatically, and append a trailing underscore (such as `class_` or `type_`) if you need to name a variable after a keyword.

---

<a id="4-everyday-error-handling"></a>

## 4. Everyday Error Handling

- **Try / Except** `Catch specific exceptions safely` <!-- great -->
- **Common Errors** `ValueError, KeyError, FileNotFoundError` <!-- great -->
- **Cleanup** `finally block always runs` <!-- good -->

Errors happen: an API returns bad text, a user types letters into a number field, or a file doesn't exist. Python uses `try / except` blocks so your program handles errors gracefully instead of crashing abruptly.

> **Analogy** 🎬
>
> **Picture it — A Gymnast's Safety Net**
>
> The code inside `try:` is the gymnast performing high on the trapeze. If they perform the routine smoothly, they finish and dismount. If they slip (an error occurs), the `except:` safety net catches them safely so nobody gets hurt.

Key patterns:
1. `try ... except ValueError as e:`: Catches specific conversion errors
2. `except (KeyError, IndexError):`: Catches multiple possible lookup errors
3. `except Exception as e:`: Fallback for unexpected errors
4. `finally:`: Code that is guaranteed to run (e.g. closing connections)
5. `raise ValueError("Invalid value")`: Manually triggers an error

```python
from __future__ import annotations

# 1. Parsing with error handling (get_age)
def get_age(age: str) -> int | None:
    try:
        return int(age)
    except ValueError as e:
        print("Cant covert age to int")  # Cant covert age to int

print(f"get_age: {get_age('40')}")       # get_age: 40
print(f"get_age: {get_age('fourty')}")   # get_age: None

# 2. Dictionary key lookups with default fallback (get_retries)
def get_retries(data: dict) -> int | None:
    try:
        return data["retries"]
    except KeyError:
        return 3

print(f"get_retries: {get_retries({'retries': 5})}")  # get_retries: 5
print(f"get_retries: {get_retries({})}")               # get_retries: 3

# 3. Catching multiple lookup errors (KeyError, IndexError)
items = [10, 20]
try:
    val = items[5]
except (KeyError, IndexError) as err:
    print(f"Lookup failed: {err}")  # Lookup failed: list index out of range

# 4. Cleanup with finally block and manual raise
def parse_percentage(val: str) -> float:
    try:
        num = float(val)
        if num < 0 or num > 100:
            raise ValueError(f"Percentage out of range: {num}")
        return num
    finally:
        print("Parsing completed.")  # Parsing completed.

print(parse_percentage("85.5"))  # 85.5
```

- **Strength — Prevents Application Crashes** Catching specific errors lets services log failures and return fallback responses without taking down the server.
- **Weakness — Bare `except: pass` Anti-pattern** Writing `except: pass` silences every error, including keyboard interrupts and variable typos, making debugging impossible.

**Interview question**

*Write a function that safely divides two numbers and returns None if division by zero occurs.*

Wrap the division operation `a / b` inside a `try / except ZeroDivisionError` block.

**Answer — Safe Division**

```python
def safe_divide(a: float, b: float):
    try:
        return a / b
    except ZeroDivisionError:
        return None

# Test cases
print(safe_divide(10, 2))  # 5.0
print(safe_divide(5, 0))   # None
print(safe_divide(0, 5))   # 0.0
print("Safe divide passed!")  # Safe divide passed!
```

> **Key idea**
>
> Always specify the error you expect to catch (such as `except ValueError:`, not just `except:`).

---

<a id="5-everyday-string-operations"></a>

## 5. Everyday String Operations

- **Formatting & Operators** `f"{var}", +, *, in, not in` <!-- great -->
- **Whitespace & Cleaning** `.strip(), .split(), .join()` <!-- great -->
- **Search & Inspection** `.replace(), .startswith(), in` <!-- good -->

Strings are one of the most commonly used data types in Python. Python strings are immutable (they cannot be changed in place; operations return a new string). Formatted string literals (f-strings) are the modern, standard way to embed variables and expressions inside text. Python also provides native string operators like `+` for concatenation, `*` for repetition, and the membership operators `in` and `not in` to test for substrings.

> **Analogy** 🎬
>
> **Picture it — A Template Letter with Fill-in Blanks**
>
> An f-string `f"Hello {name}, your total is ${price:.2f}"` is like a printed letter with blank brackets. Python reads the variables, formats them directly into the blanks, and produces the final letter in a single pass. The `in` operator is like using Ctrl+F on the document to quickly see if a keyword appears anywhere on the page.

Most commonly used string methods and operators:
1. `f"{name}"`: Embeds variable or expression inside text (f-strings)
2. `f"{price:.2f}"`: Formats float with 2 decimal places
3. Membership operators `in` and `not in`: Substring checks (`"@" in email`, `"admin" not in roles`)
4. String operators `+` and `*`: Concatenation (`first + " " + last`) and repetition (`"=" * 30`)
5. Safe identity check: `if text is None:` or `if text is not None:` (never use `text is ""` or `text is "hello"`)
6. `s.strip()`: Trims leading and trailing spaces or newlines
7. `s.split(",")`: Splits a string by delimiter into a list of strings
8. `", ".join(list_of_strings)`: Joins a list of strings into one string
9. `s.lower()` and `s.upper()`: Changes text casing
10. `s.replace(old, new)`: Replaces occurrences of a substring
11. `s.startswith(prefix)` and `s.endswith(suffix)`: Checks prefix or suffix

```python
# 1. Modern f-strings and string operators (+, *)
product = "Coffee Mug"
price = 12.994
print(f"Item: {product} | Cost: ${price:.2f}")  # Item: Coffee Mug | Cost: $12.99

divider = "=" * 30
header = "[ " + product.upper() + " ]"
print(f"{header}\n{divider}")
# [ COFFEE MUG ]
# ==============================

# 2. Membership operators (in and not in)
user_email = "alex@company.com"
if "@" in user_email and "." in user_email:
    print("Valid email structure.")  # Valid email structure.

if "admin" not in user_email:
    print("Standard user account.")  # Standard user account.

# 3. Cleaning user inputs
raw_email = "   Alex@Company.COM \n"
clean_email = raw_email.strip().lower()
print(clean_email)  # alex@company.com

# 4. Splitting and joining
csv_row = "laptop,electronics,999"
parts = csv_row.split(",")
print(parts)  # ['laptop', 'electronics', '999']

joined = " -> ".join(parts)
print(joined)  # laptop -> electronics -> 999

# 5. Substring replacement and prefix/suffix checks
sentence = "Hello World"
print(sentence.replace("World", "Python"))  # Hello Python
print(sentence.startswith("Hello"))         # True
print(sentence.endswith("World"))           # True

# 6. Safe None check vs value equality
user_input = None
if user_input is None:
    print("No input provided.")  # No input provided.

# Value equality vs identity
status = "active"
print(status == "active")  # True (always use == for string comparisons)
```

- **Strength — Clean F-strings & Native Operators** F-strings and operators like `in`, `+`, and `*` make text formatting, substring search, and visual dividers clean and readable without helper functions.
- **Weakness — Passing None to String Methods** Calling `.strip()` or `.lower()` on a variable that happens to be `None` throws an `AttributeError`. Always check `if val is not None:` first.

**Interview question**

*Write a function that normalizes a full name by removing extra spaces and capitalizing each word.*

Use `s.split()` to automatically split words by any amount of consecutive whitespace, title-case each word with `.capitalize()`, and re-join with a single space.

**Answer — Normalize Name**

```python
def normalize_name(raw_name: str) -> str:
    if raw_name is None:
        return ""
    words = raw_name.split()
    return " ".join(w.capitalize() for w in words)

# Test cases
print(normalize_name("  alex   MORGAN  "))  # Alex Morgan
print(normalize_name("john"))                # John
print(repr(normalize_name("   ")))           # ''
print(repr(normalize_name(None)))            # ''
print("Normalize name passed!")  # Normalize name passed!
```

> **Key idea**
>
> Use the `in` and `not in` operators for fast substring membership checks (`"@" in email`). When checking whether a string variable is missing, always check `if s is None:`. For comparing string values, always use `==` and `!=` (never `is` or `is not`).

---

<a id="6-operators-truthiness-and-conditionals"></a>

## 6. Operators, Truthiness & Conditionals

- **Division & Remainder** `/, //, %, divmod()` <!-- great -->
- **Identity & Membership** `is, is not, in, not in` <!-- great -->
- **Logic & Chaining** `and, or, not, 18 <= age < 65` <!-- good -->

Python features rich, expressive operators across several key categories:
- **True Division (`/`), Floor Division (`//`), and Modulo (`%`):** `/` always produces a floating-point result (`10 / 2 == 5.0`). `//` divides and truncates down towards negative infinity (`7 // 2 == 3`). `%` computes the integer remainder (`7 % 2 == 1`).
- **Identity operators (`is`, `is not`):** Test if two variables point to the exact same object in memory (`id(a) == id(b)`).
- **Membership operators (`in`, `not in`):** Test whether an item exists inside a sequence or collection (strings, lists, tuples, sets, dictionaries).
- **Comparison operators (`==`, `!=`, `<`, `>`, `<=`, `>=`):** Compare values, including Python's intuitive comparison chaining (`18 <= age < 65`).
- **Logical operators (`and`, `or`, `not`):** Combine boolean conditions with short-circuit evaluation.
- **Assignment expressions (Walrus `:=`):** Assign a variable inline within an expression.

Every object in Python also has an innate truth value: empty collections (`[]`, `""`, `{}`), `0`, and `None` evaluate to `False`; populated collections and non-zero numbers evaluate to `True`.

> **Analogy** 🎬
>
> **Picture it — Checking ID Badges vs Checking Outfits**
>
> The equality operator `==` is like checking if two people are wearing identical outfits: if both shirts and shoes match, `a == b` is `True`. The identity operator `is` is like checking their government ID numbers: even if identical twins wear the exact same clothes, they are two separate people in memory (`a is b` is `False`). You only use `is` when checking if two references point to the exact same unique individual in memory (most notably `x is None`).

Key everyday operators and patterns:
1. **True division (`/`):** Always returns a float, even with evenly divisible integers (e.g. `10 / 2 == 5.0`, `7 / 2 == 3.5`).
2. **Floor division (`//`):** Divides and rounds down to the nearest integer floor (e.g. `7 // 2 == 3`, `10 // 3 == 3`, `-7 // 2 == -4`). Ideal for pagination calculations: `total_pages = (total_items + per_page - 1) // per_page`.
3. **Modulo remainder (`%`):** Returns the remainder after integer division (e.g. `7 % 2 == 1`, `10 % 3 == 1`). Common for checking even/odd (`n % 2 == 0`) and wrapping circular array indices (`(idx + 1) % len(items)`).
4. **Combined quotient and remainder (`divmod(a, b)`):** Returns a tuple `(a // b, a % b)` in a single operation. Perfect for time unit conversions (`mins, secs = divmod(total_seconds, 60)`).
5. **Identity operators (`is`, `is not`):** Tests exact object identity (`id(a) == id(b)`). Always use `is None` and `is not None` to test for `None`.
6. **Identity vs Equality (`is` vs `==`):** `==` checks value equality; `is` checks memory address. Two lists `[1, 2] == [1, 2]` are equal (`True`), but `[1, 2] is [1, 2]` is `False`.
7. **Membership operators (`in`, `not in`):** Tests if an item exists inside a container (`"admin" in roles`, `404 not in status_codes`, `"username" in user_dict`).
8. **Chained comparisons:** Python evaluates chained inequalities naturally: `18 <= age < 65` (evaluates `age >= 18 and age < 65` with single evaluation).
9. **Logical short-circuiting:** `and` stops at the first falsy operand; `or` stops at the first truthy operand and returns that value.
10. **Emptiness checking:** `if not items:` (clean and Pythonic, no need for `len(items) == 0`).
11. **Exponentiation (`**`):** `2 ** 8 == 256` (power operator).
12. **Inline ternary conditional:** `status = "Approved" if score >= 70 else "Rejected"`.
13. **Walrus operator (`:=`):** Assigns a variable inline within an expression, e.g. `if (n := len(data)) > 0:`.

```python
# 1. Arithmetic, Division (/, //, %), Exponentiation (**), and divmod()
print(10 / 2)     # 5.0 (True division ALWAYS returns a float)
print(7 / 2)      # 3.5
print(7 // 2)     # 3   (Floor division truncates towards -infinity)
print(10 // 3)    # 3
print(-7 // 2)    # -4  (Rounds DOWN to -4, not -3!)

# Modulo operator (%) & Even/Odd checking
print(7 % 2)      # 1   (Remainder)
print(12 % 4)     # 0   (Evenly divisible)
number = 14
is_even = (number % 2 == 0)
print(is_even)    # True

# Exponentiation (**)
print(2 ** 8)     # 256 (Power operator)

# Practical 1: Pagination calculation with floor division
total_records = 23
per_page = 5
total_pages = (total_records + per_page - 1) // per_page
print(f"Total pages needed: {total_pages}")  # Total pages needed: 5

# Practical 2: Converting seconds into minutes and seconds
total_seconds = 145
minutes = total_seconds // 60   # 2 minutes
seconds = total_seconds % 60    # 25 seconds
print(f"Formatted time: {minutes}m {seconds}s")  # Formatted time: 2m 25s

# divmod() computes quotient and remainder together
mins, secs = divmod(total_seconds, 60)
print(mins, secs)  # 2 25

# Practical 3: Circular index wrapping
total_slides = 5
for current_slide in range(5):
    next_slide = (current_slide + 1) % total_slides
    # Wraps: 0->1, 1->2, 2->3, 3->4, 4->0

# 2. Identity operators (is, is not) vs Equality (==, !=)
list_a = [1, 2, 3]
list_b = [1, 2, 3]
list_c = list_a

print(list_a == list_b)  # True (same values)
print(list_a is list_b)  # False (different objects in memory)
print(list_a is list_c)  # True (exact same object)

# Checking None safely with is and is not
current_user = None
if current_user is None:
    print("User is not logged in.")  # User is not logged in.

active_session = "sess_xyz789"
if active_session is not None:
    print("Session is active.")      # Session is active.

# 3. Membership operators (in, not in) across collections
allowed_roles = {"admin", "editor", "moderator"}
if "editor" in allowed_roles:
    print("Authorized.")             # Authorized.

blocked_ips = ["192.168.1.10", "10.0.0.99"]
if "172.16.0.1" not in blocked_ips:
    print("IP connection allowed.")  # IP connection allowed.

# Dictionary key and string membership
user_dict = {"username": "alex", "tier": "gold"}
if "username" in user_dict:
    print("Key exists in user dict.")  # Key exists in user dict.

if "@" in "alex@example.com":
    print("Valid email marker found.")  # Valid email marker found.

# 4. Comparison operators (==, !=, <, >, <=, >=) & Chained comparisons
item_count = 10
print(item_count != 0)   # True
print(item_count >= 5)   # True

user_age = 28
if 18 <= user_age < 65:  # Chained inequality: evaluated as (18 <= age and age < 65)
    print("Working adult tier.")  # Working adult tier.

# 5. Innate Truthiness & Pythonic Emptiness Checking
# Innate falsy values: 0, 0.0, "", [], {}, set(), None
print(bool(0))        # False
print(bool(""))       # False
print(bool([]))       # False
print(bool({}))       # False
print(bool(None))     # False

# Innate truthy values: non-zero numbers, populated collections
print(bool(42))       # True
print(bool("text"))   # True
print(bool([1, 2]))   # True

# Clean emptiness checking (prefer 'if not items' over 'if len(items) == 0')
cart = []
if not cart:
    print("Shopping cart is empty.")  # Shopping cart is empty.

# 6. Logical operators (and, or, not) with Short-Circuit Evaluation
# 'and' stops at the first falsy operand and returns it; if all are truthy, returns the last
print([] and "python")         # [] (first operand is falsy, returns immediately)
print("apple" and "banana")    # banana (both truthy, returns last)

# 'or' stops at the first truthy operand and returns it (idiomatic fallback default)
default_theme = "" or "dark"   # "dark" (first operand is falsy, evaluates next)
print(default_theme)           # dark

raw_name = None
display_name = raw_name or "Guest"
print(display_name)            # Guest

# 'not' inverts boolean truthiness
is_admin = False
if not is_admin:
    print("Regular user permissions.")  # Regular user permissions.

# 7. Inline Ternary Conditional
score = 82
result = "Pass" if score >= 60 else "Fail"
print(result)  # Pass

# 8. Walrus operator (:=) for assignment expressions
payload = "sensor_alpha_online"
if (length := len(payload)) > 10:
    print(f"Payload accepted with {length} characters.")  # Payload accepted with 19 characters.
```

- **Strength — Rich Mathematical & Expressive Operators** The distinction between `/` (float) and `//` (integer floor), combined with `%` and `divmod()`, makes arithmetic, pagination, and circular indexing explicit and concise.
- **Weakness — Confusing is with ==** Using `is` for value equality (`if name is "alice":`) is dangerous because Python string and integer caching creates subtle, intermittent bugs that fail unpredictably.

**Interview question**

*Given an integer, return "Fizz" if it's divisible by 3, "Buzz" if divisible by 5, "FizzBuzz" if divisible by both, or the number as a string otherwise.*

Check divisibility by both 3 and 5 first (using `% 15 == 0`), then check 3 and 5 individually.

**Answer — FizzBuzz**

```python
def fizz_buzz(n: int) -> str:
    if n % 15 == 0:
        return "FizzBuzz"
    elif n % 3 == 0:
        return "Fizz"
    elif n % 5 == 0:
        return "Buzz"
    else:
        return str(n)

# Test cases
print(fizz_buzz(15))  # FizzBuzz
print(fizz_buzz(9))   # Fizz
print(fizz_buzz(10))  # Buzz
print(fizz_buzz(7))   # 7
print("FizzBuzz passed!")  # FizzBuzz passed!
```

> **Key idea**
>
> Remember the three division operators: `/` always returns a float (`7 / 2 == 3.5`), `//` performs floor division (`7 // 2 == 3`), and `%` returns the remainder (`7 % 2 == 1`). Use `divmod(a, b)` when you need both quotient and remainder. For object identity, use `is` and `is not` only with singletons like `None`. Use `in` and `not in` for clean membership testing.

---

<a id="7-loops-and-iteration"></a>

## 7. Loops & Iteration

- **Counting Loop** `for i in range(n):` <!-- great -->
- **Index & Item** `for idx, item in enumerate(seq):` <!-- great -->
- **Loop Control** `break (stop), continue (skip)` <!-- good -->

Python loops iterate directly over items in a collection, rather than keeping track of an incrementing index variable. When you need the index alongside the item, `enumerate()` gives you both cleanly.

> **Analogy** 🎬
>
> **Picture it — A Name Call at a Meeting**
>
> In older languages, running a loop is like saying: "Look at seat 0, who is there? Now look at seat 1, who is there?" In Python, the loop is like reading down the attendee roster directly: "Alice, Bob, Charlie."

Key iteration patterns:
1. `for item in items:`: Standard collection loop
2. `for i in range(5):`: Loops 5 times (producing numbers 0, 1, 2, 3, 4)
3. `for i in range(1, 10, 2):`: Loops from 1 up to 10 in steps of 2 (1, 3, 5, 7, 9)
4. `for idx, val in enumerate(items, start=1):`: Yields index and item together
5. `for a, b in zip(list_a, list_b):`: Iterates through two lists side by side
6. `break`: Immediately exits the loop
7. `continue`: Skips the remainder of the current iteration and jumps to the next

### Understanding `range()` in Depth

In Python, `range()` generates an immutable arithmetic sequence of integers on demand. Rather than creating and storing an entire list of numbers in memory, `range` is an immutable sequence type that produces each number lazily when requested by the loop.

Key features and signatures of `range()`:
1. **Single Argument `range(stop)`:** Generates numbers from `0` up to `stop - 1`. For example, `range(5)` yields `0, 1, 2, 3, 4`.
2. **Two Arguments `range(start, stop)`:** Generates numbers starting from `start` up to `stop - 1` (a half-open interval `[start, stop)`). For example, `range(2, 6)` yields `2, 3, 4, 5`.
3. **Three Arguments `range(start, stop, step)`:** Increments by `step` on each iteration. For example, `range(0, 10, 2)` produces even numbers `0, 2, 4, 6, 8`.
4. **Negative Step (Counting Down):** If `step` is negative, `range()` counts backwards (provided `start > stop`). For example, `range(5, 0, -1)` yields `5, 4, 3, 2, 1`.
5. **Lazy Evaluation & $O(1)$ Memory:** `range()` stores only the `start`, `stop`, and `step` values. Because numbers are calculated on the fly, `range(1_000_000_000)` consumes the same tiny, constant memory ($O(1)$ space, ~48 bytes) as `range(5)`.
6. **Converting to a List:** Because `range` computes values lazily, `print(range(5))` displays `range(0, 5)`. To materialize the numbers into an explicit list, pass it to `list(range(5))` which produces `[0, 1, 2, 3, 4]`.
7. **Fast $O(1)$ Membership Testing:** Checking `x in range(...)` runs in $O(1)$ constant time because Python checks bounds and step divisibility with arithmetic instead of scanning elements sequentially.

```python
fruits = ["apple", "banana", "orange"]

# Direct iteration
for fruit in fruits:
    print(fruit)
# apple
# banana
# orange

# Iteration with index
for rank, fruit in enumerate(fruits, start=1):
    print(f"{rank}. {fruit}")
# 1. apple
# 2. banana
# 3. orange

# range() forms:
# 1. Single argument: stop [0, 5)
for i in range(3):
    print(f"Step {i}")
# Step 0
# Step 1
# Step 2

# 2. Two arguments: start and stop [2, 6)
for i in range(2, 6):
    print(f"Offset {i}")
# Offset 2
# Offset 3
# Offset 4
# Offset 5

# 3. Three arguments: start, stop, step
evens = list(range(0, 10, 2))
print(f"Evens: {evens}")  # Evens: [0, 2, 4, 6, 8]

# 4. Counting backwards with negative step
countdown = list(range(3, 0, -1))
print(f"Countdown: {countdown}")  # Countdown: [3, 2, 1]

# 5. O(1) membership check
print(50 in range(0, 100, 5))  # True (instant arithmetic check)

# Parallel iteration with zip
prices = [1.20, 0.50, 0.80]
for fruit, price in zip(fruits, prices):
    print(f"{fruit}: ${price:.2f}")
# apple: $1.20
# banana: $0.50
# orange: $0.80

# Loop control: break and continue
for n in [1, 2, 3, 4, 5]:
    if n == 2:
        continue  # Skip 2
    if n == 4:
        break     # Stop loop
    print(f"Number: {n}")
# Number: 1
# Number: 3

# While loop for conditions
count = 3
while count > 0:
    print(f"Countdown: {count}")  # Countdown: 3, 2, 1
    count -= 1
# Countdown: 3
# Countdown: 2
# Countdown: 1
```

- **Strength — Clean Syntax & O(1) Memory** Direct iteration prevents off-by-one errors, while `range()` generates sequences of any size without allocating memory for elements upfront.
- **Weakness — Modifying While Looping & Exclusive Stop** Removing items from a list while iterating over it skips elements. In `range(start, stop)`, remember that `stop` is exclusive (`range(1, 5)` stops at 4).

**Interview question**

*Given a list of numbers, find the index of the first negative number, or return -1 if none exists.*

Use `enumerate()` to inspect both index and number, and `return idx` as soon as a negative value is encountered. If the loop finishes without returning, return `-1`.

**Answer — Find First Negative Index**

```python
def find_first_negative(numbers: list[int]) -> int:
    for idx, num in enumerate(numbers):
        if num < 0:
            return idx
    return -1

# Test cases
print(find_first_negative([3, 5, -2, 8]))  # 2
print(find_first_negative([1, 2, 3]))       # -1
print(find_first_negative([-10, 0, 10]))   # 0
print("Find first negative passed!")  # Find first negative passed!
```

> **Key idea**
>
> Avoid writing `for i in range(len(items)): items[i]`. Instead, use `for item in items:` or `for i, item in enumerate(items):`. When you do need numeric sequences, `range(start, stop, step)` generates them with $O(1)$ memory. Remember that `stop` is exclusive: `range(1, 5)` generates 1, 2, 3, 4 (not 5).

---

<a id="unit-2"></a>

## Unit 2 — Core Data Collections

The primary data structures used every day: ordered lists, fast key-value dictionaries, sorting collections, unique sets, and readable list comprehensions.

<a id="8-lists-and-slicing"></a>

## 8. Lists & Slicing

- **Index Lookup** `O(1) instant access` <!-- great -->
- **Append** `list.append(item) adds to end` <!-- great -->
- **Slicing** `seq[start:stop:step]` <!-- good -->

A `list` is Python's standard ordered, mutable array. You can store any types of items in a list. You can access items by index (starting at `0` for the first item, or `-1` for the last item). Slicing allows you to extract sub-portions of a list.

> **Analogy** 🎬
>
> **Picture it — A Train of Storage Wagons**
>
> A list is a row of numbered wagons hooked together. Wagon `0` is the front, wagon `-1` is the caboose. Hooking an extra wagon to the end (`append()`) is quick and easy.

Common list operations:
1. `items[0]`: First item
2. `items[-1]`: Last item
3. `items[1:4]`: Slices elements from index 1 up to (excluding) index 4
4. `items[:3]`: First 3 elements
5. `items[-2:]`: Last 2 elements
6. `items[::-1]`: Returns a reversed copy of the list
7. `items.append(x)`: Adds item `x` to the end
8. `items.pop()`: Removes and returns the last item
9. `item in items`: Checks if item exists in list

```python
todos = ["buy groceries", "pay electric bill", "walk dog"]

# Modifying lists
todos.append("read book")       # Adds to end
completed = todos.pop()         # Removes "read book"
print(f"Finished: {completed}")  # Finished: read book

# Slicing and indexing
numbers = [10, 20, 30, 40, 50]
print(numbers[0])     # 10 (first item)
print(numbers[1:3])   # [20, 30]
print(numbers[:2])    # [10, 20]
print(numbers[-2:])   # [40, 50] (last 2 items)
print(numbers[-1])    # 50 (last item)
print(numbers[::-1])  # [50, 40, 30, 20, 10] (reversed)

# Membership check
if "buy groceries" in todos:
    print("Don't forget the milk!")  # Don't forget the milk!
```

- **Strength — Flexible & General Purpose** Lists can grow, shrink, and hold mixed data types effortlessly.
- **Weakness — Linear Search Speed** Checking `item in my_list` scans elements one by one; if you have thousands of items, use a `set` for instant lookups.

**Interview question**

*Given a list of numbers, return a new list with all duplicate values removed while preserving the original order of first appearance.*

Keep a `seen` set to track items already added, and build a new list appending items only when they haven't been seen yet.

**Answer — Deduplicate While Preserving Order**

```python
def deduplicate_preserve_order(items: list) -> list:
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result

# Test cases
print(deduplicate_preserve_order([1, 2, 2, 3, 1, 4]))  # [1, 2, 3, 4]
print(deduplicate_preserve_order(["a", "b", "a"]))      # ['a', 'b']
print("Deduplicate passed!")  # Deduplicate passed!
```

> **Key idea**
>
> Slicing a list (`lst[:]`) creates a new shallow copy. Mutating the copy will not affect the original list.

---

<a id="9-dictionaries"></a>

## 9. Dictionaries

- **Key Lookup** `Instant O(1) hash access` <!-- great -->
- **Safe Retrieval** `d.get(key, default)` <!-- great -->
- **Iteration** `for k, v in d.items():` <!-- good -->

A `dict` (dictionary) stores data in key-value pairs. Looking up a value by its key is instant ($O(1)$) regardless of whether the dictionary has 10 items or 1,000,000 items. Keys must be unique and immutable (like strings, numbers, or tuples).

> **Analogy** 🎬
>
> **Picture it — A Contact Book on Your Phone**
>
> Instead of flipping through everyone's phone numbers in order, you type "Sarah" and her contact details appear immediately. The contact name is the key; the phone number and address are the values.

Common dictionary operations:
1. `d[key]`: Gets value (raises `KeyError` if key does not exist)
2. `d.get(key, default)`: Safely gets value, returning `default` (or `None`) if key is missing
3. `d[key] = value`: Adds or updates a key-value pair
4. `k in d`: Checks if a key exists in the dictionary
5. `d.items()`: Iterates over `(key, value)` pairs
6. `d.keys()` and `d.values()`: Iterates over keys or values
7. `del d[key]`: Removes key from dictionary

```python
user = {
    "name": "Sarah Connor",
    "role": "Engineer",
    "level": 3
}

# Direct lookup and membership check
print(user["name"])        # Sarah Connor
print("role" in user)      # True

# Safe lookup with .get()
location = user.get("location", "Remote")
print(f"Location: {location}")  # Location: Remote

# Adding and updating
user["level"] = 4
user["team"] = "DevOps"

# Iterating keys and values
print(list(user.keys()))    # ['name', 'role', 'level', 'team']
print(list(user.values()))  # ['Sarah Connor', 'Engineer', 4, 'DevOps']

# Iterating over key-value pairs
for key, value in user.items():
    print(f"{key}: {value}")
# name: Sarah Connor
# role: Engineer
# level: 4
# team: DevOps

# Deleting a key
del user["level"]
print("level" in user)  # False
```

- **Strength — Instant Key Lookups** Dictionaries are the fastest and most natural way to structure associated data and configuration mappings.
- **Weakness — Direct Bracket KeyError** Accessing `user["missing_key"]` directly crashes with a `KeyError`; use `user.get("missing_key")` when a key might be absent.

**Interview question**

*Given a list of words, count how many times each word appears and return a dictionary of word counts.*

Iterate over the words and update a frequency count dictionary using `.get(word, 0) + 1`.

**Answer — Word Frequency Counter**

```python
def count_word_frequencies(words: list[str]) -> dict[str, int]:
    counts = {}
    for word in words:
        counts[word] = counts.get(word, 0) + 1
    return counts

# Test cases
words = ["apple", "banana", "apple", "orange", "banana", "apple"]
result = count_word_frequencies(words)
print(result)  # {'apple': 3, 'banana': 2, 'orange': 1}
print("Word frequency passed!")  # Word frequency passed!
```

> **Key idea**
>
> Always use `d.get(key, fallback)` when reading optional fields or external data (like JSON APIs) to avoid unexpected `KeyError` crashes.

---

<a id="10-tuples-and-sets"></a>

## 10. Tuples & Sets

- **Tuples** `Immutable fixed records: (x, y)` <!-- great -->
- **Sets** `Unique values with fast in checks` <!-- great -->
- **Set Operations** `Union |, Intersection &` <!-- good -->

A `tuple` is an ordered, immutable sequence written with parentheses `(1, 2)`. Once created, you cannot add, remove, or modify items in a tuple. A `set` is an unordered collection of unique elements written with curly braces `{1, 2}`. Sets automatically eliminate duplicates and offer instant $O(1)$ membership checks.

> **Analogy** 🎬
>
> **Picture it — A GPS Coordinate vs A Unique Badge Scanner**
>
> A GPS location `(latitude, longitude)` is a tuple: latitude and longitude are permanently paired together; changing one without the other makes no sense. A security gate scanner is a set: it holds a list of authorized employee badge IDs; duplicate scans are ignored, and checking if an ID is valid takes a fraction of a second.

Key operations:
1. `point = (10, 20)`: Creates a tuple
2. `x, y = point`: Unpacks tuple into variables
3. `unique = set([1, 2, 2, 3, 3])`: Converts list to set `{1, 2, 3}`
4. `s.add("item")`: Adds item to set
5. `val in s`: Instant $O(1)$ check if `val` is in set
6. `set_a & set_b`: Intersection (items present in both)
7. `set_a | set_b`: Union (all items from either set)

```python
# Tuples for fixed records and unpacking
user_coordinate = (37.7749, -122.4194)
lat, lon = user_coordinate
print(f"Latitude: {lat}, Longitude: {lon}")  # Latitude: 37.7749, Longitude: -122.4194

# Swapping two variables with tuple packing
a = 5
b = 10
a, b = b, a
print(a, b)  # 10 5

# Sets for unique elements
raw_roles = ["admin", "editor", "admin", "viewer", "editor"]
unique_roles = set(raw_roles)
print(unique_roles)  # {'admin', 'editor', 'viewer'}

# Adding to a set
unique_roles.add("manager")
print("manager" in unique_roles)  # True

# Fast membership check
if "admin" in unique_roles:
    print("Admin role found!")  # Admin role found!

# Set operations: union and intersection
dev_team = {"alice", "bob", "charlie"}
ops_team = {"bob", "david"}
print(dev_team & ops_team)  # {'bob'}
print(dev_team | ops_team)  # {'alice', 'bob', 'charlie', 'david'}
```

- **Strength — Automatic Deduplication & Speed** Converting a list to a set strips duplicates instantly, and `val in set` is much faster than `val in list`.
- **Weakness — Unordered Sets** Sets do not preserve order; if you need both order and uniqueness, use a list alongside a set.

**Interview question**

*Given two lists of user IDs, return a list of all user IDs that appear in both lists.*

Convert both lists to sets and take their intersection using the `&` operator.

**Answer — Find Common Users**

```python
def find_common_users(group_a: list[str], group_b: list[str]) -> list[str]:
    return list(set(group_a) & set(group_b))

# Test cases
users_1 = ["alice", "bob", "charlie"]
users_2 = ["bob", "david", "alice"]
common = find_common_users(users_1, users_2)
print(sorted(common))  # ['alice', 'bob']
print("Common users passed!")  # Common users passed!
```

> **Key idea**
>
> Writing `x = {}` creates an empty dictionary, not an empty set. To create an empty set, you must write `x = set()`.

---

<a id="11-sorting-in-python"></a>

## 11. Sorting in Python

- **In-Place vs New List** `list.sort() vs sorted(iter)` <!-- great -->
- **Order Flag** `reverse=True for descending` <!-- great -->
- **Custom Keys & Comparators** `key=func or cmp_to_key(cmp_fn)` <!-- good -->

Python provides two primary mechanisms for ordering data: the built-in `sorted()` function (which accepts any iterable and returns a brand-new sorted list) and the `list.sort()` method (which mutates a list in place and returns `None`). Both mechanisms sort elements in ascending (asc) order by default using the standard `<` comparison operator, and both accept `reverse=True` to sort in descending (desc) order. You can completely customize how elements are evaluated and ordered by passing a custom transformation function to the `key` parameter, or adapt traditional two-argument comparators via `functools.cmp_to_key`.

> **Analogy** 🎬
>
> **Picture it — Organizing a Physical Bookshelf vs Printing an Ordered Catalog**
>
> Using `list.sort()` is like physically walking up to your bookcase and rearranging the books directly on the shelf into alphabetical order: the original arrangement is altered in-place, and no new bookcase is created. Using `sorted()` is like leaving the shelf untouched and printing out a fresh, organized index on paper. You can generate that printed index from any collection — books on a shelf, a box of loose bookmarks (set), an immutable display case (tuple), or an index card drawer (dictionary) — and choose whether to print them A-to-Z or Z-to-A.

Key everyday sorting patterns across basic data structures:

1. **Lists (In-Place vs New List):**
   - In-place mutation: `scores.sort()` orders the list directly and returns `None`. Use `scores.sort(reverse=True)` for descending order.
   - Non-destructive sorting: `sorted(scores)` returns a brand-new list, leaving `scores` intact. Use `sorted(scores, reverse=True)` for descending order.
2. **Tuples (Immutable Sequences):**
   - Tuples cannot be modified, so they do not provide a `.sort()` method.
   - Calling `sorted(my_tuple)` returns a sorted `list`.
   - Wrap with `tuple()` to restore tuple immutability: `tuple(sorted(my_tuple))` for ascending order, and `tuple(sorted(my_tuple, reverse=True))` for descending order.
3. **Sets (Unordered Collections):**
   - Sets do not maintain insertion or numerical order and have no `.sort()` method.
   - Calling `sorted(my_set)` extracts and orders the unique elements into a `list` in ascending order (`sorted(my_set)`) or descending order (`sorted(my_set, reverse=True)`).
   - Re-wrapping the result in `set()` loses the sorted order because sets are fundamentally hash-based and unordered.
4. **Strings (Character Sequences):**
   - Strings are immutable. `sorted("python")` sorts individual characters alphabetically into a list of characters: `['h', 'n', 'o', 'p', 't', 'y']`.
   - Recombine the characters into a string using `"".join()`: `"".join(sorted("python"))` for ascending order, or `"".join(sorted("python", reverse=True))` for descending order.
5. **Dictionaries (Keys vs Values):**
   - Iterating over a dictionary yields its keys. Calling `sorted(my_dict)` returns a list of sorted keys: `['apple', 'banana', 'orange']`.
   - Sorting by key: Rebuild an ordered dictionary using `dict(sorted(my_dict.items()))` for ascending keys, or `dict(sorted(my_dict.items(), reverse=True))` for descending keys.
   - Sorting by value: Pass a key lambda to extract the dictionary value: `dict(sorted(my_dict.items(), key=lambda item: item[1]))` for ascending values, or `dict(sorted(my_dict.items(), key=lambda item: item[1], reverse=True))` for descending values.
6. **Custom Sorting by Factors (`key` parameter):**
   - The `key` parameter takes a one-argument function applied to each element before comparison.
   - A factor (or divisor) of a positive integer $n$ is any integer $d \ge 1$ where $n \pmod d == 0$. For example, 12 has 6 factors (`[1, 2, 3, 4, 6, 12]`), 10 has 4 factors (`[1, 2, 5, 10]`), 7 has 2 factors (`[1, 7]`), and 9 has 3 factors (`[1, 3, 9]`).
   - Ascending by factor count: `sorted(numbers, key=count_factors)` orders numbers from fewest factors to most factors.
   - Descending by factor count: `sorted(numbers, key=count_factors, reverse=True)` orders numbers from most factors to fewest factors.
   - Multi-key tie-breaking: Pass a tuple `(count_factors(x), x)` to sort first by the number of factors, and break ties using the number's own numeric value.
7. **Comparators in Python 3 (`functools.cmp_to_key`):**
   - **Does Python have comparators?** Yes, but with an important architecture transition:
     - In Python 2, `sort()` and `sorted()` supported a direct `cmp=func(a, b)` argument returning negative (`a < b`), zero (`a == b`), or positive (`a > b`).
     - In Python 3, `cmp=` was removed to eliminate runtime overhead. A `key` function transforms each element exactly once ($O(n)$ calls), whereas a comparator evaluates pairwise during sorting ($O(n \log n)$ calls).
     - To use traditional two-argument comparator logic in Python 3, import `cmp_to_key` from `functools`: `from functools import cmp_to_key`.
     - Define a standard two-argument comparator `compare(a, b) -> int`:
       - Return negative (e.g. `-1`) if `a < b` (`a` should appear before `b`).
       - Return `0` if `a == b` (both items have equal rank).
       - Return positive (e.g. `1`) if `a > b` (`a` should appear after `b`).
     - Plug it in as `sorted(items, key=cmp_to_key(compare))`.
     - **Why comparators are indispensable:** When a sorting rule depends on pairwise relationships between two elements rather than an isolated scalar attribute, a comparator is required. For example, in the classic "Largest Number" concatenation puzzle, deciding whether `"9"` or `"34"` goes first requires comparing `"9" + "34"` (`"934"`) vs `"34" + "9"` (`"349"`). Because `"934" > "349"`, `"9"` precedes `"34"`.
     - **OOP / Class Comparators:** Custom classes can implement rich comparison dunder methods (`__lt__`, `__gt__`, `__eq__`, `__le__`, `__ge__`), optionally decorated with `@functools.total_ordering`.

```python
# 1. Lists: in-place .sort() vs sorted()
scores = [45, 12, 89, 33, 70]
asc_scores = sorted(scores)
desc_scores = sorted(scores, reverse=True)
print(f"Original list: {scores}")        # Original list: [45, 12, 89, 33, 70]
print(f"Sorted asc: {asc_scores}")       # Sorted asc: [12, 33, 45, 70, 89]
print(f"Sorted desc: {desc_scores}")     # Sorted desc: [89, 70, 45, 33, 12]

# In-place list mutation
scores.sort()
print(f"In-place sorted: {scores}")      # In-place sorted: [12, 33, 45, 70, 89]

# 2. Tuples: immutable sequence
coords = (40, 10, 50, 20, 30)
asc_coords = tuple(sorted(coords))
desc_coords = tuple(sorted(coords, reverse=True))
print(f"Tuple asc: {asc_coords}")        # Tuple asc: (10, 20, 30, 40, 50)
print(f"Tuple desc: {desc_coords}")      # Tuple desc: (50, 40, 30, 20, 10)

# 3. Sets: unordered unique collection
unique_tags = {"golang", "python", "rust", "c"}
asc_tags = sorted(unique_tags)
desc_tags = sorted(unique_tags, reverse=True)
print(f"Set sorted asc: {asc_tags}")     # Set sorted asc: ['c', 'golang', 'python', 'rust']
print(f"Set sorted desc: {desc_tags}")   # Set sorted desc: ['rust', 'python', 'golang', 'c']

# 4. Strings: sorting characters
word = "python"
asc_chars = "".join(sorted(word))
desc_chars = "".join(sorted(word, reverse=True))
print(f"String asc: '{asc_chars}'")      # String asc: 'hnopty'
print(f"String desc: '{desc_chars}'")    # String desc: 'ytponh'

# 5. Dictionaries: sorting by keys and values
inventory = {"banana": 30, "apple": 10, "orange": 25, "mango": 15}

# Sort by keys (asc and desc)
by_key_asc = dict(sorted(inventory.items()))
by_key_desc = dict(sorted(inventory.items(), reverse=True))
print(f"Dict by keys asc: {by_key_asc}")
# Dict by keys asc: {'apple': 10, 'banana': 30, 'mango': 15, 'orange': 25}
print(f"Dict by keys desc: {by_key_desc}")
# Dict by keys desc: {'orange': 25, 'mango': 15, 'banana': 30, 'apple': 10}

# Sort by values (asc and desc)
by_val_asc = dict(sorted(inventory.items(), key=lambda item: item[1]))
by_val_desc = dict(sorted(inventory.items(), key=lambda item: item[1], reverse=True))
print(f"Dict by values asc: {by_val_asc}")
# Dict by values asc: {'apple': 10, 'mango': 15, 'orange': 25, 'banana': 30}
print(f"Dict by values desc: {by_val_desc}")
# Dict by values desc: {'banana': 30, 'orange': 25, 'mango': 15, 'apple': 10}

# 6. Custom sorting: Sorting list of numbers by factors count
def count_factors(n: int) -> int:
    """Return the total number of positive divisors/factors of n."""
    count = 0
    for i in range(1, int(n ** 0.5) + 1):
        if n % i == 0:
            count += 1 if i * i == n else 2
    return count

numbers = [12, 7, 9, 10, 16]
# Factor breakdown:
# 12 -> 6 factors (1, 2, 3, 4, 6, 12)
# 7  -> 2 factors (1, 7)
# 9  -> 3 factors (1, 3, 9)
# 10 -> 4 factors (1, 2, 5, 10)
# 16 -> 5 factors (1, 2, 4, 8, 16)

asc_by_factors = sorted(numbers, key=count_factors)
desc_by_factors = sorted(numbers, key=count_factors, reverse=True)
print(f"Numbers sorted by factors (asc): {asc_by_factors}")
# Numbers sorted by factors (asc): [7, 9, 10, 16, 12]
print(f"Numbers sorted by factors (desc): {desc_by_factors}")
# Numbers sorted by factors (desc): [12, 16, 10, 9, 7]

# 7. Comparators in Python 3: functools.cmp_to_key
# In Python 2, sorted() had a direct `cmp` parameter: cmp(a, b) -> -1, 0, 1.
# In Python 3, `cmp` was removed in favor of `key` because `key` is called once per element O(N),
# whereas a comparator is called O(N log N) times during pairwise comparisons.
# However, Python 3 provides functools.cmp_to_key() to bridge two-argument comparators into key functions.
from functools import cmp_to_key

# Comparator contract:
# - return negative (e.g. -1) if a < b (a precedes b)
# - return 0 if a == b (equal rank)
# - return positive (e.g. 1) if a > b (a follows b)
def factor_comparator(a: int, b: int) -> int:
    """Compare two numbers by factor count; break ties by numeric value."""
    fa, fb = count_factors(a), count_factors(b)
    if fa != fb:
        return -1 if fa < fb else 1
    if a != b:
        return -1 if a < b else 1
    return 0

numbers_by_cmp = sorted(numbers, key=cmp_to_key(factor_comparator))
print(f"Numbers sorted with comparator: {numbers_by_cmp}")
# Numbers sorted with comparator: [7, 9, 10, 16, 12]

# Pairwise comparator example: Largest Number concatenation (LeetCode 179)
# Why comparators are indispensable:
# When determining whether "9" or "34" comes first in ["3", "30", "34", "5", "9"],
# we compare relative combinations: "9"+"34" ("934") vs "34"+"9" ("349").
# Since "934" > "349", "9" precedes "34".
# This relative pairwise rule cannot be expressed with an isolated scalar key without comparing pairs.
def largest_number_comparator(a: str, b: str) -> int:
    if a + b > b + a:
        return -1  # a should come first
    elif a + b < b + a:
        return 1   # b should come first
    return 0

str_nums = ["3", "30", "34", "5", "9"]
largest_num = "".join(sorted(str_nums, key=cmp_to_key(largest_number_comparator)))
print(f"Largest number arrangement: {largest_num}")
# Largest number arrangement: 9534330
```

- **Strength — Stable & Universal Timsort** Python uses Timsort ($O(n \log n)$), which is guaranteed to be stable (preserving the relative order of elements with equal keys) and works universally across any iterable via `sorted()`.
- **Weakness — list.sort() Returns None & Type Homogeneity** Calling `x = my_list.sort()` assigns `None` to `x`, wiping out references by mistake. Furthermore, comparing elements with incompatible types (such as `[1, "2"]`) raises a `TypeError` at runtime.

**Interview question**

*Given a list of positive integers, sort the list in ascending order by their number of factors. If two numbers have the same number of factors, break the tie by sorting them by their numeric value in ascending order. Also support descending order.*

Count the divisors of each integer efficiently up to $\sqrt{n}$. In Python, this can be implemented in two ways:
1. **Idiomatic Key Function (Recommended):** Return a tuple `(count_factors(x), x)` from `key`. Python compares tuples element by element: if factor counts tie, the numeric value breaks the tie.
2. **Two-Argument Comparator:** Define a comparator function taking `(a, b)` that returns `-1`, `0`, or `1`, and convert it with `functools.cmp_to_key()`.

**Answer — Sort Numbers by Factors**

```python
from functools import cmp_to_key

def count_factors(n: int) -> int:
    """Count positive divisors of n in O(sqrt(n)) time."""
    if n <= 0:
        return 0
    count = 0
    for i in range(1, int(n ** 0.5) + 1):
        if n % i == 0:
            count += 1 if i * i == n else 2
    return count

# Method 1: Idiomatic key function with tuple tie-breaking
def sort_by_factors(nums: list[int], reverse: bool = False) -> list[int]:
    """Sort numbers by their factor count; ties broken by numeric value."""
    return sorted(nums, key=lambda x: (count_factors(x), x), reverse=reverse)

# Method 2: Two-argument comparator via functools.cmp_to_key
def factor_cmp(a: int, b: int) -> int:
    fa, fb = count_factors(a), count_factors(b)
    if fa != fb:
        return -1 if fa < fb else 1
    if a != b:
        return -1 if a < b else 1
    return 0

def sort_by_factors_cmp(nums: list[int], reverse: bool = False) -> list[int]:
    """Sort numbers using a 2-argument comparator and cmp_to_key."""
    return sorted(nums, key=cmp_to_key(factor_cmp), reverse=reverse)

# Test cases
test_list = [12, 10, 7, 16, 9, 8]
# 7  -> 2 factors (1, 7)
# 9  -> 3 factors (1, 3, 9)
# 8  -> 4 factors (1, 2, 4, 8)
# 10 -> 4 factors (1, 2, 5, 10)  <- 8 and 10 tie on factors (4); tie broken: 8 < 10
# 16 -> 5 factors (1, 2, 4, 8, 16)
# 12 -> 6 factors (1, 2, 3, 4, 6, 12)

asc_sorted = sort_by_factors(test_list)
print(asc_sorted)  # [7, 9, 8, 10, 16, 12]

desc_sorted = sort_by_factors(test_list, reverse=True)
print(desc_sorted)  # [12, 16, 10, 8, 9, 7]

assert sort_by_factors_cmp(test_list) == asc_sorted
assert sort_by_factors_cmp(test_list, reverse=True) == desc_sorted

print(sort_by_factors([2, 4, 6, 8, 1]))  # [1, 2, 4, 6, 8]
print("Sorting by factors passed!")      # Sorting by factors passed!
```

> **Key idea**
>
> Remember that `list.sort()` operates in-place and returns `None`, while `sorted()` returns a new list and leaves the original iterable unmodified. While Python 3 removed the legacy `cmp=` parameter in favor of $O(n)$ `key=` extractions, you can bridge any two-argument comparator using `from functools import cmp_to_key`. For deterministic multi-criteria sorting, return a tuple from your `key` function or resolve ties inside your comparator.

---

<a id="12-unpacking-and-destructuring"></a>

## 12. Unpacking & Destructuring

- **Multiple Assignment** `a, b = [10, 20]` <!-- great -->
- **Starred Unpacking** `first, *rest = items` <!-- great -->
- **Dict Merging** `{**defaults, **custom}` <!-- good -->

Unpacking (often called destructuring) allows you to extract elements from iterables (tuples, lists, dictionaries, or strings) and assign them directly to multiple variables in a single, clean statement. Python inspects the shape of the data on the right and distributes each element to the corresponding variable on the left.

> **Analogy** 🎬
>
> **Picture it — A Card Dealer Distributing Hands**
>
> Imagine a card dealer laying out cards onto labelled player mats. Instead of picking up the deck, finding card 0, and walking it over to Player A, then finding card 1 and handing it to Player B, the dealer deals the cards across the table in one swift motion (`player_a, player_b = deal()`). With a starred variable (`*bench`), any remaining cards are collected into a single pile automatically.

Common unpacking patterns:
1. Sequence unpacking: `x, y = (10, 20)` or `a, b, c = [1, 2, 3]`
2. In-place swapping: `a, b = b, a` (evaluates right-hand side first into a temporary tuple, then unpacks)
3. Starred leftovers: `first, *middle, last = [1, 2, 3, 4, 5]` (`first=1, middle=[2, 3, 4], last=5`)
4. Discarding unused values: `user, _, email = ("Alice", 28, "alice@example.com")` or `head, *_ = items`
5. Unpacking in iterations: `for key, value in config.items():` or `for idx, val in enumerate(items):`
6. Nested data destructuring: `name, (lat, lon) = ("Warehouse", (37.77, -122.42))`
7. Dictionary unpacking & merging: `merged = {**defaults, **custom}` (keys on the right overwrite earlier ones)

```python
# 1. Multiple assignment and variable swap
a, b = 10, 20
a, b = b, a
print(f"Swapped: a={a}, b={b}")  # Swapped: a=20, b=10

# 2. Starred unpacking for flexible lengths
scores = [98, 85, 91, 78, 88]
highest, *others, lowest = sorted(scores, reverse=True)
print(f"Top: {highest}, Rest: {others}, Lowest: {lowest}")
# Top: 98, Rest: [91, 88, 85], Lowest: 78

# 3. Discarding unneeded elements
name, _, email = ("Bob Smith", "Accountant", "bob@example.com")
print(f"{name} <{email}>")  # Bob Smith <bob@example.com>

# 4. Nested unpacking and dictionary merging
user_payload = ("admin_user", ("us-east", "cluster-1"))
username, (region, cluster) = user_payload
print(f"User {username} deployed to {region}/{cluster}")
# User admin_user deployed to us-east/cluster-1

default_settings = {"theme": "light", "notifications": True, "timeout": 30}
user_settings = {"theme": "dark", "timeout": 60}
active_settings = {**default_settings, **user_settings}
print(active_settings)  # {'theme': 'dark', 'notifications': True, 'timeout': 60}
```

- **Strength — Expressive & Clean Syntax** Eliminates clunky temporary variables, index lookups like `row[0]`, and verbose slice assignments.
- **Weakness — ValueError on Shape Mismatch** Unpacking without `*` requires the exact number of variables to match the elements (`too many values to unpack` or `not enough values to unpack`).

**Interview question**

*Given a list of transaction records where each record is a tuple formatted as `(transaction_id, customer_name, (amount, currency), status)`, write a function `extract_successful_totals(transactions: list[tuple]) -> dict[str, float]` that uses destructuring to calculate the total amount spent per currency for all `"COMPLETED"` transactions.*

Loop through transactions using nested destructuring `for _tx_id, _customer, (amount, currency), status in transactions:`. If status is `"COMPLETED"`, accumulate `amount` into the dictionary for that `currency`.

**Answer — Extract Successful Totals with Destructuring**

```python
def extract_successful_totals(transactions: list[tuple]) -> dict[str, float]:
    totals = {}
    for _tx_id, _customer, (amount, currency), status in transactions:
        if status == "COMPLETED":
            totals[currency] = round(totals.get(currency, 0.0) + amount, 2)
    return totals

# Test cases
records = [
    ("TX101", "Alice", (120.50, "USD"), "COMPLETED"),
    ("TX102", "Bob", (45.00, "EUR"), "PENDING"),
    ("TX103", "Charlie", (80.25, "USD"), "COMPLETED"),
    ("TX104", "Alice", (30.00, "EUR"), "COMPLETED"),
]
print(extract_successful_totals(records))  # {'USD': 200.75, 'EUR': 30.0}
print("Extract successful totals passed!")  # Extract successful totals passed!
```

> **Key idea**
>
> In Python, unpacking requires an exact count match. Writing `x, y = [1, 2, 3]` raises `ValueError: too many values to unpack (expected 2)`. Use a starred variable like `x, y, *rest = [1, 2, 3]` or `x, *_, y = ...` when iterable length varies.

---

<a id="13-list-comprehensions"></a>

## 13. List Comprehensions

- **Syntax** `[expression for item in iterable]` <!-- great -->
- **With Filter** `[expr for item in iterable if condition]` <!-- great -->
- **Readability** `Replaces 4 lines of loop with 1 line` <!-- good -->

A list comprehension provides a concise, readable way to create a new list by transforming or filtering elements from an existing collection. It replaces verbose multi-line `for` loops that append items one by one.

> **Analogy** 🎬
>
> **Picture it — A Filtering Sieve on a Production Line**
>
> A standard `for` loop is like an inspector inspecting each widget, deciding if it meets standards, and walking it over to place it into a bin. A list comprehension is a conveyor belt with a built-in filter: pieces that pass the filter drop directly into the box in one smooth motion.

Common patterns:
1. Basic transformation: `[x * 2 for x in numbers]`
2. Transformation with condition: `[x for x in numbers if x > 0]`
3. Cleaning strings: `[word.strip() for word in words]`
4. Inline ternary: `["Even" if x % 2 == 0 else "Odd" for x in numbers]`

```python
# Example 1: Squaring numbers
numbers = [1, 2, 3, 4, 5]
squares = [n * n for n in numbers]
print(squares)  # [1, 4, 9, 16, 25]

# Example 2: Filtering even numbers
evens = [n for n in numbers if n % 2 == 0]
print(evens)  # [2, 4]

# Example 3: Cleaning strings
raw_tags = ["  python ", "FASTAPI", "  sql  "]
clean_tags = [tag.strip().lower() for tag in raw_tags]
print(clean_tags)  # ['python', 'fastapi', 'sql']

# Example 4: Inline ternary conditional inside comprehension
labels = ["Even" if n % 2 == 0 else "Odd" for n in numbers]
print(labels)  # ['Odd', 'Even', 'Odd', 'Even', 'Odd']
```

- **Strength — Clean & Expressive** Turns repetitive 4-line accumulator loops into a single self-explanatory statement.
- **Weakness — Avoid Overcomplicating** Don't write nested comprehensions spanning three lines with multiple `if` clauses; write a regular `for` loop when logic gets complex.

**Interview question**

*Given a list of file names, return a list containing only the `.csv` files converted to lowercase.*

Use a list comprehension filtering with `.endswith(".csv")` and transforming with `.lower()`.

**Answer — Filter CSV Files**

```python
def get_csv_files(filenames: list[str]) -> list[str]:
    return [name.lower() for name in filenames if name.lower().endswith(".csv")]

# Test cases
files = ["data.CSV", "report.pdf", "users.csv", "image.png"]
print(get_csv_files(files))  # ['data.csv', 'users.csv']
print("Filter CSV files passed!")  # Filter CSV files passed!
```

> **Key idea**
>
> Only use list comprehensions when you intend to produce a new list. Never use a comprehension solely to produce side effects (like `[print(x) for x in items]`); use a normal `for` loop instead.

---

<a id="unit-3"></a>

## Unit 3 — Functions & Asynchronous Programming

Writing clean reusable functions, argument packing, and non-blocking asynchronous coroutines.

<a id="14-functions-and-arguments"></a>

## 14. Functions & Arguments

- **Definition & Defaults** `def fn(param=default):` <!-- great -->
- **Variable Positional** `*args (packed as tuple)` <!-- great -->
- **Variable Keyword** `**kwargs (packed as dict)` <!-- great -->
- **Unpacking Calls** `fn(*items, **options)` <!-- good -->

Functions let you package code into reusable, modular blocks. Functions accept arguments, execute logic, and return values using the `return` statement (or `None` if omitted).

Beyond fixed positional and default arguments, Python provides `*args` and `**kwargs` for handling arbitrary numbers of inputs:
- `*args` collects any extra positional arguments into a `tuple`.
- `**kwargs` collects any extra keyword arguments into a `dict`.
- The `*` and `**` operators also work in reverse: when calling a function, `*iterable` unpacks sequence items into positional arguments, while `**dictionary` unpacks key-value pairs into named keyword arguments.

> **Analogy** 🎬
>
> **Picture it — A Blender with an Open Hopper and Labeled Spice Rack**
>
> Standard parameters are the fixed measuring cup slots on top of a blender. `*args` is an open hopper where you can drop in as many loose fruit pieces as you want (they all land inside a basket together as a tuple). `**kwargs` is a spice rack where every ingredient arrives labeled with its own name tag (stored neatly inside a dictionary).

Key everyday patterns:
1. Positional arguments: `def add(a, b): return a + b`
2. Default arguments: `def greet(name, greeting="Hello"): return f"{greeting}, {name}"`
3. Collecting variable positional arguments with `*args`: Packed into a `tuple` inside the function (e.g. `def total(*numbers): return sum(numbers)`).
4. Collecting variable keyword arguments with `**kwargs`: Packed into a `dict` inside the function (e.g. `def configure(**settings): ...`).
5. Standard parameter ordering: Positional first, then `*args`, then keyword defaults, then `**kwargs` (`def fn(x, y=10, *args, flag=True, **kwargs):`).
6. Unpacking arguments at call time: `fn(*my_list)` expands items as positional arguments, while `fn(**my_dict)` expands keys and values as keyword arguments.
7. Forwarding arguments in wrappers: `def wrapper(*args, **kwargs): return original_func(*args, **kwargs)` passes all arguments through unchanged.
8. Multiple return values: `return width, height` (returns a tuple that can be unpacked).

```python
# 1. Default parameters and multiple return values
def calculate_total(subtotal: float, tax_rate: float = 0.08) -> float:
    return round(subtotal * (1 + tax_rate), 2)

print(calculate_total(100.0))         # 108.0 (default 8% tax)
print(calculate_total(100.0, 0.05))   # 105.0 (overrides tax rate)

# 2. Variable positional arguments (*args -> tuple)
def calculate_average(*numbers: float) -> float:
    if not numbers:
        return 0.0
    return sum(numbers) / len(numbers)

print(calculate_average(10, 20, 30))  # 20.0
scores = [85, 90, 95]
print(calculate_average(*scores))     # 90.0 (unpacking list with *)

# 3. Variable keyword arguments (**kwargs -> dict)
def build_profile(username: str, **attributes) -> dict:
    profile = {"username": username}
    profile.update(attributes)
    return profile

user = build_profile("alex_dev", role="admin", active=True, theme="dark")
print(user)
# {'username': 'alex_dev', 'role': 'admin', 'active': True, 'theme': 'dark'}

# 4. Unpacking dictionary and forwarding arguments
extra_opts = {"retries": 3, "timeout": 15}
def connect(host: str, **opts):
    return f"Connecting to {host} with {opts}"

print(connect("db.internal", **extra_opts))
# Connecting to db.internal with {'retries': 3, 'timeout': 15}

# 5. Multiple return values (unpacked as a tuple)
def get_dimensions() -> tuple[int, int]:
    return 1920, 1080

width, height = get_dimensions()
print(f"Width: {width}, Height: {height}")  # Width: 1920, Height: 1080

# 6. Forwarding arguments through a wrapper function
def log_call(fn, *args, **kwargs):
    return fn(*args, **kwargs)

print(log_call(calculate_total, 200.0, 0.10))  # 220.0
```

- **Strength — Maximum API Flexibility** `*args` and `**kwargs` let you create wrappers, middleware, and flexible helper utilities that pass arguments forward without needing to redefine every parameter.
- **Weakness — Reduced Self-Documentation When Overused** If a function signature only declares `def process(*args, **kwargs):`, callers lose IDE autocomplete, type checking, and clear documentation on what parameters are actually expected.

**Interview question**

*Write a function that calculates a bill's tip amount based on bill total and a percentage, defaulting to 15% tip.*

Define a function taking `bill: float` and `percentage: float = 15.0`, computing `bill * (percentage / 100)`.

**Answer — Calculate Tip**

```python
def calculate_tip(bill: float, percentage: float = 15.0) -> float:
    if bill < 0:
        raise ValueError("Bill cannot be negative.")
    return round(bill * (percentage / 100), 2)

# Test cases
print(calculate_tip(100.0))        # 15.0
print(calculate_tip(50.0, 20.0))   # 10.0
print(calculate_tip(0.0))          # 0.0
print("Calculate tip passed!")  # Calculate tip passed!
```

**Interview question**

*Write a URL builder function `build_query_url(base_url, *paths, **params)` that accepts a base URL, any number of path segments via `*paths`, and query parameters via `**params`, returning a cleanly formatted URL.*

Strip trailing slashes from `base_url`, join any non-empty `paths` with forward slashes, and format sorted `params` into a query string joined by `&` following a `?`.

**Answer — Build Query URL with *args and **kwargs**

```python
def build_query_url(base_url: str, *paths: str, **params: str) -> str:
    url = base_url.rstrip("/")
    if paths:
        url += "/" + "/".join(p.strip("/") for p in paths)
    if params:
        query = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
        url += "?" + query
    return url

# Test cases
print(build_query_url("https://api.example.com", "v1", "users", page="1", sort="desc"))
# https://api.example.com/v1/users?page=1&sort=desc
print(build_query_url("https://api.example.com", status="active"))
# https://api.example.com?status=active
print(build_query_url("https://api.example.com/", "health"))
# https://api.example.com/health
print("Build query URL passed!")  # Build query URL passed!
```

> **Key idea**
>
> Remember the parameter order: regular positional arguments first, then `*args`, then keyword defaults, and finally `**kwargs` (`def func(pos, *args, kw_default='val', **kwargs):`). When forwarding arguments to another function, use `func(*args, **kwargs)`.

---

<a id="15-async-and-await"></a>

## 15. Async / Await

- **Coroutine Function** `async def fetch(): ...` <!-- great -->
- **Yield Control** `await coroutine()` <!-- great -->
- **Concurrent Execution** `asyncio.gather(*tasks)` <!-- good -->
- **Event Loop Runner** `asyncio.run(main())` <!-- good -->

Modern Python supports asynchronous programming via `async` and `await` and the built-in `asyncio` library. Unlike multi-threading which relies on the operating system to switch between threads, asynchronous programming uses **cooperative multitasking** on a single thread. When a coroutine reaches an I/O operation (such as waiting for an HTTP API response or database query), it uses `await` to yield control back to the **event loop**, allowing other tasks to run in the meantime.

> **Analogy** 🎬
>
> **Picture it — A Fast-Order Chef with Kitchen Timers**
>
> In synchronous code, a chef puts bread in the toaster and stares blankly at it for 3 minutes before starting to boil water for tea. In asynchronous code (`async/await`), the chef pushes the toaster lever down (`await toast()`), immediately turns around to start the kettle (`await boil_water()`), and chops vegetables. When a timer dings, the chef picks up the finished item. One chef (a single thread), zero idle waiting time.

Key async patterns and concepts:
1. `async def`: Declares an asynchronous coroutine function. Calling it does not run the code immediately; it returns a coroutine object.
2. `await`: Pauses execution of the coroutine until the awaited operation finishes, yielding the thread back to the event loop. `await` can only be used inside `async def` functions.
3. `asyncio.run(main())`: The modern entry point to run an async program. It creates a new event loop, executes the passed coroutine, and closes the loop upon completion.
4. `asyncio.gather(*tasks)`: Runs multiple coroutines concurrently and returns their aggregated results in the order the tasks were passed.
5. `asyncio.sleep(delay)`: A non-blocking asynchronous sleep. In contrast, `time.sleep()` freezes the entire thread and blocks all concurrent tasks.
6. `asyncio.create_task(coro)`: Schedules a coroutine to run immediately in the background on the event loop as an independent Task.
7. I/O-bound vs CPU-bound: Use `asyncio` for I/O-bound operations (network requests, API calls, database queries, file transfers). For CPU-intensive operations (heavy number crunching, image processing), use `multiprocessing` to run tasks on separate CPU cores.

```python
import asyncio
import time

# Asynchronous coroutine simulating non-blocking network I/O
async def fetch_service_data(service_name: str, delay: float) -> dict:
    await asyncio.sleep(delay)  # Non-blocking pause
    return {"service": service_name, "status": "online", "latency_ms": int(delay * 1000)}

async def main():
    # Running multiple coroutines concurrently
    start = time.perf_counter()
    results = await asyncio.gather(
        fetch_service_data("auth-service", 0.05),
        fetch_service_data("billing-service", 0.03),
        fetch_service_data("analytics-service", 0.01),
    )
    elapsed = time.perf_counter() - start

    for res in results:
        print(f"Service: {res['service']} | Status: {res['status']} ({res['latency_ms']}ms)")
    # Service: auth-service | Status: online (50ms)
    # Service: billing-service | Status: online (30ms)
    # Service: analytics-service | Status: online (10ms)

    # Elapsed time is approximately max(delays) ~0.05s, not sum(delays) 0.09s
    print(f"Concurrent fetch completed in {elapsed:.3f}s")
    # Concurrent fetch completed in 0.052s

    # Running a background task independently with create_task
    task = asyncio.create_task(fetch_service_data("metrics-collector", 0.02))
    bg_res = await task
    print(f"Background: {bg_res['service']} ({bg_res['latency_ms']}ms)")
    # Background: metrics-collector (20ms)

# Entry point to execute top-level coroutine
if __name__ == "__main__":
    asyncio.run(main())
```

- **Strength — Massive I/O Concurrency with Low Overhead** A single process can easily manage tens of thousands of concurrent network connections without the high memory and context-switching overhead of OS threads.
- **Weakness — Blocking Calls Freeze the Entire Event Loop** If you execute synchronous blocking code (like `time.sleep()` or synchronous `requests.get()`) inside a coroutine, the entire event loop stops, stalling every other concurrent task.

**Interview question**

*Write an asynchronous function `check_all_services(endpoints: list[tuple[str, float]]) -> dict[str, str]` that queries multiple service endpoints concurrently using `asyncio.gather()`. Simulate network latency using `asyncio.sleep()`, and return a dictionary mapping each service name to its health status.*

Define a helper coroutine `ping_endpoint(name: str, delay: float) -> tuple[str, str]` that awaits `asyncio.sleep(delay)` and returns `(name, "healthy")`. In `check_all_services`, construct task coroutines for each endpoint, execute them concurrently with `await asyncio.gather(*tasks)`, and convert the returned list of tuples into a dictionary.

**Answer — Concurrent Service Health Checker**

```python
import asyncio

async def ping_endpoint(name: str, delay: float) -> tuple[str, str]:
    await asyncio.sleep(delay)
    return (name, "healthy")

async def check_all_services(endpoints: list[tuple[str, float]]) -> dict[str, str]:
    tasks = [ping_endpoint(name, delay) for name, delay in endpoints]
    results = await asyncio.gather(*tasks)
    return dict(results)

# Test cases
async def run_tests():
    services = [("auth", 0.02), ("db", 0.01), ("cache", 0.01)]
    status_map = await check_all_services(services)
    print(status_map)
    # {'auth': 'healthy', 'db': 'healthy', 'cache': 'healthy'}

    # Empty list test
    empty_res = await check_all_services([])
    print(empty_res)  # {}
    print("Service health checker passed!")  # Service health checker passed!

asyncio.run(run_tests())
```

> **Key idea**
>
> Never invoke synchronous blocking calls (such as `time.sleep()` or synchronous file/network I/O) inside coroutines. If you must run blocking legacy code, delegate it to a worker thread using `await asyncio.to_thread(blocking_func, arg)`.

---

<a id="unit-4"></a>

## Unit 4 — Object-Oriented Programming

Modeling real-world entities, encapsulating state, and writing clean maintainable classes with methods and inheritance.

<a id="16-object-oriented-programming"></a>

## 16. Object-Oriented Programming (OOP)

- **Class & Instance** `class BankAccount: / acc = BankAccount()` <!-- great -->
- **Initializer** `def __init__(self, ...):` <!-- great -->
- **Special Methods** `__str__, __repr__` <!-- good -->
- **Inheritance** `class Savings(BankAccount): super()` <!-- good -->
- **Multiple Inheritance & MRO** `class Copier(Scanner, Printer): super()` <!-- great -->

In Python, Object-Oriented Programming (OOP) is a programming paradigm that organizes code around objects rather than just isolated functions. A **class** is a blueprint defining attributes (data) and methods (behavior). An **object** (or instance) is a concrete realization of that blueprint with its own state.

Python passes the instance itself explicitly as the first parameter to methods, conventionally named `self`. The `__init__` constructor sets up initial instance state when an object is instantiated. Classes also support single and multiple inheritance, allowing child classes to reuse, extend, or override parent methods using `super()`.

> **Analogy** 🎬
>
> **Picture it — An Architectural Blueprint vs Built Houses**
>
> A class is the architectural blueprint for a house: it specifies that every house has bedrooms, bathrooms, and a front door, and defines how the doorbell works. An object (instance) is an actual physical house built on a specific lot with its own address, wall color, and occupants. You can build dozens of unique houses (`house1`, `house2`) from the exact same blueprint.

Key everyday OOP concepts:
1. `class Name:`: Defines a class template. Class names conventionally use CapWords / PascalCase.
2. `def __init__(self, ...):`: The initializer method that runs automatically when creating a new object.
3. `self`: A reference to the current instance, used to read or modify its attributes (`self.balance = 0.0`).
4. Instance attributes vs Class attributes: Attributes assigned to `self` belong to that specific instance; attributes defined at the class level are shared across all instances.
5. Special dunder methods: `__str__` returns a friendly string for end users (used by `print()`), while `__repr__` returns an unambiguous representation for developers and debugging.
6. Single inheritance and `super()`: `class Child(Parent):` inherits behavior from a parent class, and `super().__init__(...)` delegates initialization to the parent class.
7. Multiple Inheritance: Python allows a class to inherit from multiple parent classes: `class Child(ParentA, ParentB):`.
8. The Diamond Problem: A diamond inheritance hierarchy occurs when class `D` inherits from both `B` and `C`, and both `B` and `C` inherit from the same common base class `A`. In naive implementations, calling base classes directly (`A.__init__(self)`) causes grandparent `A`'s initializer to execute twice, corrupting state and duplicating side-effects.
9. Method Resolution Order (MRO) & C3 Linearization: Python solves the diamond problem using the **C3 linearization** algorithm. It flattens the inheritance graph into a deterministic, linear search order (e.g., `D -> B -> C -> A -> object`) where subclasses always precede parents, parent ordering is preserved, and every ancestor is visited exactly once. Inspect it anytime via `ClassName.__mro__` or `ClassName.mro()`.
10. Cooperative `super()` and `**kwargs`: In Python, `super()` does not simply mean "my direct parent" — it dynamically calls the **next class in the instance's runtime MRO**. In a diamond (`D(B, C)`), calling `super()` inside `B` delegates to sibling `C`, not grandparent `A`! To work properly, all classes in the hierarchy must:
    - Call `super().__init__(**kwargs)` rather than hardcoding parent names like `ParentA.__init__(self)`.
    - Accept `**kwargs` and pass remaining unconsumed keyword arguments up the chain so sibling classes receive their needed parameters.
    - Let the top-level base class pass any remaining keyword arguments to `object.__init__(**kwargs)`.

```python
# 1. Defining a class with __init__ and methods
class BankAccount:
    bank_name = "TechBank"  # Class attribute (shared)

    def __init__(self, owner: str, balance: float = 0.0):
        self.owner = owner          # Instance attribute
        self.balance = balance      # Instance attribute

    def deposit(self, amount: float) -> float:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self.balance += amount
        return self.balance

    def withdraw(self, amount: float) -> float:
        if amount > self.balance:
            raise ValueError("Insufficient funds.")
        self.balance -= amount
        return self.balance

    def __str__(self) -> str:
        return f"BankAccount(owner='{self.owner}', balance=${self.balance:.2f})"

    def __repr__(self) -> str:
        return f"BankAccount(owner='{self.owner}', balance={self.balance})"

# 2. Creating instances and invoking methods
acc = BankAccount("Alice", 100.0)
acc.deposit(50.0)
print(acc)        # BankAccount(owner='Alice', balance=$150.00)
print(repr(acc))  # BankAccount(owner='Alice', balance=150.0)

# 3. Inheritance and super()
class SavingsAccount(BankAccount):
    def __init__(self, owner: str, balance: float = 0.0, interest_rate: float = 0.03):
        super().__init__(owner, balance)
        self.interest_rate = interest_rate

    def apply_interest(self) -> float:
        earned = self.balance * self.interest_rate
        self.balance += earned
        return self.balance

savings = SavingsAccount("Bob", 1000.0)
savings.apply_interest()
print(f"Savings balance: ${savings.balance:.2f}")  # Savings balance: $1030.00

# 4. Multiple Inheritance & The Diamond Problem solved properly with super()
#
#       Device
#       /    \
#   Scanner  Printer
#       \    /
#       Copier
#
class Device:
    def __init__(self, device_id: str, **kwargs):
        super().__init__(**kwargs)
        self.device_id = device_id

class Scanner(Device):
    def __init__(self, resolution_dpi: int, **kwargs):
        super().__init__(**kwargs)
        self.resolution_dpi = resolution_dpi

class Printer(Device):
    def __init__(self, print_speed_ppm: int, **kwargs):
        super().__init__(**kwargs)
        self.print_speed_ppm = print_speed_ppm

class Copier(Scanner, Printer):
    def __init__(self, is_color: bool, **kwargs):
        super().__init__(**kwargs)
        self.is_color = is_color

# Copier MRO: Copier -> Scanner -> Printer -> Device -> object
print([cls.__name__ for cls in Copier.__mro__])
# ['Copier', 'Scanner', 'Printer', 'Device', 'object']

copier = Copier(device_id="DEV-101", resolution_dpi=1200, print_speed_ppm=35, is_color=True)
print(copier.device_id, copier.resolution_dpi, copier.print_speed_ppm, copier.is_color)
# DEV-101 1200 35 True
```

- **Strength — Encapsulation & Cohesion** Bundling state and behavior together keeps related logic organized, avoids scattered helper functions, and protects data integrity.
- **Strength — Cooperative Multiple Inheritance & Mixins** Python's C3 Linearization MRO allows clean composability through mixins and multiple inheritance without duplicate base execution when `super()` is used consistently.
- **Weakness — Avoid Over-Engineering** Don't create complex 5-level inheritance hierarchies or write classes for simple tasks where a plain dictionary, namedtuple, or pure function is simpler and faster.
- **Weakness — Brittle Diamond Coupling with Direct Class Calls** Hardcoding `BaseClass.__init__(self)` bypasses the MRO chain, causing grandparent initializers to execute multiple times, state to be clobbered, and cooperative siblings to be skipped.

**Interview question**

*Design an InventoryItem class that tracks product name, stock quantity, and price. Add methods to restock items, record sales (raising a ValueError if stock is insufficient), and calculate the total inventory valuation.*

Define an `InventoryItem` class initialized with `name: str`, `quantity: int = 0`, and `unit_price: float = 0.0`. Validate that quantity and price are non-negative. Provide `.restock(amount)` to increase quantity, `.sell(amount)` to decrease quantity (raising `ValueError` when `amount > self.quantity`), and `.total_value()` returning `round(quantity * unit_price, 2)`. Add `__repr__` for clear debugging.

**Answer — Inventory Item Class**

```python
class InventoryItem:
    def __init__(self, name: str, quantity: int = 0, unit_price: float = 0.0):
        if quantity < 0 or unit_price < 0:
            raise ValueError("Quantity and price must be non-negative.")
        self.name = name
        self.quantity = quantity
        self.unit_price = unit_price

    def restock(self, amount: int) -> int:
        if amount <= 0:
            raise ValueError("Restock amount must be positive.")
        self.quantity += amount
        return self.quantity

    def sell(self, amount: int) -> int:
        if amount <= 0:
            raise ValueError("Sale amount must be positive.")
        if amount > self.quantity:
            raise ValueError(f"Cannot sell {amount}; only {self.quantity} in stock.")
        self.quantity -= amount
        return self.quantity

    def total_value(self) -> float:
        return round(self.quantity * self.unit_price, 2)

    def __repr__(self) -> str:
        return f"InventoryItem(name='{self.name}', qty={self.quantity}, price={self.unit_price})"

# Test cases
item = InventoryItem("Mechanical Keyboard", quantity=10, unit_price=79.99)
print(item.total_value())  # 799.9
item.restock(5)
print(item.quantity)       # 15
item.sell(3)
print(item.quantity)       # 12
print(item.total_value())  # 959.88

try:
    item.sell(20)
except ValueError as e:
    print(e)  # Cannot sell 20; only 12 in stock.

print("Inventory item passed!")  # Inventory item passed!
```

**Interview question**

*Design a diamond inheritance hierarchy for a smart document workstation with a base class Device, intermediate classes Scanner and Printer, and a derived class Copier that inherits from both Scanner and Printer. Implement cooperative multiple inheritance using super() and **kwargs so that each class initializes its specific attributes properly, the root Device initializer executes exactly once without duplicate calls, and a cooperative diagnostics method delegates across the entire Method Resolution Order (MRO).*

In Python multiple inheritance, when a derived class `Copier` inherits from both `Scanner` and `Printer`, and both inherit from `Device`, the inheritance hierarchy forms a diamond shape (`Copier -> Scanner, Printer -> Device`).

To solve the diamond problem properly:
1. **Linearize Ancestors with MRO:** Inspect `Copier.__mro__` to verify the resolution path: `Copier -> Scanner -> Printer -> Device -> object`.
2. **Cooperative Initialization with `**kwargs`:** Each class accepts its own specific keyword arguments (`device_id` and `brand` in `Device`, `resolution_dpi` in `Scanner`, `print_speed_ppm` in `Printer`, and `has_duplex` in `Copier`). Each class extracts what it needs and forwards `**kwargs` via `super().__init__(**kwargs)`.
3. **Avoid Explicit Class Calls:** Never invoke `Device.__init__(self, ...)` directly. Using `super().__init__(**kwargs)` guarantees that `Device.__init__` is reached exactly once at the end of the MRO.
4. **Cooperative Method Delegation:** In `diagnostics() -> list[str]`, each class prepends its status and delegates to `super().diagnostics()`. When `Scanner` calls `super().diagnostics()`, MRO directs the call to sibling `Printer`, not `Device`, ensuring every subsystem is tested.

**Answer — Diamond Inheritance with Cooperative super()**

```python
class Device:
    init_count = 0

    def __init__(self, device_id: str, brand: str = "Generic", **kwargs):
        super().__init__(**kwargs)
        self.device_id = device_id
        self.brand = brand
        Device.init_count += 1

    def diagnostics(self) -> list[str]:
        return [f"Device({self.device_id}, brand={self.brand}) OK"]

class Scanner(Device):
    def __init__(self, resolution_dpi: int = 600, **kwargs):
        super().__init__(**kwargs)
        self.resolution_dpi = resolution_dpi

    def diagnostics(self) -> list[str]:
        return [f"Scanner({self.resolution_dpi} DPI) OK"] + super().diagnostics()

class Printer(Device):
    def __init__(self, print_speed_ppm: int = 30, **kwargs):
        super().__init__(**kwargs)
        self.print_speed_ppm = print_speed_ppm

    def diagnostics(self) -> list[str]:
        return [f"Printer({self.print_speed_ppm} PPM) OK"] + super().diagnostics()

class Copier(Scanner, Printer):
    def __init__(self, has_duplex: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.has_duplex = has_duplex

    def diagnostics(self) -> list[str]:
        return [f"Copier(duplex={self.has_duplex}) OK"] + super().diagnostics()

# Test cases
copier = Copier(
    device_id="DEV-200",
    brand="Canon",
    resolution_dpi=2400,
    print_speed_ppm=40,
    has_duplex=True
)

# 1. Verify attributes from all classes in diamond
print(copier.device_id)        # DEV-200
print(copier.brand)            # Canon
print(copier.resolution_dpi)   # 2400
print(copier.print_speed_ppm)  # 40
print(copier.has_duplex)       # True

# 2. Verify root Device.__init__ ran exactly once
print(Device.init_count)       # 1

# 3. Verify MRO order
mro_order = [cls.__name__ for cls in Copier.__mro__]
print(mro_order)
# ['Copier', 'Scanner', 'Printer', 'Device', 'object']

# 4. Verify cooperative diagnostics method execution
for status in copier.diagnostics():
    print(status)
# Copier(duplex=True) OK
# Scanner(2400 DPI) OK
# Printer(40 PPM) OK
# Device(DEV-200, brand=Canon) OK

print("Diamond problem solution passed!")  # Diamond problem solution passed!
```

> **Key idea**
>
> In Python, multiple inheritance solves the diamond problem via **C3 linearization (MRO)** and **cooperative `super()`**. Never call parent initializers explicitly by class name like `Base.__init__(self)`; always use `super().__init__(**kwargs)` and forward `**kwargs` across the entire hierarchy so every ancestor is visited exactly once in deterministic order.

---

<a id="unit-5"></a>

## Unit 5 — Modules & Environments

Structuring scripts, and managing isolated project environments.

<a id="17-modules-and-imports"></a>

## 17. Modules & Imports

- **Import Syntax** `import mod / from mod import fn` <!-- great -->
- **Script Guard** `if __name__ == "__main__":` <!-- great -->
- **Standard Library** `math, os, sys, json, pathlib` <!-- good -->

A module in Python is simply a `.py` file containing functions, classes, and variables. A package is a directory containing multiple modules (often accompanied by an `__init__.py` file). Python's module system lets you organize code logically across files, reuse utilities, and avoid namespace pollution. The standard library provides dozens of battle-tested modules out of the box without needing third-party packages.

> **Analogy** 🎬
>
> **Picture it — A Professional Toolbox with Labeled Drawers**
>
> Instead of dumping every wrench, hammer, screwdriver, and nail onto your workbench all at once (which causes clutter and confusion), a workshop organizes tools into labeled drawers. When you need a measuring tape, you open the `math` drawer; when you need to serialize data, you open the `json` drawer. If you only need one specific screwdriver, you take just that tool (`from toolbox import screwdriver`) without cluttering your workbench.

Key import patterns and practices:
1. `import module_name`: Imports the entire module under its namespace (e.g. `import math; math.sqrt(16)`).
2. `from module_name import function_name`: Imports specific attributes directly into the local namespace (e.g. `from math import sqrt, pi`).
3. `import module_name as alias`: Aliases the module name for brevity or to avoid collisions (e.g. `import datetime as dt`).
4. Avoid `from module import *`: Wildcard imports pollute the local namespace, obscure where names originated, and can accidentally overwrite existing variables.
5. `if __name__ == "__main__":`: When a Python file is run directly (via `python script.py`), Python sets `__name__` to `"__main__"`. When imported as a module, `__name__` is set to the module's file name. This guard lets you write files that act as reusable libraries when imported, but execute scripts or tests when run directly.
6. Standard library powerhouses: `pathlib` for modern object-oriented filesystem paths, `json` for serializing and deserializing JSON, `datetime` for timestamps, and `math` for mathematical functions.

```python
import json
import math
from datetime import datetime
from pathlib import Path

# 1. Standard library math functions
root = math.isqrt(49)
print(f"Square root: {root}")  # Square root: 7

# 2. JSON serialization and deserialization
user_data = {"username": "alex_dev", "role": "admin", "active": True}
json_string = json.dumps(user_data)
print(f"Serialized JSON: {json_string}")
# Serialized JSON: {"username": "alex_dev", "role": "admin", "active": true}

parsed_data = json.loads(json_string)
print(f"Parsed username: {parsed_data['username']}")  # Parsed username: alex_dev

# 3. Pathlib for filesystem path handling
config_path = Path("config/app.json")
print(f"Filename: {config_path.name}, Extension: {config_path.suffix}")
# Filename: app.json, Extension: .json

# 4. Datetime handling
sample_date = datetime(2026, 1, 1, 12, 0)
print(sample_date.strftime("%Y-%m-%d"))  # 2026-01-01

# 5. Entry point guard for standalone script execution
def run_app():
    print("Application initialized successfully.")  # Application initialized successfully.

if __name__ == "__main__":
    run_app()
```

- **Strength — Clean Namespaces & Reusability** Modules separate concerns, prevent variable name collisions, and let teams share tested code across projects without duplication.
- **Weakness — Circular Imports** If module A imports module B and module B simultaneously imports module A at the top level, Python throws an `ImportError` or `AttributeError` because one module is accessed before it finishes executing.

**Interview question**

*Write a modular configuration loader function `load_config(raw_json: str, required_keys: list[str]) -> dict` that parses a JSON configuration string and verifies that all required keys are present. If the JSON is malformed or any required key is missing, raise a descriptive ValueError.*

Use `json.loads()` to deserialize the input string inside a `try / except json.JSONDecodeError` block, verify the parsed object is a dictionary, and check that each required key exists in the parsed data.

**Answer — Load and Validate Config**

```python
import json

def load_config(raw_json: str, required_keys: list[str]) -> dict:
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as err:
        raise ValueError(f"Invalid JSON format: {err}") from err

    if not isinstance(data, dict):
        raise ValueError("Configuration payload must be a JSON object.")

    missing = [k for k in required_keys if k not in data]
    if missing:
        missing_str = ", ".join(missing)
        raise ValueError(f"Missing required configuration keys: {missing_str}")

    return data

# Test cases
valid_payload = '{"host": "localhost", "port": 5432, "database": "analytics"}'
config = load_config(valid_payload, ["host", "port"])
print(config["host"])  # localhost
print(config["port"])  # 5432

# Test missing key raises ValueError
try:
    load_config(valid_payload, ["host", "api_key"])
except ValueError as e:
    print(e)  # Missing required configuration keys: api_key

# Test invalid JSON syntax raises ValueError
try:
    load_config("{invalid: json", ["host"])
except ValueError as e:
    print("Invalid JSON caught")  # Invalid JSON caught

print("Load config passed!")  # Load config passed!
```

> **Key idea**
>
> Always wrap executable code in `if __name__ == "__main__":` so that importing the file from another module or test suite doesn't execute script entry logic. Avoid `from module import *` in production code to prevent naming collisions and hidden bugs.

---

<a id="18-virtual-environments"></a>

## 18. Virtual Environments

- **Environment Creation** `python3 -m venv .venv` <!-- great -->
- **Activation** `source .venv/bin/activate` <!-- great -->
- **Dependency Installation** `pip install -r requirements.txt` <!-- good -->

A virtual environment is a self-contained, isolated directory tree containing a Python installation for a specific version, along with its own independent set of packages in `site-packages`. Without a virtual environment, installing third-party libraries globally with `pip install` risks version conflicts across different projects and can corrupt system Python tools. Activating an environment temporarily modifies your shell's `PATH` so `python` and `pip` point directly to the project's local sandbox.

> **Analogy** 🎬
>
> **Picture it — A Dedicated Apartment Kitchen vs. A Shared Public Canteen**
>
> Imagine sharing one giant global kitchen with every tenant in a city. If project A needs Chef salt v1 and project B demands Chef salt v2, their conflicting ingredients ruin each other's recipes. A virtual environment is your project's private kitchen: you stock exactly the spices and utensils your specific recipe needs without interfering with anyone else. When you leave the project, you simply step outside or delete the kitchen folder without leaving any mess.

### Using

```bash
# Create a virtual environment named `.venv`
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`

# Install dependencies from `requirements.txt` if it exists
pip install -r requirements.txt
```

Key everyday commands and workflow:
1. `python3 -m venv .venv`: Uses Python's built-in `venv` module to create an isolated environment in a directory named `.venv`.
2. `source .venv/bin/activate`: Updates shell environment variables (`PATH` and `VIRTUAL_ENV`) so terminal commands resolve to `.venv/bin/python` and `.venv/bin/pip`. On Windows (PowerShell/Command Prompt), run `.venv\Scripts\activate`.
3. `pip install -r requirements.txt`: Reads the dependency specification and installs reproducible package versions into `.venv/lib/pythonX.Y/site-packages`.
4. `pip freeze > requirements.txt`: Exports currently installed packages and exact version pins to share with collaborators or deploy in CI/CD.
5. `deactivate`: Restores shell environment variables back to their previous system values.
6. Verify active environment in Python code: inspect `sys.prefix != sys.base_prefix` to confirm isolation at runtime.

```python
import re
import sys
from pathlib import Path

# Verify whether the current script is running inside a virtual environment
def is_virtual_env() -> bool:
    # In a virtual environment, sys.prefix points to the .venv directory,
    # while sys.base_prefix points to the global system Python installation.
    return sys.prefix != sys.base_prefix

print(f"Python Executable: {sys.executable}")
# Python Executable: /Users/pankaj/Workspace/ai/.venv/bin/python3
print(f"Active Environment Path: {sys.prefix}")
# Active Environment Path: /Users/pankaj/Workspace/ai/.venv
print(f"Base System Python Path: {sys.base_prefix}")
# Base System Python Path: /usr/local
print(f"Running inside virtual environment: {is_virtual_env()}")
# Running inside virtual environment: True

# Check for requirements.txt in project root
req_file = Path("requirements.txt")
if req_file.exists():
    dependencies = [line.strip() for line in req_file.read_text().splitlines() if line.strip() and not line.startswith("#")]
    print(f"Project requirements ({len(dependencies)} packages): {dependencies}")
    # Project requirements (3 packages): ['fastapi>=0.110.0', 'uvicorn~=0.28.0', 'requests==2.31.0']
```

- **Strength — Clean Project Isolation & Reproducibility** Keeps conflicting package versions strictly separated per project and enables deterministic, zero-surprise builds across team members and CI/CD pipelines.
- **Weakness — Committing `.venv` to Git** The `.venv` folder is OS- and path-dependent and must never be committed to source control. Always add `.venv/` to `.gitignore` and commit `requirements.txt` instead.

**Interview question**

*Write a Python utility function `parse_requirements(requirements_content: str) -> dict[str, str]` that parses a standard `requirements.txt` file string and returns a dictionary mapping package names to their pinned version constraints (e.g. `{"fastapi": ">=0.110.0", "requests": "==2.31.0"}`). Ignore comments and empty lines.*

Iterate over the lines, strip whitespace, ignore empty lines and comment lines starting with `#`, then parse package names and version specifiers (such as `==`, `>=`, `<=`, `~=`).

**Answer — Parse Requirements File**

```python
import re

def parse_requirements(requirements_content: str) -> dict[str, str]:
    requirements = {}
    pattern = re.compile(r"^([A-Za-z0-9_.\-]+)\s*([<>=!~].*)?$")

    for line in requirements_content.splitlines():
        cleaned = line.strip()
        # Skip empty lines and comment lines
        if not cleaned or cleaned.startswith("#"):
            continue

        match = pattern.match(cleaned)
        if match:
            pkg_name = match.group(1).lower()
            specifier = (match.group(2) or "").strip()
            requirements[pkg_name] = specifier

    return requirements

# Test cases
sample_reqs = """
# Production dependencies
requests==2.31.0
fastapi>=0.110.0
uvicorn~=0.28.0
pytest
"""

parsed = parse_requirements(sample_reqs)
print(parsed["requests"])      # ==2.31.0
print(parsed["fastapi"])       # >=0.110.0
print(parsed["uvicorn"])       # ~=0.28.0
print(repr(parsed["pytest"]))  # ''
print("Parse requirements passed!")  # Parse requirements passed!
```

> **Key idea**
>
> Always use a dedicated virtual environment for every Python project. Never install third-party dependencies into the global system interpreter, and never commit the `.venv` directory to Git — commit `requirements.txt` so anyone can recreate the environment in seconds.

---

## Daily Python Cheat Sheet

A quick checklist of the most common daily syntax:

1. **Variables, Types & Casting:** Python is dynamically typed. Check for emptiness with `if items:` or `if not items:`. Compare singletons with `if val is None:`. Cast explicitly with `int()`, `float()`, `str()`, `bool()`.
2. **Type Hints:** Annotate variables and functions: `def fn(x: int) -> str | None:`. Use `list[str]` and `dict[str, int]` for generic collections.
3. **Keywords:** Only 35 reserved words in Python (`keyword.kwlist`). Check with `keyword.iskeyword()`. Never name variables after keywords.
4. **Error Handling:** Catch expected issues with `try / except SpecificError:`. Use `else` for code that runs only when no exception occurs, and `finally` for cleanup. Never write bare `except: pass`.
5. **Strings:** Format with `f"Hello {name}"`. Clean with `.strip()`, split into lists with `.split()`, join with `", ".join(list)`, and test substrings with `in` and `not in`.
6. **Conditionals & Operators:** Use `/` for float division, `//` for floor division, `%` for modulo, and `divmod()` for both. Use `is` and `is not` for identity (`val is None`), `==` and `!=` for values. Chain comparisons: `18 <= age < 65`.
7. **Loops:** Iterate cleanly with `for item in items:` or `for i, item in enumerate(items):`. Use `zip()` for parallel iteration, and `break` / `continue` for control flow.
8. **Lists:** Access with `items[0]` and `items[-1]`. Append with `.append()`, remove with `.pop()`. Slice with `seq[start:stop:step]` and reverse with `[::-1]`.
9. **Dictionaries:** Use `.get(key, default)` for safe lookups that never crash with `KeyError`. Iterate over `items()` for `(key, value)` pairs.
10. **Tuples & Sets:** Use immutable tuples for fixed records and instant hash keys. Use `set(items)` to strip duplicates with $O(1)$ membership checks, union (`|`), and intersection (`&`).
11. **Sorting:** Sort in-place with `list.sort()` or create a new sorted list with `sorted(iterable)`. Pass `reverse=True` for descending order. Works on lists, tuples, sets, strings, and dictionaries. Supply `key=func` for $O(n)$ single-element keys, or use `from functools import cmp_to_key` with `key=cmp_to_key(compare_func)` for custom two-argument pairwise comparators (-1, 0, 1).
12. **Unpacking & Destructuring:** Multiple assignment (`a, b = b, a`), capture leftovers with `*` (`head, *tail = items`), ignore values (`first, *_ = items`), and merge dictionaries with `{**defaults, **custom}`.
13. **Comprehensions:** Transform and filter concisely: `[x.lower() for x in names if x]`. Use dictionary comprehensions `{k: v for ...}` and set comprehensions similarly.
14. **Functions & Arguments:** Define with `def fn(a, b=default, *args, **kwargs):`. `*args` captures extra positional arguments into a tuple, while `**kwargs` captures keyword arguments into a dictionary.
15. **Async & Await:** Concurrency for I/O-bound tasks. Declare with `async def`, yield with `await`, run with `asyncio.run()`, and execute concurrently with `asyncio.gather()`. Never execute blocking synchronous code inside coroutines.
16. **Classes & OOP:** Define classes with `class Item:`, initialize attributes inside `def __init__(self, ...):`, and provide `__str__` or `__repr__` for clean display. For single or multiple inheritance (the diamond problem), resolve ancestors safely using cooperative `super().__init__(**kwargs)` and C3 Linearization MRO (`ClassName.__mro__`) rather than calling base classes directly.
17. **Modules & Imports:** Organize code into `.py` files. Use `from module import func` or `import module as alias`. Guard scripts with `if __name__ == "__main__":` and avoid `from module import *`.
18. **Virtual Environments:** Create isolated project environments with `python3 -m venv .venv`, activate with `source .venv/bin/activate` (or `.venv\Scripts\activate` on Windows), install dependencies from `requirements.txt` via `pip install -r requirements.txt`, and check with `sys.prefix != sys.base_prefix`. Never commit `.venv` to git.

---

© 2026 TechToday. Python Study Library.
