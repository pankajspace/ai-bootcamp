<!--
Source: python-my-course.html
Title: Python My Course | TechToday
Description: Fast-track Python essentials for everyday programming — variables, type hints, keywords, strings, operators, loops, lists, dictionaries, sorting, tuples, sets, unpacking & destructuring, comprehensions, functions, async/await, OOP, error handling, modules & imports, virtual environments, decorators, generators, context managers & file I/O, dataclasses & Pydantic, regular expressions, environment variables & logging, testing with pytest, and the standard library toolkit.
-->

Navigation: [TechToday](../../../index.html) · [← Programming Languages](../programming-languages.html)

<a id="python-my-course"></a>

# Python My Course

The high-yield Python course reference: common everyday syntax, type hints, keywords, core collections, functions, async/await concurrency, practical OOP solutions, error handling, modules & imports, virtual environments, decorators, generators, context managers, data models, regex, configuration & logging, testing, and the standard-library toolkit used in real projects.

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
13. [List, Dict & Set Comprehensions](#13-list-comprehensions)
14. [Functions & Arguments](#14-functions-and-arguments)
15. [Async / Await](#15-async-and-await)
16. [Object-Oriented Programming (OOP)](#16-object-oriented-programming)
17. [Modules & Imports](#17-modules-and-imports)
18. [Virtual Environments](#18-virtual-environments)
19. [Decorators](#19-decorators)
20. [Generators & Iterators](#20-generators-and-iterators)
21. [Context Managers & File I/O](#21-context-managers-and-file-io)
22. [Dataclasses, TypedDict & Pydantic](#22-dataclasses-typeddict-and-pydantic)
23. [Regular Expressions](#23-regular-expressions)
24. [Environment Variables, CLI & Logging](#24-environment-variables-cli-and-logging)
25. [Testing with pytest](#25-testing-with-pytest)
26. [Standard Library Toolkit](#26-standard-library-toolkit)

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
- **Generics & Legacy Forms** `TypeVar, Optional[X], Iterable[T]` <!-- good -->

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

Type hints you will meet constantly in real codebases (and in older code written before Python 3.10):

1. `from __future__ import annotations`: Placed at the top of a module, it postpones evaluation of all annotations, so `str | None` works on older Python versions and a class can reference itself in its own method signatures.
2. Legacy `typing` spellings: `Optional[str]` is `str | None`, `Union[int, str]` is `int | str`, and `List[str]` / `Dict[str, Any]` are `list[str]` / `dict[str, Any]`. Read them fluently, but prefer the modern forms in new code.
3. `Any`: Opts a value out of type checking — handy for raw JSON (`dict[str, Any]`), but use it sparingly.
4. `Iterable[T]` / `Iterator[T]`: Import from `collections.abc` to accept any iterable (lists, tuples, generators) instead of demanding a `list`.
5. `TypeVar`: Links input and output types in generic functions: `def first(items: list[T]) -> T`.
6. `TypedDict` & Pydantic: Describe dictionary shapes and validated models (see topic 22).

```python
from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Optional, TypeVar

# Legacy spelling seen in older code (identical to: str | None)
def find_city(code: str) -> Optional[str]:
    return {"BOM": "Mumbai"}.get(code)

print(find_city("BOM"), find_city("XYZ"))  # Mumbai None

# Accept any iterable, not just lists
def total_tokens(counts: Iterable[int]) -> int:
    return sum(counts)

print(total_tokens([120, 80]), total_tokens(n for n in (5, 5)))  # 200 10

# TypeVar: the return type follows the argument type
T = TypeVar("T")

def first_or_default(items: list[T], default: T) -> T:
    return items[0] if items else default

print(first_or_default(["gpt-4o", "llama3"], "none"))  # gpt-4o
print(first_or_default([], 0))  # 0

# Forward reference: a class can mention itself thanks to postponed annotations
class Node:
    def __init__(self, value: Any, next_node: Node | None = None):
        self.value = value
        self.next_node = next_node

print(Node(1, Node(2)).next_node.value)  # 2
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
- **Custom & Chained** `class AppError(Exception), raise ... from err` <!-- good -->

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

Production code (agents, tools, APIs) relies on a few more error-handling patterns:

1. `try / except / else / finally`: The `else` block runs only when no exception was raised, keeping the `try` block focused on the one risky line.
2. Custom exception classes: Subclass `Exception` to create a domain-specific hierarchy (`class AssessorError(Exception)`, `class LLMResponseError(AssessorError)`); catching the base class catches every subclass.
3. `raise NewError(...) from err`: Chains exceptions: the original error is kept in `__cause__`, and the traceback shows both — essential when translating low-level errors into meaningful ones.
4. Bare `raise`: Inside `except`, re-raises the current exception unchanged after logging or cleanup.
5. Error boundaries: Tools called by an LLM agent should catch expected errors and return an error message (often JSON) instead of crashing the whole agent loop.

```python
import json

# Custom exception hierarchy for a package
class AssessorError(Exception):
    """Base error for the assessor package."""

class LLMResponseError(AssessorError):
    def __init__(self, message: str, raw: str):
        super().__init__(message)
        self.raw = raw

# try / except / else + exception chaining with `raise ... from`
def parse_llm_json(raw: str) -> dict:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as err:
        raise LLMResponseError("Model returned invalid JSON", raw=raw) from err
    else:  # runs only when no exception was raised
        return data

try:
    parse_llm_json("{not valid")
except AssessorError as err:  # the base class also catches subclasses
    print(type(err).__name__, "|", err, "|", type(err.__cause__).__name__)
    # LLMResponseError | Model returned invalid JSON | JSONDecodeError

print(parse_llm_json('{"ok": true}'))  # {'ok': True}

# Error boundary: a tool never crashes the agent loop
def safe_tool(payload: str) -> str:
    try:
        data = parse_llm_json(payload)
        return json.dumps({"ok": True, "keys": sorted(data)})
    except AssessorError as err:
        return json.dumps({"ok": False, "error": str(err)})

print(safe_tool('{"b": 1, "a": 2}'))  # {"ok": true, "keys": ["a", "b"]}
print(safe_tool("oops"))              # {"ok": false, "error": "Model returned invalid JSON"}
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

**Interview question**

*Write `parse_port(value: str) -> int` that raises a custom `ConfigError` when the value is not an integer (chained from the original `ValueError`) or is outside the range 1–65535.*

Define `class ConfigError(Exception)`. Convert with `int()` inside `try`, and in `except ValueError as err:` use `raise ConfigError(...) from err`. Check the range after a successful conversion.

**Answer — Custom Exception with Chaining**

```python
class ConfigError(Exception):
    pass

def parse_port(value: str) -> int:
    try:
        port = int(value)
    except ValueError as err:
        raise ConfigError(f"Port must be an integer, got {value!r}") from err
    if not 1 <= port <= 65535:
        raise ConfigError(f"Port out of range: {port}")
    return port

# Test cases
print(parse_port("8080"))  # 8080
for bad in ["http", "70000"]:
    try:
        parse_port(bad)
    except ConfigError as err:
        cause = type(err.__cause__).__name__ if err.__cause__ else None
        print(f"{err} | caused by: {cause}")
# Port must be an integer, got 'http' | caused by: ValueError
# Port out of range: 70000 | caused by: None
print("Parse port passed!")  # Parse port passed!
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
- **Format Specifiers** `f"{x:,.2f} {r:.1%} {s:<10}"` <!-- good -->

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

The part after the colon in an f-string is a **format specifier**. These are the ones used most for reports, metrics tables, and logs:

1. Decimals: `{x:.2f}` fixed decimals, `{x:,.2f}` adds thousands separators, `{n:,}` for integers.
2. Percentages: `{ratio:.1%}` multiplies by 100 and appends `%` (`0.457` → `45.7%`).
3. Signs & zero padding: `{delta:+.1f}` always shows the sign; `{n:03d}` pads with zeros (`007`).
4. Alignment: `{s:<10}` left, `{s:>10}` right, `{s:^10}` centre within 10 characters — ideal for aligned console tables.
5. Debugging: `{value!r}` uses `repr()` (shows quotes), and `{value=}` prints the expression and its value (Python 3.8+).
6. `textwrap.dedent`: Removes common indentation from triple-quoted strings, keeping multi-line prompts readable inside functions.

```python
import textwrap

price, ratio, big, delta = 1234.5678, 0.4567, 12_500_000, 3.27
print(f"{price:.2f}")   # 1234.57
print(f"{price:,.2f}")  # 1,234.57
print(f"{big:,}")       # 12,500,000
print(f"{ratio:.1%}")   # 45.7%
print(f"{delta:+.1f}")  # +3.3
print(f"{7:03d}")       # 007
print(f"[{'id':<6}|{'score':>7}|{'ok':^4}]")  # [id    |  score| ok ]

model = "gpt-4o"
print(f"{model!r}")  # 'gpt-4o'
print(f"{model=}")   # model='gpt-4o'

# Aligned metrics table
for name, score in [("faithfulness", 0.912), ("relevance", 0.78)]:
    print(f"{name:<14}{score:>7.1%}")
# faithfulness    91.2%
# relevance       78.0%

# Multi-line prompt without leading indentation
def build_prompt(question: str) -> str:
    return textwrap.dedent(f"""\
        You are a helpful assistant.
        Question: {question}""")

print(build_prompt("What is RAG?").splitlines())
# ['You are a helpful assistant.', 'Question: What is RAG?']
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
- **Loop Else** `for ... else: (runs if no break)` <!-- good -->

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

Two more loop tools that appear in search and retry logic:

1. `for ... else`: The `else` block runs only when the loop finishes without hitting `break` — a clean way to express "searched everything and found nothing".
2. `reversed(seq)`: Iterates a sequence backwards without copying it (e.g. newest messages first).

```python
# for ... else: else runs only if the loop did NOT break
for attempt in range(1, 4):
    if attempt == 2:
        print(f"Succeeded on attempt {attempt}")
        break
else:
    print("All attempts failed")
# Succeeded on attempt 2

for ticker in ["AAPL", "MSFT"]:
    if ticker == "TSLA":
        break
else:
    print("TSLA not found")  # TSLA not found

# reversed(): newest chat messages first
messages = ["hi", "how are you?", "fine"]
print([m for m in reversed(messages)])  # ['fine', 'how are you?', 'hi']
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
- **Specialised Dicts** `Counter, defaultdict(list), d1 | d2` <!-- good -->

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

The `collections` module and modern dict syntax remove most hand-written counting and grouping code:

1. `Counter(iterable)`: Counts hashable items; `.most_common(n)` returns the top `n` pairs, and missing keys count as `0` instead of raising `KeyError`.
2. `defaultdict(list)`: Creates a default value the first time a key is touched — perfect for grouping (`groups[key].append(item)`) without `if key not in groups` checks.
3. `d.setdefault(key, default)`: Returns the existing value or inserts and returns the default.
4. Dict comprehension: `{k: v for k, v in d.items() if cond}` builds or filters dictionaries in one line.
5. Merge operators (3.9+): `defaults | overrides` returns a merged dict (right side wins); `config |= overrides` updates in place.

```python
from collections import Counter, defaultdict

# Counting with Counter
labels = ["bug", "billing", "bug", "feature", "bug"]
counts = Counter(labels)
print(counts.most_common(2))  # [('bug', 3), ('billing', 1)]
print(counts["unknown"])      # 0 (missing keys count as zero)

# Grouping with defaultdict(list)
tickets = [("acme", "T1"), ("globex", "T2"), ("acme", "T3")]
by_customer: defaultdict[str, list[str]] = defaultdict(list)
for customer, ticket_id in tickets:
    by_customer[customer].append(ticket_id)
print(dict(by_customer))  # {'acme': ['T1', 'T3'], 'globex': ['T2']}

# setdefault: get-or-insert in one call
cache: dict[str, list[str]] = {}
cache.setdefault("acme", []).append("T4")
print(cache)  # {'acme': ['T4']}

# Dict comprehension and the merge operator
prices = {"apple": 1.2, "banana": 0.5, "mango": 2.0}
print({k: v for k, v in prices.items() if v >= 1})  # {'apple': 1.2, 'mango': 2.0}
defaults = {"temperature": 0.2, "max_tokens": 512}
print(defaults | {"temperature": 0.7})  # {'temperature': 0.7, 'max_tokens': 512}
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

**Interview question**

*Given evaluation records as `(stage, latency_ms)` tuples, return `(stage, count, average_ms)` for each stage, ordered by count (highest first). Average to one decimal place.*

Use `Counter` to count stages (its `.most_common()` gives the ordering) and a `defaultdict(int)` to accumulate total latency per stage, then compute averages in a list comprehension.

**Answer — Group & Aggregate with collections**

```python
from collections import Counter, defaultdict

def summarize_latency(records: list[tuple[str, int]]) -> list[tuple[str, int, float]]:
    counts = Counter(stage for stage, _ in records)
    totals: defaultdict[str, int] = defaultdict(int)
    for stage, ms in records:
        totals[stage] += ms
    return [(stage, n, round(totals[stage] / n, 1)) for stage, n in counts.most_common()]

# Test cases
records = [("retrieval", 120), ("llm", 900), ("retrieval", 80), ("tool", 300), ("llm", 1100), ("retrieval", 100)]
print(summarize_latency(records))
# [('retrieval', 3, 100.0), ('llm', 2, 1000.0), ('tool', 1, 300.0)]
print(summarize_latency([]))  # []
print("Summarize latency passed!")  # Summarize latency passed!
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

## 13. List, Dict & Set Comprehensions

- **Syntax** `[expression for item in iterable]` <!-- great -->
- **With Filter** `[expr for item in iterable if condition]` <!-- great -->
- **Readability** `Replaces 4 lines of loop with 1 line` <!-- good -->
- **Dict & Set Variants** `{k: v for ...}, {x for ...}` <!-- good -->

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

The same syntax builds dictionaries and sets, flattens nested lists, and (without brackets) produces lazy generator expressions:

1. Dict comprehension: `{key_expr: value_expr for item in items}` — build lookups such as `{u["id"]: u for u in users}`.
2. Set comprehension: `{expr for item in items}` — unique values, e.g. distinct domains or sources.
3. Flattening: `[x for row in rows for x in row]` — read the `for` clauses left to right, exactly like nested loops.
4. Generator expression: `sum(len(d) for d in docs)` — no brackets, no intermediate list (see topic 20).

```python
# Dict comprehension: build a lookup table
users = [{"id": 1, "name": "Ana"}, {"id": 2, "name": "Raj"}]
by_id = {u["id"]: u["name"] for u in users}
print(by_id)  # {1: 'Ana', 2: 'Raj'}

# Set comprehension: unique values
emails = ["A@x.com", "a@x.com", "b@y.com"]
domains = {e.split("@")[1].lower() for e in emails}
print(sorted(domains))  # ['x.com', 'y.com']

# Flattening nested lists (outer loop first, inner loop second)
batches = [["d1", "d2"], ["d3"], []]
flat = [doc for batch in batches for doc in batch]
print(flat)  # ['d1', 'd2', 'd3']

# Generator expression: no brackets, no intermediate list
print(sum(len(doc) for doc in flat))  # 6
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
- **Keyword-Only & Closures** `def fn(q, *, top_k=5), nonlocal` <!-- good -->

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

A few more function features used heavily in library and agent code:

1. Keyword-only parameters: Everything after a bare `*` must be passed by name (`def search(query, *, top_k=5)`), so call sites stay readable and argument order can change safely.
2. `lambda`: A one-expression anonymous function for `key=` arguments, callbacks, and small dispatch tables: `max(docs, key=lambda d: d["score"])`.
3. Closures & `nonlocal`: An inner function remembers variables from its enclosing function; `nonlocal` lets it rebind them (counters, factories, decorators).
4. `global`: Rebinds a module-level variable from inside a function. Prefer passing values or using a class — global mutable state is hard to test.
5. Mutable default gotcha: Defaults are evaluated once, at definition time: `def add(item, items=[])` shares one list across calls. Use `items: list | None = None` and create the list inside.

```python
# Keyword-only parameters: everything after * must be named
def search(query: str, *, top_k: int = 5, rerank: bool = False) -> str:
    return f"{query!r} top_k={top_k} rerank={rerank}"

print(search("refund policy", top_k=3))  # 'refund policy' top_k=3 rerank=False
try:
    search("refund policy", 3)
except TypeError as err:
    print(err)  # search() takes 1 positional argument but 2 were given

# lambda for key= arguments and dispatch tables
docs = [{"id": "a", "score": 0.4}, {"id": "b", "score": 0.9}]
print(max(docs, key=lambda d: d["score"])["id"])  # b
ops = {"add": lambda a, b: a + b, "mul": lambda a, b: a * b}
print(ops["mul"](6, 7))  # 42

# Closures: the inner function remembers `count`
def make_counter():
    count = 0
    def increment() -> int:
        nonlocal count  # rebind the enclosing variable instead of creating a local one
        count += 1
        return count
    return increment

next_id = make_counter()
print(next_id(), next_id(), next_id())  # 1 2 3

# Mutable default gotcha and the fix
def add_bad(item: str, items: list[str] = []) -> list[str]:
    items.append(item)
    return items

def add_good(item: str, items: list[str] | None = None) -> list[str]:
    items = [] if items is None else items
    items.append(item)
    return items

add_bad("a")
print(add_bad("b"))  # ['a', 'b'] (the same list is shared between calls!)
add_good("a")
print(add_good("b"))  # ['b']
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
- **Async Context & Streams** `async with, async for, Semaphore` <!-- good -->

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

Async SDKs (MCP clients, A2A agents, `httpx.AsyncClient`, streaming LLM responses) add a few more tools:

1. `async with`: Async context managers (`__aenter__` / `__aexit__`) open and close network sessions, e.g. `async with ClientSession(read, write) as session:`.
2. `async for`: Consumes async iterators and async generators, such as streamed LLM tokens or agent events.
3. `asyncio.Semaphore(n)`: Limits how many coroutines run a section at once — respect API rate limits while still using `gather()`.
4. `asyncio.wait_for(coro, timeout)`: Cancels a slow operation and raises `TimeoutError`.
5. `await asyncio.to_thread(fn, *args)`: Runs blocking synchronous code in a worker thread without freezing the event loop.

```python
import asyncio
import time

class FakeSession:  # stands in for an MCP ClientSession or httpx.AsyncClient
    async def __aenter__(self):
        print("session opened")
        return self

    async def __aexit__(self, exc_type, exc, tb):
        print("session closed")

    async def call_tool(self, name: str) -> str:
        await asyncio.sleep(0.01)
        return f"{name}: ok"

async def stream_tokens(text: str):  # an async generator
    for token in text.split():
        await asyncio.sleep(0)
        yield token

async def limited_fetch(sem: asyncio.Semaphore, i: int) -> int:
    async with sem:  # at most 2 coroutines inside this block at once
        await asyncio.sleep(0.01)
        return i * i

def blocking_io() -> str:
    time.sleep(0.02)  # legacy synchronous call (e.g. requests.get)
    return "legacy done"

async def main():
    async with FakeSession() as session:
        print(await session.call_tool("search"))
    # session opened
    # search: ok
    # session closed

    tokens = [tok async for tok in stream_tokens("hello from the agent")]
    print(tokens)  # ['hello', 'from', 'the', 'agent']

    sem = asyncio.Semaphore(2)
    print(await asyncio.gather(*(limited_fetch(sem, i) for i in range(5))))  # [0, 1, 4, 9, 16]

    try:
        await asyncio.wait_for(asyncio.sleep(1), timeout=0.05)
    except TimeoutError:
        print("timed out")  # timed out

    print(await asyncio.to_thread(blocking_io))  # legacy done

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
- **Properties & Class Methods** `@property, @classmethod, @staticmethod` <!-- good -->

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

Everyday class features beyond `__init__` and inheritance:

1. `@property`: Exposes a computed or read-only attribute accessed without parentheses (`doc.title`). Add an `@name.setter` to validate assignments.
2. `@classmethod`: Receives the class (`cls`) instead of an instance; the standard way to write alternative constructors such as `Store.load(path)` or `Config.from_json(raw)`.
3. `@staticmethod`: A plain helper function namespaced inside the class; it needs neither `self` nor `cls`.
4. Base class contract: A base class whose method raises `NotImplementedError` defines an interface that subclasses must implement (e.g. `Embedder.embed()`). `abc.ABC` with `@abstractmethod` enforces this at instantiation time.
5. More dunder methods: `__len__` enables `len(obj)`, `__eq__` customises `==`, and `__iter__` makes objects loopable.
6. `getattr` / `hasattr` / `setattr`: Read or write attributes by name at runtime (`getattr(resp, "usage", None)`), common when handling optional fields on SDK response objects.

```python
import json

class Embedder:
    """Base class: subclasses must implement embed()."""
    dim = 0

    def embed(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError

class KeywordEmbedder(Embedder):
    VOCAB = ("refund", "invoice", "delay")
    dim = len(VOCAB)

    def __init__(self, name: str = "keyword-v1"):
        self._name = name

    @property
    def name(self) -> str:  # read-only attribute: emb.name (no parentheses)
        return self._name

    @classmethod
    def from_json(cls, raw: str) -> "KeywordEmbedder":  # alternative constructor
        return cls(**json.loads(raw))

    @staticmethod
    def tokenize(text: str) -> list[str]:  # needs neither self nor cls
        return text.lower().split()

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [[float(self.tokenize(t).count(w)) for w in self.VOCAB] for t in texts]

    def __len__(self) -> int:
        return self.dim

emb = KeywordEmbedder.from_json('{"name": "kw-test"}')
print(emb.name, len(emb))                            # kw-test 3
print(emb.embed(["Refund delayed invoice refund"]))  # [[2.0, 1.0, 0.0]]

try:
    emb.name = "other"
except AttributeError as err:
    print(err)  # property 'name' of 'KeywordEmbedder' object has no setter

try:
    Embedder().embed(["x"])
except NotImplementedError:
    print("Base class must be subclassed")  # Base class must be subclassed

# Dynamic attribute access with safe defaults
print(getattr(emb, "dim", None), hasattr(emb, "usage"), getattr(emb, "usage", "n/a"))  # 3 False n/a
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

**Interview question**

*Implement a `Temperature` class that stores Celsius, validates assignments through a property setter (nothing below absolute zero, -273.15 °C), exposes a read-only `fahrenheit` property, and provides a `from_fahrenheit` class-method constructor.*

Store the value in `self._celsius`, assign through `self.celsius = ...` in `__init__` so the setter validates it, compute `fahrenheit` in a `@property` without a setter, and return `cls(...)` from the `@classmethod`.

**Answer — Properties & Class Methods**

```python
class Temperature:
    def __init__(self, celsius: float):
        self.celsius = celsius  # goes through the setter below

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        if value < -273.15:
            raise ValueError("Below absolute zero")
        self._celsius = value

    @property
    def fahrenheit(self) -> float:
        return round(self._celsius * 9 / 5 + 32, 2)

    @classmethod
    def from_fahrenheit(cls, f: float) -> "Temperature":
        return cls(round((f - 32) * 5 / 9, 2))

# Test cases
t = Temperature(25)
print(t.fahrenheit)  # 77.0
t.celsius = 100
print(t.fahrenheit)  # 212.0
print(Temperature.from_fahrenheit(98.6).celsius)  # 37.0
try:
    Temperature(-300)
except ValueError as err:
    print(err)  # Below absolute zero
print("Temperature property passed!")  # Temperature property passed!
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
- **Packages & Relative Imports** `from .config import settings` <!-- good -->

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

Multi-file projects organise modules into **packages** — the layout used by every project folder:

1. Packages: A folder with an `__init__.py` file is a package; `__init__.py` can be empty or re-export the package's public names.
2. Relative imports: Inside a package, `from .config import settings` imports a sibling module and `from ..utils import chunk` goes up one level. They only work when the file is imported as part of a package.
3. `python -m package.module`: Runs a module as part of its package from the project root. Running `python package/module.py` directly breaks relative imports with "attempted relative import with no known parent package".
4. `sys.path` tweaks: Scripts and notebooks sometimes call `sys.path.insert(0, project_root)` so sibling folders become importable; prefer running from the project root with `-m` or installing the project with `pip install -e .`.
5. Optional / lazy imports: Import heavy optional dependencies inside the function that needs them, or wrap them in `try / except ImportError` to fall back gracefully.

```text
project/
├── run_assessor.py          # entry point: from assessor.graph import build_graph
└── assessor/
    ├── __init__.py          # marks the folder as a package
    ├── config.py
    ├── llm.py               # from .config import settings
    └── graph.py             # from .llm import call_llm
```

```python
# assessor/llm.py: relative imports inside a package
from .config import settings  # sibling module in the same package
from . import prompts         # import a sibling module object

# Run from the project root:
#   python -m assessor.graph   -> works (graph.py runs as part of the package)
#   python assessor/graph.py   -> ImportError: attempted relative import with no known parent package

# Optional dependency with a graceful fallback
try:
    import numpy as np
except ImportError:  # numpy not installed
    np = None

def mean(values: list[float]) -> float:
    if np is not None:
        return float(np.mean(values))
    return sum(values) / len(values)
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

<a id="unit-6"></a>

## Unit 6 — Advanced Functions & Data Models

Decorators, lazy generators, resource-safe context managers and file I/O, and structured data models with dataclasses, TypedDict, and Pydantic.

<a id="19-decorators"></a>

## 19. Decorators

- **Function Wrapper** `@deco  ≡  fn = deco(fn)` <!-- great -->
- **Preserve Metadata** `@functools.wraps(fn)` <!-- great -->
- **Built-in Caching** `@lru_cache(maxsize=64)` <!-- good -->
- **Registration** `@tool, @mcp.tool, @app.get("/")` <!-- good -->

In Python, functions are first-class objects: you can pass them as arguments, return them from other functions, and store them in dictionaries. A **decorator** is simply a callable that takes a function and returns a replacement (usually a wrapper that adds behavior before or after the original call). Writing `@timer` above `def fetch():` is syntactic sugar for `fetch = timer(fetch)`.

Decorators are everywhere in AI and web projects: `@tool` turns a plain function into an LLM-callable tool (its docstring becomes the tool description), `@mcp.tool` registers MCP server tools, `@app.get("/health")` maps FastAPI routes, `@lru_cache` caches expensive API calls, `@pytest.fixture` provides test setup, and `@dataclass` generates class boilerplate.

> **Analogy** 🎬
>
> **Picture it — Gift Wrapping at the Checkout Counter**
>
> The gift (your function) stays exactly the same. The wrapping counter adds a box, a ribbon, and a greeting card around it (logging, timing, retries, caching). The recipient still opens the same gift — they just get some extras around it, and you can wrap any gift the same way without changing the gift itself.

Key everyday patterns:
1. Functions are objects: Pass them around like data: `handlers = {"add": add}`, `apply(fn, x)`.
2. `@decorator` syntax: `@log_calls` placed above `def add(...)` is exactly `add = log_calls(add)`.
3. Wrapper signature: Define `def wrapper(*args, **kwargs):` and call `fn(*args, **kwargs)` so the decorator works with any function signature.
4. `@functools.wraps(fn)`: Copies `__name__`, `__doc__`, and the signature onto the wrapper. Without it, frameworks that read the docstring (like `@tool`) and tracebacks see `wrapper` instead of your function.
5. Decorators with arguments: `@retry(times=3)` is a factory: `retry(times=3)` returns the actual decorator, which then receives the function (three nested levels).
6. Registration decorators: Store the function in a registry and return it unchanged. This is how `@tool`, `@mcp.tool`, and `@app.get` discover your functions.
7. `@functools.lru_cache(maxsize=N)`: Memoizes results of pure functions with hashable arguments; inspect with `.cache_info()` and reset with `.cache_clear()`.
8. Stacking order: Decorators apply bottom-up: `@a` over `@b` over `def f` means `f = a(b(f))`.

```python
import functools

# 1. A basic decorator: log every call and its result
def log_calls(fn):
    @functools.wraps(fn)  # keep fn's name and docstring on the wrapper
    def wrapper(*args, **kwargs):
        print(f"-> {fn.__name__}{args}")
        result = fn(*args, **kwargs)
        print(f"<- {fn.__name__} returned {result!r}")
        return result
    return wrapper

@log_calls
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

print(add(2, 3))
# -> add(2, 3)
# <- add returned 5
# 5
print(add.__name__, "|", add.__doc__)  # add | Add two numbers.

# 2. A decorator with arguments (factory -> decorator -> wrapper)
def retry(times: int = 3, exceptions: tuple = (ConnectionError,)):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return fn(*args, **kwargs)
                except exceptions as err:
                    print(f"Attempt {attempt} failed: {err}")
            raise RuntimeError(f"{fn.__name__} failed after {times} attempts")
        return wrapper
    return decorator

calls = {"count": 0}

@retry(times=3)
def flaky_api() -> str:
    calls["count"] += 1
    if calls["count"] < 3:
        raise ConnectionError("timeout")
    return "200 OK"

print(flaky_api())
# Attempt 1 failed: timeout
# Attempt 2 failed: timeout
# 200 OK

# 3. A registration decorator: how @tool / @mcp.tool / @app.get work
TOOLS: dict[str, dict] = {}

def tool(fn):
    TOOLS[fn.__name__] = {"fn": fn, "description": (fn.__doc__ or "").strip()}
    return fn  # returned unchanged

@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    return f"Sunny in {city}"

print(list(TOOLS))                          # ['get_weather']
print(TOOLS["get_weather"]["description"])  # Get the current weather for a city.
print(TOOLS["get_weather"]["fn"]("Pune"))   # Sunny in Pune

# 4. Built-in caching with lru_cache
@functools.lru_cache(maxsize=64)
def fetch_price(ticker: str) -> float:
    print(f"Calling API for {ticker}")
    return {"AAPL": 189.5, "MSFT": 410.2}.get(ticker, 0.0)

print(fetch_price("AAPL"))
# Calling API for AAPL
# 189.5
print(fetch_price("AAPL"))  # 189.5 (served from cache, no API call)
print(fetch_price.cache_info().hits)  # 1
```

- **Strength — Write Cross-Cutting Logic Once** Logging, timing, retries, caching, auth checks, and tool registration are written once and applied to any function with a single line, keeping business logic clean.
- **Weakness — Hidden Behavior & Lost Metadata** Forgetting `@functools.wraps` hides the original name and docstring (breaking `@tool` descriptions and debugging). `lru_cache` needs hashable arguments, never expires entries, and caching impure functions returns stale data.

**Interview question**

*Implement a `memoize` decorator (without using `lru_cache`) that caches results for both positional and keyword arguments, preserves the function name, and exposes the cache as `fn.cache`. Use it to compute `fib(50)` instantly.*

Build a hashable key from `args` and `tuple(sorted(kwargs.items()))`, store results in a dictionary captured by the wrapper's closure, and decorate the wrapper with `@functools.wraps(fn)`.

**Answer — Memoize Decorator**

```python
import functools

def memoize(fn):
    cache: dict = {}

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        key = (args, tuple(sorted(kwargs.items())))
        if key not in cache:
            cache[key] = fn(*args, **kwargs)
        return cache[key]

    wrapper.cache = cache
    return wrapper

@memoize
def fib(n: int) -> int:
    """Return the nth Fibonacci number."""
    return n if n < 2 else fib(n - 1) + fib(n - 2)

# Test cases
print(fib(50))         # 12586269025
print(len(fib.cache))  # 51
print(fib.__name__)    # fib
print(fib.__doc__)     # Return the nth Fibonacci number.
print("Memoize decorator passed!")  # Memoize decorator passed!
```

> **Key idea**
>
> A decorator is just `fn = decorator(fn)`. Always forward `*args, **kwargs`, always apply `@functools.wraps(fn)` to the wrapper, and only cache pure functions whose arguments are hashable.

---

<a id="20-generators-and-iterators"></a>

## 20. Generators & Iterators

- **Lazy Function** `yield value` <!-- great -->
- **Generator Expression** `sum(x for x in items)` <!-- great -->
- **First Match** `next((x for x in it if ok(x)), None)` <!-- good -->
- **Delegation** `yield from other_iterable` <!-- good -->

An **iterable** is anything you can loop over (lists, dicts, files, strings). An **iterator** hands out values one at a time through `next()` and raises `StopIteration` when it is exhausted. A **generator** is the easiest way to build an iterator: any function containing `yield` returns a generator object that produces values lazily, pausing its state between values.

Generators let you process huge files, paginated APIs, or streaming LLM tokens with constant memory. In real projects you will see them constantly: generator expressions inside `sum()`, `any()`, `max()`, and `", ".join()`; `next(...)` to find the first matching item; batching texts before sending them to an embeddings API; and `yield` inside `@contextmanager` functions.

> **Analogy** 🎬
>
> **Picture it — A Water Tap vs. a Water Tank**
>
> A list is a water tank: you must fill the whole tank before anyone drinks, and it takes space for every litre. A generator is a tap: water is produced only when someone opens it, one glass at a time, and the pipe never needs to hold the whole reservoir. Once the reservoir behind a tap is drained, though, you cannot rewind it — you need a new tap.

Key everyday patterns:
1. `yield`: Turns a function into a generator. Calling it runs nothing yet; the body executes up to the next `yield` each time a value is requested.
2. Paused state: Local variables survive between yields, so a generator naturally remembers where it was.
3. Single-use: A generator is exhausted after one pass. Call the generator function again (or use a list) if you need to iterate twice.
4. Generator expressions: `(expr for x in items if cond)` is the lazy cousin of a list comprehension. Pass it straight into `sum()`, `any()`, `all()`, `max()`, `min()`, or `"".join()` without square brackets.
5. `next(iterator, default)`: Grabs the next value, returning `default` instead of raising `StopIteration` — the idiomatic "first match or None".
6. `iter(iterable)`: Creates an iterator from any iterable; useful to peek at the first item.
7. `yield from`: Delegates to another iterable, yielding each of its values.
8. Pipelines: Chain generators (read → clean → filter → batch) so each item flows through every stage without building intermediate lists.
9. `itertools`: Ready-made lazy helpers: `islice`, `chain`, `groupby`, and `batched` (Python 3.12+).

```python
import itertools
from collections.abc import Iterator

# 1. Generator function: values are produced lazily, one per next()
def countdown(n: int) -> Iterator[int]:
    while n > 0:
        yield n
        n -= 1

gen = countdown(3)
print(next(gen))  # 3
print(next(gen))  # 2
print(list(gen))  # [1]
print(list(gen))  # [] (exhausted - generators are single-use)

# 2. Batching: the pattern used to send texts to an embeddings API in chunks
def batched(items: list[str], size: int) -> Iterator[list[str]]:
    for i in range(0, len(items), size):
        yield items[i:i + size]

docs = ["d1", "d2", "d3", "d4", "d5"]
for batch in batched(docs, 2):
    print(batch)
# ['d1', 'd2']
# ['d3', 'd4']
# ['d5']
print(list(itertools.batched(docs, 2)))  # [('d1', 'd2'), ('d3', 'd4'), ('d5',)]

# 3. Generator expressions feed aggregate functions without building a list
latencies_ms = [120, 340, 95, 410]
print(sum(ms for ms in latencies_ms if ms > 100))   # 870
print(any(ms > 400 for ms in latencies_ms))         # True
print(all(ms < 500 for ms in latencies_ms))         # True
print(max(len(w) for w in ["rag", "agent", "llm"]))  # 5

# 4. next() with a default: first match or None
tools = [{"name": "search"}, {"name": "calculator"}]
print(next((t for t in tools if t["name"] == "calculator"), None))  # {'name': 'calculator'}
print(next((t for t in tools if t["name"] == "weather"), None))     # None

# 5. A memory-flat pipeline with yield from
def read_lines(text: str) -> Iterator[str]:
    yield from text.splitlines()

def non_empty(lines: Iterator[str]) -> Iterator[str]:
    return (line.strip() for line in lines if line.strip())

raw = "alpha\n\n  beta  \ngamma\n"
print(list(non_empty(read_lines(raw))))  # ['alpha', 'beta', 'gamma']
```

- **Strength — Constant Memory & Composability** Generators process one item at a time, so a 10 GB log file or an endless token stream uses the same memory as a tiny one, and small generator stages compose into readable pipelines.
- **Weakness — Single-Use and Lazy Errors** Generators have no `len()` or indexing, are exhausted after one loop, and defer errors until values are consumed. Printing one shows `<generator object ...>` instead of its contents.

**Interview question**

*Write a generator `read_jsonl(lines)` that yields parsed records from JSON Lines text (one JSON object per line), skipping blank and malformed lines. Use it to compute the average `total_ms` without loading all records into a list.*

Loop over the lines, `strip()` each one, skip empty lines, and `yield json.loads(line)` inside a `try / except json.JSONDecodeError` block. Accumulate a running total and count while iterating.

**Answer — Stream JSON Lines**

```python
import json
from collections.abc import Iterable, Iterator

def read_jsonl(lines: Iterable[str]) -> Iterator[dict]:
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            continue

# Test cases
log = """{"trace_id": "a1", "total_ms": 120}
not-json

{"trace_id": "b2", "total_ms": 80}
{"trace_id": "c3", "total_ms": 100}"""

total = count = 0
for record in read_jsonl(log.splitlines()):
    total += record["total_ms"]
    count += 1
print(count, total / count)  # 3 100.0

print(next(read_jsonl(['{"ok": true}']), None))  # {'ok': True}
print(next(read_jsonl([]), None))                # None
print("Read JSONL generator passed!")  # Read JSONL generator passed!
```

> **Key idea**
>
> Use a list when you need to reuse, index, or `len()` the result; use a generator when you stream through values once. Drop the square brackets inside `sum()`, `any()`, `all()`, `max()`, and `"".join()`.

---

<a id="21-context-managers-and-file-io"></a>

## 21. Context Managers & File I/O

- **Guaranteed Cleanup** `with open(path) as f:` <!-- great -->
- **Explicit Encoding** `encoding="utf-8"` <!-- great -->
- **Pathlib Shortcuts** `path.read_text() / write_text()` <!-- good -->
- **Custom Manager** `@contextmanager + try / yield / finally` <!-- good -->

Files, database connections, locks, and network sessions must be released even when an error occurs halfway through. The `with` statement guarantees this: it calls the object's `__enter__` method at the start of the block and its `__exit__` method at the end — whether the block finishes normally, returns early, or raises an exception.

You will see `with` everywhere in real code: `with open(...)` for files, `with sqlite3.connect(...)` for transactions, `with lock:` for threads, `async with ClientSession(...)` for MCP clients, and custom `@contextmanager` functions that time a block of code (tracing spans).

> **Analogy** 🎬
>
> **Picture it — A Hotel Key-Card Slot**
>
> When you slide your key card into the slot by the door, the lights and AC switch on. When you leave — calmly, in a hurry, or during a fire alarm — pulling the card out switches everything off automatically. A `with` block is that slot: entering acquires the resource, and leaving always releases it, no matter how you leave.

Key everyday patterns:
1. `with open(path, mode, encoding="utf-8") as f:`: Opens a file and always closes it, even if an exception is raised inside the block.
2. File modes: `"r"` read (default), `"w"` create/overwrite, `"a"` append, `"x"` create only (fails if the file exists); add `"b"` for binary data (`"rb"`).
3. Reading: `f.read()` loads everything; `for line in f:` streams line by line with constant memory.
4. Writing: `f.write(text)` does not add a newline — append `"\n"` yourself.
5. Pathlib one-liners: `path.read_text(encoding=...)`, `path.write_text(...)`, `path.mkdir(parents=True, exist_ok=True)`, `path.exists()`, `path.glob("*.md")`, and the `/` join operator.
6. JSON & JSON Lines: `json.dump(obj, f, indent=2)` / `json.load(f)` for whole files; `.jsonl` files store one JSON object per line, ideal for append-only logs and traces.
7. CSV: `csv.DictReader` / `csv.DictWriter` map rows to dictionaries; open CSV files with `newline=""`. Values read from CSV are always strings.
8. Custom context managers: Decorate a generator with `@contextlib.contextmanager` and wrap the `yield` in `try / finally`, or implement `__enter__` / `__exit__` on a class.
9. Multiple resources: `with open(src) as fin, open(dst, "w") as fout:` manages both in one statement.

```python
import csv
import json
import time
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

with TemporaryDirectory() as tmp:  # the temp folder is deleted when the block exits
    data_dir = Path(tmp) / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    # 1. Write, append, and stream a text file (always pass an encoding)
    notes = data_dir / "notes.txt"
    with open(notes, "w", encoding="utf-8") as f:
        f.write("first line\n")
        f.write("second line\n")
    with open(notes, "a", encoding="utf-8") as f:
        f.write("appended line\n")

    with open(notes, encoding="utf-8") as f:
        for line in f:
            print(line.rstrip())
    # first line
    # second line
    # appended line

    # 2. Pathlib one-liners
    print(notes.read_text(encoding="utf-8").count("\n"))  # 3
    print(notes.exists(), notes.suffix)                   # True .txt

    # 3. JSON config file and an append-only JSON Lines log
    config_file = data_dir / "config.json"
    config_file.write_text(json.dumps({"model": "gpt-4o-mini", "temperature": 0.2}, indent=2), encoding="utf-8")
    with open(config_file, encoding="utf-8") as f:
        config = json.load(f)
    print(config["model"])  # gpt-4o-mini

    traces = data_dir / "traces.jsonl"
    for i, ms in enumerate([120, 95]):
        with traces.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"id": i, "ms": ms}) + "\n")
    print(traces.read_text(encoding="utf-8").splitlines())
    # ['{"id": 0, "ms": 120}', '{"id": 1, "ms": 95}']

    # 4. CSV with DictWriter / DictReader
    csv_file = data_dir / "survey.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["customer", "score"])
        writer.writeheader()
        writer.writerows([{"customer": "acme", "score": 9}, {"customer": "globex", "score": 4}])
    with open(csv_file, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    print(rows[0])  # {'customer': 'acme', 'score': '9'} (CSV values are always strings)

    print(sorted(p.name for p in data_dir.glob("*")))
    # ['config.json', 'notes.txt', 'survey.csv', 'traces.jsonl']

# 5. Custom context manager: try / yield / finally (a tracing span)
@contextmanager
def span(name: str, log: list[dict]):
    start = time.perf_counter()
    record = {"name": name}
    try:
        yield record  # the body of the with-block runs here
    finally:
        record["ms"] = round((time.perf_counter() - start) * 1000, 2)
        log.append(record)
        print(f"closed span {name}")

spans: list[dict] = []
with span("retrieve", spans) as rec:
    rec["hits"] = 5
# closed span retrieve
print(spans[0]["name"], spans[0]["hits"], "ms" in spans[0])  # retrieve 5 True

try:
    with span("generate", spans):
        raise TimeoutError("LLM timed out")
except TimeoutError as err:
    print(f"Caught: {err}")
# closed span generate
# Caught: LLM timed out
```

- **Strength — Deterministic Cleanup** Files are closed, locks released, and transactions committed or rolled back even when exceptions occur, with far less boilerplate than hand-written `try / finally` blocks.
- **Weakness — Encoding & Overwrite Surprises** Omitting `encoding="utf-8"` uses the platform default (e.g. cp1252 on Windows), causing `UnicodeDecodeError` on emojis or non-English text. Mode `"w"` silently truncates existing files, and `f.read()` loads huge files fully into memory.

**Interview question**

*Write a context manager `atomic_write(path)` that yields a file handle to a temporary file and only replaces the target file if the `with` block completes without errors, so a crash never leaves a half-written config file behind.*

Write to a sibling `.tmp` file inside the `try` block, call `os.replace(tmp, path)` after the `yield` succeeds (an atomic rename on the same filesystem), and delete any leftover temp file in `finally`.

**Answer — Atomic File Write**

```python
import os
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

@contextmanager
def atomic_write(path: Path, encoding: str = "utf-8"):
    tmp_path = path.with_name(path.name + ".tmp")
    try:
        with open(tmp_path, "w", encoding=encoding) as f:
            yield f
        os.replace(tmp_path, path)  # atomic rename on the same filesystem
    finally:
        if tmp_path.exists():
            tmp_path.unlink()

# Test cases
with TemporaryDirectory() as tmp:
    target = Path(tmp) / "settings.json"
    with atomic_write(target) as f:
        f.write('{"version": 1}')
    print(target.read_text(encoding="utf-8"))  # {"version": 1}

    try:
        with atomic_write(target) as f:
            f.write('{"version": 2, "broken": ')
            raise RuntimeError("crash mid-write")
    except RuntimeError:
        pass
    print(target.read_text(encoding="utf-8"))           # {"version": 1}
    print(sorted(p.name for p in Path(tmp).iterdir()))  # ['settings.json']
print("Atomic write passed!")  # Atomic write passed!
```

> **Key idea**
>
> Always open files with `with` and an explicit `encoding="utf-8"`. Use `"a"` for append-only logs and `"x"` when you must never overwrite. For any acquire/release pair you write yourself, use `@contextmanager` with `try / yield / finally`.

---

<a id="22-dataclasses-typeddict-and-pydantic"></a>

## 22. Dataclasses, TypedDict & Pydantic

- **Data Containers** `@dataclass` <!-- great -->
- **Mutable Defaults** `field(default_factory=list)` <!-- great -->
- **Dict Shapes** `class State(TypedDict)` <!-- good -->
- **Runtime Validation** `class Report(BaseModel)` <!-- great -->

Most application code passes structured records around: retrieved chunks, tool results, agent state, API payloads, and LLM structured outputs. Python gives you three complementary tools for describing them:

**`@dataclass`** (standard library) auto-generates `__init__`, `__repr__`, and `__eq__` from annotated fields, but performs no validation. **`TypedDict`** describes the keys and value types of a plain `dict` for type checkers, with zero runtime cost (LangGraph agent state is usually a `TypedDict`). **Pydantic `BaseModel`** (`pip install pydantic`) validates and coerces data at runtime, parses JSON, and generates JSON Schema — the backbone of LLM structured output (`llm.with_structured_output(Model)`) and FastAPI request bodies.

> **Analogy** 🎬
>
> **Picture it — Forms at a Government Office**
>
> A `TypedDict` is a sample form pinned to the wall: it shows what the boxes should contain, but nobody checks your copy. A dataclass is a pre-printed form with labelled boxes: the structure is fixed, but the clerk never reads what you wrote. Pydantic is the strict clerk at the counter: every box is checked, "29" is converted to the number 29, and an invalid form is handed back with a list of every mistake.

Key everyday patterns:
1. `@dataclass`: Declare typed fields; get `__init__`, `__repr__`, and `__eq__` for free.
2. `field(default_factory=list)`: Required for mutable defaults — `tags: list[str] = []` raises `ValueError` so instances never share one list.
3. `__post_init__`: Runs after the generated `__init__`; use it for normalisation or derived fields.
4. `@dataclass(frozen=True)`: Immutable and hashable instances (safe as dict keys); `asdict(obj)` converts to a dictionary.
5. `TypedDict`: Type hints for dict-shaped data; at runtime it is an ordinary `dict`. `total=False` makes every key optional.
6. Pydantic `BaseModel`: Fields are validated and coerced on construction; bad data raises `ValidationError` listing every problem.
7. `Field(...)`: Adds constraints (`ge`, `le`, `min_length`, `max_length`) and a `description` that is sent to the LLM in structured-output schemas.
8. Pydantic I/O: `model_dump()` → dict, `model_dump_json()` → JSON string, `Model.model_validate(dict)`, `Model.model_validate_json(text)`, and `Model.model_json_schema()`.
9. Which to choose: Dataclasses for trusted internal data, `TypedDict` for dict-based framework state, and Pydantic at trust boundaries (LLM output, HTTP requests, config files).

```python
from dataclasses import asdict, dataclass, field
from typing import Literal, TypedDict

from pydantic import BaseModel, Field, ValidationError

# 1. Dataclass: boilerplate-free record with safe mutable defaults
@dataclass
class Chunk:
    doc_id: str
    text: str
    score: float = 0.0
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        self.text = self.text.strip()

c = Chunk("policy-1", "  Vendors must encrypt data.  ")
print(c)  # Chunk(doc_id='policy-1', text='Vendors must encrypt data.', score=0.0, metadata={})
print(c == Chunk("policy-1", "Vendors must encrypt data."))  # True
print(asdict(c)["doc_id"])  # policy-1

@dataclass(frozen=True)
class ModelConfig:
    name: str
    temperature: float = 0.2

cfg = ModelConfig("gpt-4o-mini")
try:
    cfg.temperature = 0.9
except AttributeError as err:  # FrozenInstanceError is a subclass of AttributeError
    print(type(err).__name__)  # FrozenInstanceError

# 2. TypedDict: type hints for plain dicts (e.g. LangGraph agent state)
class AgentState(TypedDict, total=False):
    question: str
    documents: list[str]
    answer: str

state: AgentState = {"question": "What is RAG?"}
state["documents"] = ["doc-a", "doc-b"]
print(type(state).__name__, len(state))  # dict 2

# 3. Pydantic: runtime validation and coercion at trust boundaries
class RiskFinding(BaseModel):
    vendor: str = Field(description="Vendor company name")
    risk_level: Literal["low", "medium", "high"]
    score: int = Field(ge=0, le=100, description="Risk score 0-100")
    evidence: list[str] = Field(default_factory=list)

finding = RiskFinding(vendor="Acme", risk_level="high", score="87")  # "87" is coerced to 87
print(finding.score, type(finding.score).__name__)  # 87 int
print(finding.model_dump())
# {'vendor': 'Acme', 'risk_level': 'high', 'score': 87, 'evidence': []}

llm_json = '{"vendor": "Globex", "risk_level": "low", "score": 12, "evidence": ["SOC 2 report"]}'
parsed = RiskFinding.model_validate_json(llm_json)
print(parsed.evidence)  # ['SOC 2 report']

try:
    RiskFinding(vendor="Initech", risk_level="critical", score=150)
except ValidationError as err:
    print(err.error_count())                     # 2
    print([e["loc"][0] for e in err.errors()])  # ['risk_level', 'score']

schema = RiskFinding.model_json_schema()  # what with_structured_output() sends to the LLM
print(schema["required"])                           # ['vendor', 'risk_level', 'score']
print(schema["properties"]["score"]["description"])  # Risk score 0-100
```

- **Strength — Less Boilerplate, Safer Boundaries** Dataclasses remove hand-written `__init__` / `__repr__` / `__eq__`, while Pydantic turns untrusted JSON (LLM replies, HTTP bodies, config) into typed, validated objects with precise error messages and an automatic JSON Schema.
- **Weakness — No Validation Without Pydantic** Dataclasses and `TypedDict` never check types at runtime — `Chunk(doc_id=123, text=None)` is accepted silently. Pydantic adds a dependency and validation overhead, and lax coercion ("87" → 87) can hide sloppy upstream data unless you enable strict mode.

**Interview question**

*An LLM returns JSON for support-ticket triage. Define a Pydantic model `Triage` with `category` (one of `"billing"`, `"bug"`, `"feature"`), `priority` (integer 1–5), and `summary` (non-empty, at most 80 characters). Write `parse_triage(raw: str) -> Triage | None` that returns `None` and prints the names of the failing fields when the output is invalid.*

Use `Literal` for the category and `Field(ge=1, le=5)` / `Field(min_length=1, max_length=80)` for the constraints. Call `Triage.model_validate_json(raw)` inside `try / except ValidationError`, and read each error's `loc` tuple (an empty `loc` means the JSON itself was invalid).

**Answer — Validate LLM Output**

```python
from typing import Literal

from pydantic import BaseModel, Field, ValidationError

class Triage(BaseModel):
    category: Literal["billing", "bug", "feature"]
    priority: int = Field(ge=1, le=5)
    summary: str = Field(min_length=1, max_length=80)

def parse_triage(raw: str) -> Triage | None:
    try:
        return Triage.model_validate_json(raw)
    except ValidationError as err:
        fields = [str(e["loc"][0]) if e["loc"] else "<root>" for e in err.errors()]
        print(f"Invalid fields: {fields}")
        return None

# Test cases
ok = parse_triage('{"category": "bug", "priority": 2, "summary": "Login button crashes app"}')
print(ok.category, ok.priority)  # bug 2

bad = parse_triage('{"category": "spam", "priority": 9, "summary": ""}')
# Invalid fields: ['category', 'priority', 'summary']
print(bad)  # None

print(parse_triage("not json"))
# Invalid fields: ['<root>']
# None
print("Parse triage passed!")  # Parse triage passed!
```

> **Key idea**
>
> Validate at the boundary, trust inside: parse LLM responses, API payloads, and config with Pydantic once, then pass dataclasses or validated models through internal code. Never use a mutable literal (`[]`, `{}`) as a default — use `field(default_factory=...)` or `Field(default_factory=...)`.

---

<a id="unit-7"></a>

## Unit 7 — Production Toolkit

Regular expressions, configuration and logging, automated testing with pytest, and the everyday standard library used across real projects.

<a id="23-regular-expressions"></a>

## 23. Regular Expressions

- **Search & Validate** `re.search(), re.fullmatch()` <!-- great -->
- **Extract All** `re.findall(), re.finditer()` <!-- great -->
- **Replace** `re.sub(pattern, repl, text)` <!-- good -->
- **Precompile** `re.compile(pattern, re.I)` <!-- good -->

Regular expressions (the `re` module) are a mini-language for finding, validating, extracting, and replacing text that follows a pattern. String methods like `in`, `.startswith()`, and `.split()` handle fixed text; regex handles variable text such as "any email address" or "a JSON block wrapped in markdown fences".

In AI projects regex is used constantly: pulling JSON out of an LLM reply, redacting emails and API keys in guardrails, extracting ticker symbols or IDs, splitting documents on headings before chunking, and normalising whitespace in scraped text.

> **Analogy** 🎬
>
> **Picture it — A Metal Detector with Custom Settings**
>
> Scanning a beach by hand (manual string slicing) means digging up every square metre. A metal detector tuned to "coins between 2 and 3 cm" beeps only where something matches the shape you described. A regex is that tuned detector: describe the shape once, and it finds (or replaces) every match in the text.

Key everyday patterns:
1. Raw strings: Always write patterns as `r"\d+"` so backslashes reach the regex engine unchanged.
2. Building blocks: `\d` digit, `\w` word character, `\s` whitespace, `.` any character, `[A-Z]` a character class, `^` / `$` anchors, and `\b` word boundary.
3. Quantifiers: `*` (0+), `+` (1+), `?` (0 or 1), `{2,4}`; add `?` for non-greedy matching (`.*?`).
4. Groups: `(...)` captures, `(?P<name>...)` captures by name, `(?:...)` groups without capturing.
5. search vs match vs fullmatch: `re.search` finds the first match anywhere, `re.match` only at the start, and `re.fullmatch` requires the entire string to match (use it for validation).
6. Extract many: `re.findall` returns strings (or tuples of groups); `re.finditer` yields `Match` objects with positions.
7. Replace & split: `re.sub(pattern, repl, text)` where `repl` can be a string or a function; `re.split(pattern, text)` splits on any matching delimiter.
8. Flags: `re.I` ignore case, `re.S` (`re.DOTALL`) lets `.` match newlines, `re.M` makes `^` / `$` match on every line.
9. `re.compile` & `re.escape`: Compile patterns reused in loops once at module level; escape user input with `re.escape(text)` to match it literally.

```python
import json
import re

# 1. search with named groups, fullmatch for validation
m = re.search(r"(?P<ticker>[A-Z]{1,5}) closed at \$(?P<price>\d+\.\d{2})", "Today AAPL closed at $189.50.")
if m:
    print(m.group("ticker"), float(m.group("price")))  # AAPL 189.5
print(bool(re.fullmatch(r"[A-Z]{1,5}", "MSFT")))     # True
print(bool(re.fullmatch(r"[A-Z]{1,5}", "MSFT123")))  # False

# 2. findall / finditer for extraction (compile once, reuse many times)
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
text = "Contact sales@acme.com or support@acme.io for help."
print(EMAIL_RE.findall(text))                        # ['sales@acme.com', 'support@acme.io']
print([m.start() for m in EMAIL_RE.finditer(text)])  # [8, 26]

# 3. sub: redact PII, normalise whitespace, and mask secrets with a function
print(EMAIL_RE.sub("[EMAIL]", text))                          # Contact [EMAIL] or [EMAIL] for help.
print(re.sub(r"\s+", " ", "too   many \n\t spaces").strip())  # too many spaces
masked = re.sub(r"sk-[A-Za-z0-9]{8,}", lambda m: "sk-****" + m.group()[-4:], "key=sk-abc123XYZ7890")
print(masked)  # key=sk-****7890

# 4. Flags: IGNORECASE + DOTALL to pull a JSON block out of an LLM reply
reply = 'Sure! Here is the result:\n```JSON\n{"risk": "high",\n "score": 87}\n```'
block = re.search(r"```json\s*(\{.*?\})\s*```", reply, re.I | re.S)
print(json.loads(block.group(1)))  # {'risk': 'high', 'score': 87}

# 5. split on several delimiters; escape user input before embedding it in a pattern
print(re.split(r"[,;|]\s*", "rag, agents;mcp|evals"))  # ['rag', 'agents', 'mcp', 'evals']
print(re.escape("price (USD)?"))                       # price\ \(USD\)\?
```

- **Strength — Powerful Pattern Matching in One Line** A single pattern replaces dozens of lines of manual slicing and looping, compiled patterns are fast, and regex is the standard tool for PII redaction, log parsing, and cleaning LLM output.
- **Weakness — Hard to Read and Easy to Over-Match** Dense patterns are hard to maintain, greedy `.*` silently grabs too much, nested quantifiers can cause catastrophic backtracking, and regex is the wrong tool for parsing nested HTML or JSON — use a real parser for those.

**Interview question**

*Write `extract_json(reply: str) -> dict | None` that extracts the first JSON object from an LLM reply. The JSON may be wrapped in a fenced code block (with or without a `json` language tag) or embedded directly in prose. Return `None` if nothing parseable is found.*

Try a fenced-block pattern first (`re.I | re.S`, non-greedy `\{.*?\}`), then fall back to the widest brace span `\{.*\}`. Attempt `json.loads()` on each candidate and catch `json.JSONDecodeError`.

**Answer — Extract JSON from LLM Reply**

```python
import json
import re

FENCE_RE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.I | re.S)
BRACE_RE = re.compile(r"\{.*\}", re.S)

def extract_json(reply: str) -> dict | None:
    for pattern in (FENCE_RE, BRACE_RE):
        match = pattern.search(reply)
        if not match:
            continue
        candidate = match.group(1) if match.groups() else match.group(0)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue
    return None

# Test cases
print(extract_json('Here you go:\n```json\n{"answer": 42}\n```'))  # {'answer': 42}
print(extract_json('Result: {"status": "ok", "items": [1, 2]} as requested.'))
# {'status': 'ok', 'items': [1, 2]}
print(extract_json('```\n{"nested": {"a": 1}}\n```'))  # {'nested': {'a': 1}}
print(extract_json("No structured data here."))        # None
print(extract_json('Broken: {"a": 1,,}'))               # None
print("Extract JSON passed!")  # Extract JSON passed!
```

> **Key idea**
>
> Use raw strings, prefer `re.fullmatch` for validation, compile patterns you reuse, and reach for plain string methods first — use regex only when the text you need to match genuinely varies.

---

<a id="24-environment-variables-cli-and-logging"></a>

## 24. Environment Variables, CLI & Logging

- **Secrets & Config** `os.getenv("KEY", default)` <!-- great -->
- **.env Files** `load_dotenv()` <!-- great -->
- **CLI Flags** `argparse.ArgumentParser()` <!-- good -->
- **Diagnostics** `logging.getLogger(__name__)` <!-- good -->

Real scripts need configuration (API keys, model names, temperatures), command-line options, and diagnostics that can be switched on or off. Hardcoding these makes code insecure and impossible to reuse across laptops, CI, and production.

The standard toolkit is: environment variables via `os.getenv()` / `os.environ`, a local `.env` file loaded with `python-dotenv`, `argparse` for typed command-line flags, `sys.exit()` for failing fast, and the `logging` module for leveled diagnostics. Almost every agent, RAG pipeline, and API server in a real codebase starts with `load_dotenv()` followed by `os.getenv(...)` calls.

> **Analogy** 🎬
>
> **Picture it — A Rental Car's Adjustable Settings**
>
> The engine (your code) is identical for every driver. Each driver adjusts the seat and mirrors (environment variables and CLI flags) for their trip without opening the hood, and the dashboard warning lights (logging) report what is happening at the level of detail the driver chooses.

Key everyday patterns:
1. `os.getenv("NAME", "default")`: Returns the value or the default (`None` if omitted). `os.environ["NAME"]` raises `KeyError` when missing — use it for required secrets.
2. Values are strings: Convert explicitly: `int(os.getenv("MAX_RETRIES", "3"))`; parse booleans with `value.lower() in {"1", "true", "yes"}`, because `bool("false")` is `True`.
3. `.env` files: `pip install python-dotenv`, then `from dotenv import load_dotenv; load_dotenv()` copies `KEY=VALUE` lines into `os.environ` without overriding variables that are already set (pass `override=True` to force). Commit `.env.example`, never `.env`.
4. Fail fast: Validate required configuration at startup; `sys.exit("Missing OPENAI_API_KEY")` prints the message to stderr and exits with status 1.
5. `sys.argv` vs `argparse`: `sys.argv` is the raw list of arguments; `argparse` adds types, defaults, `choices`, boolean flags (`action="store_true"`), and a free `--help`.
6. Testable CLIs: `parser.parse_args(["--top-k", "8"])` accepts an explicit list, so tests do not need a real command line.
7. `logging` setup: Call `logging.basicConfig(level=..., format=...)` once in the entry-point script and use `logger = logging.getLogger(__name__)` in every module.
8. Log levels: `DEBUG < INFO < WARNING < ERROR < CRITICAL`; messages below the configured level are dropped. Inside `except`, `logger.exception(...)` also records the traceback.
9. `print` vs `logging`: Use `print()` for the program's actual output and `logging` (stderr by default) for diagnostics you may want to silence or redirect.

```python
import argparse
import logging
import os
import sys

# 1. Environment variables (always strings, so convert explicitly)
os.environ["MODEL_NAME"] = "gpt-4o-mini"  # normally set by the shell or a .env file
model = os.getenv("MODEL_NAME", "gpt-4o")
max_retries = int(os.getenv("MAX_RETRIES", "3"))
debug = os.getenv("DEBUG", "false").lower() in {"1", "true", "yes"}
print(model, max_retries, debug)  # gpt-4o-mini 3 False

# 2. Loading a .env file (pip install python-dotenv)
# from dotenv import load_dotenv
# load_dotenv()  # reads KEY=VALUE lines from .env into os.environ

# 3. Fail fast when a required secret is missing
def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        sys.exit(f"Missing required environment variable: {name}")  # exit status 1
    return value

try:
    require_env("SOME_MISSING_KEY")
except SystemExit as exc:  # caught here only to show the message
    print(exc.code)  # Missing required environment variable: SOME_MISSING_KEY

# 4. argparse: typed CLI options with defaults, choices, flags, and --help
parser = argparse.ArgumentParser(description="Run the vendor risk assessor")
parser.add_argument("vendor", help="Vendor name to assess")
parser.add_argument("--top-k", type=int, default=5, help="Chunks to retrieve")
parser.add_argument("--provider", choices=["openai", "groq"], default="openai")
parser.add_argument("--verbose", action="store_true")

args = parser.parse_args(["Acme Corp", "--top-k", "8", "--verbose"])  # scripts call parse_args()
print(args.vendor, args.top_k, args.provider, args.verbose)  # Acme Corp 8 openai True

# 5. logging: configure once at the entry point, then use module-level loggers
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("assessor")
logger.debug("Not shown: DEBUG is below the INFO level")
logger.info("Retrieved %d chunks for %s", 8, args.vendor)
# INFO assessor: Retrieved 8 chunks for Acme Corp
try:
    int("eight")
except ValueError as err:
    logger.warning("Bad --top-k value, using default: %s", err)
# WARNING assessor: Bad --top-k value, using default: invalid literal for int() with base 10: 'eight'
```

- **Strength — Same Code, Any Environment** Separating configuration from code lets one script run locally, in CI, and in production by swapping environment variables. `argparse` gives free validation and `--help`, and log levels silence noise without deleting statements.
- **Weakness — Leaked Secrets and Stringly-Typed Config** Committing `.env`, hardcoding keys in notebooks, or logging full request headers leaks credentials. Environment values are untyped strings, so `bool(os.getenv("DEBUG"))` is `True` even for `"false"`.

**Interview question**

*Write `load_settings(env)` that reads `OPENAI_API_KEY` (required), `MODEL_NAME` (default `"gpt-4o-mini"`), `TEMPERATURE` (float, default `0.2`, must be between 0 and 2), and `DEBUG` (true for `1/true/yes/on`). Collect every problem and raise a single `ValueError` listing them. Accept the environment as a mapping so the function is testable (pass `os.environ` in production).*

Read each key with `env.get(key, default)`, append error messages to a list instead of raising immediately, convert `TEMPERATURE` inside `try / except ValueError`, and raise once at the end if the error list is non-empty.

**Answer — Validated Settings Loader**

```python
from collections.abc import Mapping

TRUTHY = {"1", "true", "yes", "on"}

def load_settings(env: Mapping[str, str]) -> dict:
    errors = []
    api_key = env.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        errors.append("OPENAI_API_KEY is required")

    temperature = None
    try:
        temperature = float(env.get("TEMPERATURE", "0.2"))
        if not 0 <= temperature <= 2:
            errors.append("TEMPERATURE must be between 0 and 2")
    except ValueError:
        errors.append("TEMPERATURE must be a number")

    if errors:
        raise ValueError("; ".join(errors))
    return {
        "api_key": api_key,
        "model": env.get("MODEL_NAME", "gpt-4o-mini"),
        "temperature": temperature,
        "debug": env.get("DEBUG", "").strip().lower() in TRUTHY,
    }

# Test cases
settings = load_settings({"OPENAI_API_KEY": "sk-test", "DEBUG": "True"})
print(settings["model"], settings["temperature"], settings["debug"])  # gpt-4o-mini 0.2 True

try:
    load_settings({"TEMPERATURE": "hot"})
except ValueError as err:
    print(err)  # OPENAI_API_KEY is required; TEMPERATURE must be a number

try:
    load_settings({"OPENAI_API_KEY": "sk-test", "TEMPERATURE": "3"})
except ValueError as err:
    print(err)  # TEMPERATURE must be between 0 and 2
print("Load settings passed!")  # Load settings passed!
```

> **Key idea**
>
> Read configuration from the environment, validate required values at startup, and fail fast with a clear message. Use `print()` for program output and `logging` for diagnostics, and call `logging.basicConfig()` only once, in the entry-point script.

---

<a id="25-testing-with-pytest"></a>

## 25. Testing with pytest

- **Test Functions** `def test_x(): assert ...` <!-- great -->
- **Expected Errors** `with pytest.raises(ValueError):` <!-- great -->
- **Data-Driven** `@pytest.mark.parametrize` <!-- good -->
- **Setup & Fakes** `@pytest.fixture, monkeypatch, tmp_path` <!-- good -->

Automated tests prove that parsers, scoring functions, tools, and prompts-building code still work after every change. `pytest` (`pip install pytest`) is the de-facto standard: it discovers files named `test_*.py` and functions named `test_*`, and uses plain `assert` statements while showing the actual values when an assertion fails.

For AI applications, the key skill is isolating your logic from slow, costly, nondeterministic LLM and network calls: replace them with fakes via fixtures or `monkeypatch`, so unit tests run in milliseconds and always give the same answer. (Measuring model quality is a separate job for evaluation suites.)

> **Analogy** 🎬
>
> **Picture it — Crash Tests at the Car Factory**
>
> Every new car model goes through the same crash tests before it leaves the factory, using crash-test dummies instead of real people. Your test suite is that crash-test track: every code change drives through the same checks, and fake LLMs and APIs play the role of the dummies.

Key everyday patterns:
1. Running tests: `pytest` runs everything; `pytest tests/test_rag.py -q` one file; `pytest -k "cost"` by name; `pytest -x` stops at the first failure; `-v` lists each test.
2. Naming: Files `test_*.py`, functions `test_*`, optional grouping classes `Test*` (no `__init__`).
3. Plain `assert`: `assert result == expected`; use `pytest.approx(x)` when comparing floats.
4. `pytest.raises`: `with pytest.raises(ValueError, match="non-negative"):` asserts that the block raises that exception with a matching message.
5. `@pytest.mark.parametrize`: Runs one test function over many input/expected pairs; each pair is reported as a separate test.
6. `@pytest.fixture`: Reusable setup injected by parameter name; put shared fixtures in `conftest.py`.
7. Built-in fixtures: `tmp_path` (fresh temp directory), `monkeypatch` (set env vars, replace functions or attributes), and `capsys` (capture printed output).
8. Fake external services: Pass a fake LLM callable into your function, or `monkeypatch.setattr` the client method, so tests make zero network calls.
9. `unittest`: The standard-library alternative (`class TestX(unittest.TestCase)` with `self.assertEqual`); pytest runs these tests too.

```python
# test_pricing.py  -  run with:  pytest -q test_pricing.py
import os

import pytest

# --- code under test (normally imported, e.g. from pricing import estimate_cost) ---
def estimate_cost(input_tokens: int, output_tokens: int, usd_per_m_in: float, usd_per_m_out: float) -> float:
    if input_tokens < 0 or output_tokens < 0:
        raise ValueError("token counts must be non-negative")
    return input_tokens / 1e6 * usd_per_m_in + output_tokens / 1e6 * usd_per_m_out

def summarize(text: str, llm) -> str:
    return llm(f"Summarize: {text}").strip()

# 1. Plain assert + approx for floats
def test_estimate_cost_basic():
    assert estimate_cost(1_000_000, 0, 0.15, 0.60) == pytest.approx(0.15)

# 2. Expected exceptions
def test_negative_tokens_rejected():
    with pytest.raises(ValueError, match="non-negative"):
        estimate_cost(-1, 0, 0.15, 0.60)

# 3. One test function, many cases
@pytest.mark.parametrize(
    ("inp", "out", "expected"),
    [(0, 0, 0.0), (500_000, 0, 0.075), (0, 1_000_000, 0.60)],
)
def test_estimate_cost_cases(inp, out, expected):
    assert estimate_cost(inp, out, 0.15, 0.60) == pytest.approx(expected)

# 4. Fixture providing a fake LLM (no network, deterministic)
@pytest.fixture
def fake_llm():
    calls = []

    def _llm(prompt: str) -> str:
        calls.append(prompt)
        return "  A short summary.  "

    _llm.calls = calls
    return _llm

def test_summarize_uses_llm(fake_llm):
    assert summarize("long text", fake_llm) == "A short summary."
    assert fake_llm.calls == ["Summarize: long text"]

# 5. Built-in fixtures: monkeypatch (env vars) and tmp_path (temp directory)
def test_reads_config(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")  # restored automatically after the test
    cfg = tmp_path / "config.txt"
    cfg.write_text("model=gpt-4o-mini", encoding="utf-8")
    assert os.environ["OPENAI_API_KEY"] == "sk-test"
    assert cfg.read_text(encoding="utf-8").split("=")[1] == "gpt-4o-mini"
```

```bash
$ pytest -q test_pricing.py
.......                                                                  [100%]
7 passed in 0.02s
```

- **Strength — Fast, Readable Safety Net** Plain asserts, fixtures, and parametrization keep tests short. Fast deterministic tests with fake LLMs catch regressions in parsers, tools, and scoring logic before they reach users.
- **Weakness — Real API Calls and Over-Mocking** Tests that call real LLMs or web APIs are slow, cost money, need secrets, and fail randomly. On the other hand, mocking too much ends up testing the mock instead of real behavior.

**Interview question**

*Write parametrized pytest tests for `classify_nps(score: int) -> str`, which returns `"detractor"` for 0–6, `"passive"` for 7–8, and `"promoter"` for 9–10. Cover every boundary and verify that out-of-range scores raise `ValueError`.*

Use one `@pytest.mark.parametrize` test for the boundary values (0, 6, 7, 8, 9, 10) and a second parametrized test using `pytest.raises(ValueError, match=...)` for invalid scores.

**Answer — Parametrized NPS Tests**

```python
# test_nps.py  -  run with:  pytest -q test_nps.py
import pytest

def classify_nps(score: int) -> str:
    if not 0 <= score <= 10:
        raise ValueError(f"NPS score out of range: {score}")
    if score >= 9:
        return "promoter"
    if score >= 7:
        return "passive"
    return "detractor"

@pytest.mark.parametrize(
    ("score", "expected"),
    [(0, "detractor"), (6, "detractor"), (7, "passive"), (8, "passive"), (9, "promoter"), (10, "promoter")],
)
def test_classify_nps_boundaries(score, expected):
    assert classify_nps(score) == expected

@pytest.mark.parametrize("bad_score", [-1, 11, 100])
def test_classify_nps_rejects_out_of_range(bad_score):
    with pytest.raises(ValueError, match="out of range"):
        classify_nps(bad_score)

# $ pytest -q test_nps.py
# .........                                                              [100%]
# 9 passed in 0.01s
```

> **Key idea**
>
> Unit-test pure logic (parsers, scoring, tool functions) with fast tests, replace LLM and network calls with fakes via fixtures or `monkeypatch`, use `pytest.approx` for floats and `pytest.raises` for errors, and keep model-quality checks in a separate evaluation suite.

---

<a id="26-standard-library-toolkit"></a>

## 26. Standard Library Toolkit

- **Dates & Times** `datetime.now(timezone.utc), timedelta` <!-- great -->
- **Timing** `time.perf_counter()` <!-- great -->
- **IDs & Fingerprints** `uuid.uuid4(), hashlib.sha256()` <!-- good -->
- **Local Database** `sqlite3.connect(path)` <!-- good -->
- **Threads & Processes** `ThreadPoolExecutor, Lock, subprocess.run` <!-- good -->

Python ships with "batteries included": a large standard library that needs no `pip install`. Beyond `json`, `pathlib`, `re`, and `collections`, a handful of modules show up in almost every real project: `datetime` for timestamps, `time` for measuring latency, `uuid` and `hashlib` for IDs and content fingerprints, `statistics` for quick metrics, `sqlite3` for a zero-setup database, `concurrent.futures` / `threading` for parallel I/O, and `subprocess` for running other programs.

> **Analogy** 🎬
>
> **Picture it — A Fully Stocked Workshop Pegboard**
>
> Before buying a specialised power tool (a third-party package), look at the pegboard that came with the workshop. The tape measure (`time`), calendar (`datetime`), label maker (`uuid`), fingerprint scanner (`hashlib`), filing cabinet (`sqlite3`), and extra pairs of hands (threads) are already hanging there, tested and ready to use.

Key everyday modules:
1. `datetime`: `datetime.now(timezone.utc)` for timezone-aware timestamps (avoid the deprecated `datetime.utcnow()`), `timedelta` arithmetic, `.isoformat()` / `datetime.fromisoformat()`, `strftime` / `strptime`, and `zoneinfo.ZoneInfo("Asia/Kolkata")` for named time zones.
2. `time`: `time.perf_counter()` to measure durations (monotonic, high resolution); `time.time()` for wall-clock epoch timestamps; `time.sleep()` blocks the thread (use `asyncio.sleep` in async code).
3. `uuid` & `hashlib`: `uuid.uuid4()` for random unique session, trace, or thread IDs; `hashlib.sha256(text.encode()).hexdigest()` for deterministic fingerprints used in de-duplication and caching (never for storing passwords).
4. `statistics`: `mean`, `median`, `stdev`, and `quantiles` for quick metrics without NumPy.
5. `sqlite3`: A full SQL database in a single file (or `":memory:"`). Always use `?` placeholders for values, set `conn.row_factory = sqlite3.Row` for dict-like rows, and remember `with conn:` commits or rolls back a transaction but does not close the connection.
6. `concurrent.futures`: `ThreadPoolExecutor` runs blocking I/O (HTTP calls, file reads) in parallel from synchronous code; `pool.map` keeps results in input order. Guard shared mutable state with `threading.Lock`.
7. CPU-bound work: Threads do not speed up pure-Python CPU work on the standard (GIL) interpreter; use `ProcessPoolExecutor` or `multiprocessing` instead.
8. `subprocess.run`: Run external commands with a list of arguments, `capture_output=True, text=True`, and a `timeout`; avoid `shell=True` with untrusted input.

```python
import hashlib
import sqlite3
import statistics
import subprocess
import sys
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

# 1. datetime: timezone-aware timestamps and arithmetic
created = datetime(2026, 1, 15, 9, 30, tzinfo=timezone.utc)
expires = created + timedelta(days=30)
print(expires.isoformat())        # 2026-02-14T09:30:00+00:00
print((expires - created).days)   # 30
print(datetime.fromisoformat("2026-02-14T09:30:00+00:00") == expires)  # True
print(created.strftime("%d %b %Y"))  # 15 Jan 2026
now = datetime.now(timezone.utc)  # prefer this over the deprecated datetime.utcnow()

# 2. Measuring durations with perf_counter
start = time.perf_counter()
time.sleep(0.01)
elapsed_ms = (time.perf_counter() - start) * 1000
print(elapsed_ms >= 10)  # True

# 3. Unique IDs and content fingerprints
session_id = str(uuid.uuid4())
print(len(session_id), session_id.count("-"))  # 36 4
fingerprint = hashlib.sha256("Vendors must encrypt data.".encode("utf-8")).hexdigest()
print(len(fingerprint), fingerprint == hashlib.sha256(b"Vendors must encrypt data.").hexdigest())  # 64 True

# 4. Quick statistics
latencies = [120, 95, 410, 130, 101]
print(statistics.mean(latencies), statistics.median(latencies))  # 171.2 120

# 5. sqlite3: parameterized queries and dict-like rows
conn = sqlite3.connect(":memory:")  # or a file such as "trips.db"
conn.row_factory = sqlite3.Row
with conn:  # commits on success, rolls back on error
    conn.execute("CREATE TABLE bookings (id INTEGER PRIMARY KEY, city TEXT, nights INTEGER)")
    conn.executemany("INSERT INTO bookings (city, nights) VALUES (?, ?)", [("Goa", 3), ("Pune", 2), ("Goa", 4)])
city = "Goa"  # user input: always pass values through ? placeholders, never an f-string
row = conn.execute("SELECT city, SUM(nights) AS total FROM bookings WHERE city = ?", (city,)).fetchone()
print(row["city"], row["total"])  # Goa 7
conn.close()

# 6. Threads for blocking I/O, with a Lock protecting shared state
counter = {"done": 0}
lock = threading.Lock()

def fetch(url: str) -> int:
    time.sleep(0.01)  # stands in for a blocking HTTP call
    with lock:
        counter["done"] += 1
    return len(url)

urls = ["https://a.dev", "https://bb.dev", "https://ccc.dev"]
with ThreadPoolExecutor(max_workers=3) as pool:
    sizes = list(pool.map(fetch, urls))  # results keep input order
print(sizes, counter["done"])  # [13, 14, 15] 3

# 7. subprocess: run another program safely (list args, timeout, captured output)
result = subprocess.run(
    [sys.executable, "-c", "print('tests passed')"], capture_output=True, text=True, timeout=30
)
print(result.returncode, result.stdout.strip())  # 0 tests passed
```

- **Strength — Zero Dependencies, Battle-Tested** Standard-library modules need no installation, are stable across versions, and cover most daily utility needs — fewer dependencies mean fewer security updates and version conflicts.
- **Weakness — Subtle Defaults** Naive datetimes (no `tzinfo`) silently mix time zones and cannot be compared with aware ones (`TypeError`); `with sqlite3.connect()` does not close the connection; and threads do not speed up CPU-bound Python code on the standard interpreter.

**Interview question**

*Using only the standard library, implement a `TTLCache` class with `set(key, value)` and `get(key, default=None)` where entries expire `ttl_seconds` after being set (useful for caching stock prices or API responses). Make it testable without real waiting.*

Store `(expires_at, value)` tuples in a dictionary. Inject the clock as a constructor parameter that defaults to `time.monotonic`, so tests can pass a fake clock and advance time instantly. Delete expired entries lazily inside `get`.

**Answer — TTL Cache with Injectable Clock**

```python
import time
from collections.abc import Callable
from typing import Any

class TTLCache:
    def __init__(self, ttl_seconds: float, clock: Callable[[], float] = time.monotonic):
        self.ttl = ttl_seconds
        self.clock = clock
        self._data: dict[str, tuple[float, Any]] = {}

    def set(self, key: str, value: Any) -> None:
        self._data[key] = (self.clock() + self.ttl, value)

    def get(self, key: str, default: Any = None) -> Any:
        item = self._data.get(key)
        if item is None:
            return default
        expires_at, value = item
        if self.clock() >= expires_at:
            del self._data[key]
            return default
        return value

# Test cases with a fake clock: instant and deterministic
fake_now = [1000.0]
cache = TTLCache(ttl_seconds=60, clock=lambda: fake_now[0])
cache.set("AAPL", 189.5)
print(cache.get("AAPL"))  # 189.5
fake_now[0] += 59
print(cache.get("AAPL"))  # 189.5
fake_now[0] += 1
print(cache.get("AAPL"))  # None
print(cache.get("MSFT", "miss"))  # miss
print("TTL cache passed!")  # TTL cache passed!
```

> **Key idea**
>
> Store and compare timestamps as timezone-aware UTC, measure durations with `time.perf_counter()`, always use `?` placeholders in SQL, and use threads for blocking I/O but processes for CPU-heavy work.

---

## Daily Python Cheat Sheet

A quick checklist of the most common daily syntax:

1. **Variables, Types & Casting:** Python is dynamically typed. Check for emptiness with `if items:` or `if not items:`. Compare singletons with `if val is None:`. Cast explicitly with `int()`, `float()`, `str()`, `bool()`.
2. **Type Hints:** Annotate variables and functions: `def fn(x: int) -> str | None:`. Use `list[str]` and `dict[str, int]` for generic collections. Read legacy forms fluently (`Optional[X]` = `X | None`), accept `Iterable[T]` for inputs, and use `TypeVar` for generic helpers.
3. **Keywords:** Only 35 reserved words in Python (`keyword.kwlist`). Check with `keyword.iskeyword()`. Never name variables after keywords.
4. **Error Handling:** Catch expected issues with `try / except SpecificError:`. Use `else` for code that runs only when no exception occurs, and `finally` for cleanup. Never write bare `except: pass`. Define domain exceptions by subclassing `Exception`, and translate low-level errors with `raise AppError(...) from err`.
5. **Strings:** Format with `f"Hello {name}"`. Clean with `.strip()`, split into lists with `.split()`, join with `", ".join(list)`, and test substrings with `in` and `not in`. Format numbers with specifiers: `{x:,.2f}`, `{ratio:.1%}`, `{name:<10}`, and debug with `{value=}`.
6. **Conditionals & Operators:** Use `/` for float division, `//` for floor division, `%` for modulo, and `divmod()` for both. Use `is` and `is not` for identity (`val is None`), `==` and `!=` for values. Chain comparisons: `18 <= age < 65`.
7. **Loops:** Iterate cleanly with `for item in items:` or `for i, item in enumerate(items):`. Use `zip()` for parallel iteration, and `break` / `continue` for control flow.
8. **Lists:** Access with `items[0]` and `items[-1]`. Append with `.append()`, remove with `.pop()`. Slice with `seq[start:stop:step]` and reverse with `[::-1]`.
9. **Dictionaries:** Use `.get(key, default)` for safe lookups that never crash with `KeyError`. Iterate over `items()` for `(key, value)` pairs. Count with `Counter(items).most_common(n)`, group with `defaultdict(list)`, and merge with `defaults | overrides`.
10. **Tuples & Sets:** Use immutable tuples for fixed records and instant hash keys. Use `set(items)` to strip duplicates with $O(1)$ membership checks, union (`|`), and intersection (`&`).
11. **Sorting:** Sort in-place with `list.sort()` or create a new sorted list with `sorted(iterable)`. Pass `reverse=True` for descending order. Works on lists, tuples, sets, strings, and dictionaries. Supply `key=func` for $O(n)$ single-element keys, or use `from functools import cmp_to_key` with `key=cmp_to_key(compare_func)` for custom two-argument pairwise comparators (-1, 0, 1).
12. **Unpacking & Destructuring:** Multiple assignment (`a, b = b, a`), capture leftovers with `*` (`head, *tail = items`), ignore values (`first, *_ = items`), and merge dictionaries with `{**defaults, **custom}`.
13. **Comprehensions:** Transform and filter concisely: `[x.lower() for x in names if x]`. Use dictionary comprehensions `{k: v for ...}` and set comprehensions similarly. Flatten with `[x for row in rows for x in row]`, and drop the brackets for lazy generator expressions inside `sum()`, `any()`, and `max()`.
14. **Functions & Arguments:** Define with `def fn(a, b=default, *args, **kwargs):`. `*args` captures extra positional arguments into a tuple, while `**kwargs` captures keyword arguments into a dictionary. Force named arguments with a bare `*` (`def search(q, *, top_k=5)`), use `lambda` for `key=` callbacks, and never use mutable defaults like `items=[]`.
15. **Async & Await:** Concurrency for I/O-bound tasks. Declare with `async def`, yield with `await`, run with `asyncio.run()`, and execute concurrently with `asyncio.gather()`. Never execute blocking synchronous code inside coroutines. Use `async with` for sessions, `async for` for streams, `asyncio.Semaphore(n)` for rate limits, and `asyncio.to_thread()` for blocking calls.
16. **Classes & OOP:** Define classes with `class Item:`, initialize attributes inside `def __init__(self, ...):`, and provide `__str__` or `__repr__` for clean display. For single or multiple inheritance (the diamond problem), resolve ancestors safely using cooperative `super().__init__(**kwargs)` and C3 Linearization MRO (`ClassName.__mro__`) rather than calling base classes directly. Expose computed attributes with `@property`, write alternative constructors with `@classmethod`, and define interfaces with base methods that raise `NotImplementedError`.
17. **Modules & Imports:** Organize code into `.py` files. Use `from module import func` or `import module as alias`. Guard scripts with `if __name__ == "__main__":` and avoid `from module import *`. Inside packages, use relative imports (`from .config import settings`) and run modules from the project root with `python -m package.module`.
18. **Virtual Environments:** Create isolated project environments with `python3 -m venv .venv`, activate with `source .venv/bin/activate` (or `.venv\Scripts\activate` on Windows), install dependencies from `requirements.txt` via `pip install -r requirements.txt`, and check with `sys.prefix != sys.base_prefix`. Never commit `.venv` to git.
19. **Decorators:** `@deco` means `fn = deco(fn)`. Wrap with `def wrapper(*args, **kwargs)`, always add `@functools.wraps(fn)`, and cache pure functions with `@functools.lru_cache(maxsize=N)`.
20. **Generators & Iterators:** `yield` produces values lazily with constant memory. Generators are single-use; use `next((x for x in items if ok(x)), None)` for the first match and `yield from` to delegate.
21. **Context Managers & File I/O:** Always `with open(path, mode, encoding="utf-8") as f:`. Use `Path.read_text()` / `write_text()`, `json.load()` / `json.dump()`, `csv.DictReader`, and `@contextmanager` with `try / yield / finally` for custom cleanup.
22. **Dataclasses, TypedDict & Pydantic:** `@dataclass` for internal records (`field(default_factory=list)` for mutable defaults), `TypedDict` for dict-shaped state, and Pydantic `BaseModel` + `Field(...)` to validate LLM output and API input with `model_validate_json()`.
23. **Regular Expressions:** Use raw strings (`r"\d+"`), `re.fullmatch` for validation, `re.search` / `re.findall` for extraction, `re.sub` for redaction, flags `re.I | re.S`, and `re.compile` for reused patterns.
24. **Environment Variables, CLI & Logging:** Read config with `os.getenv("KEY", default)` after `load_dotenv()`, fail fast with `sys.exit("message")`, parse flags with `argparse`, and log with `logging.getLogger(__name__)` after one `basicConfig()` call.
25. **Testing with pytest:** Name files `test_*.py`, use plain `assert`, `pytest.approx` for floats, `pytest.raises` for errors, `@pytest.mark.parametrize` for cases, and fixtures / `monkeypatch` / `tmp_path` to fake LLMs, env vars, and files.
26. **Standard Library Toolkit:** `datetime.now(timezone.utc)` + `timedelta`, `time.perf_counter()` for latency, `uuid.uuid4()` for IDs, `hashlib.sha256()` for fingerprints, `sqlite3` with `?` placeholders, `ThreadPoolExecutor` for blocking I/O, and `subprocess.run([...], timeout=...)`.

---

© 2026 TechToday. Python Study Library.
