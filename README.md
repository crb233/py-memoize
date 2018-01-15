# Py Memoize

A small library for automatic memoization of Python functions using decorators

## Usage

```python
from memoize import Memoizer

memoized = Memoizer()

@memoized
def fib(n):
    if n <= 1: return n
    return fib(n - 1) + fib(n - 2)
```
