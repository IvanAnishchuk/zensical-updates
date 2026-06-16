"""Core implementation for zensical-updates.

Everything public is re-exported from the package root
(`zensical_updates`) — import from there, not from this private
module. Replace the example `greet` / `Greeter` below with the real library API.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["Greeter", "greet"]


def greet(name: str = "world", *, shout: bool = False) -> str:
    """Return a friendly greeting.

    Args:
        name: Who to greet.
        shout: If ``True``, upper-case the result for emphasis.

    Returns:
        The greeting, e.g. ``"Hello, world!"``.

    Examples:
        >>> greet("Ada")
        'Hello, Ada!'
        >>> greet("Ada", shout=True)
        'HELLO, ADA!'
    """
    message = f"Hello, {name}!"
    return message.upper() if shout else message


@dataclass(frozen=True, slots=True)
class Greeter:
    """A reusable greeter with a fixed style.

    Bundles greeting options so the same configuration can be applied across
    many calls.

    Attributes:
        shout: Whether `greet` upper-cases its output.
    """

    shout: bool = False

    def greet(self, name: str = "world") -> str:
        """Greet ``name`` using this greeter's configured style.

        Args:
            name: Who to greet.

        Returns:
            The greeting string.
        """
        return greet(name, shout=self.shout)
