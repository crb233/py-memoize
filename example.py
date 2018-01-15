from memoize import Memoizer

memoized = Memoizer()

@memoized
def fib(n):
    if n <= 1: return n
    return fib(n - 1) + fib(n - 2)

@memoized
def choose(n, k):
    if k < 0 or k > n: return 0
    if k == 0 or k == n: return 1
    return choose(n - 1, k - 1) + choose(n - 1, k)
