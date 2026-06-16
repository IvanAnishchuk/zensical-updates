# Usage

Install the package and import the public API from
`zensical_updates`:

```python
from zensical_updates import Greeter, greet

greet("Ada")               # "Hello, Ada!"
greet("Ada", shout=True)   # "HELLO, ADA!"

greeter = Greeter(shout=True)
greeter.greet("Ada")       # "HELLO, ADA!"
```

The complete, supported surface is whatever is listed in
`zensical_updates.__all__`; see the [API Reference](api.md) for
full signatures and docstrings.
