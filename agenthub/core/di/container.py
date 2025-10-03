"""Dependency injection container."""

import threading
from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")


class DIContainer:
    """Simple dependency injection container."""

    _instance: "DIContainer | None" = None
    _lock = threading.Lock()

    def __new__(cls) -> "DIContainer":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, "_initialized") or not getattr(
            self, "_initialized", False
        ):
            self._services: dict[type, Any] = {}
            self._factories: dict[type, Callable[[], Any]] = {}
            self._initialized = True

    def register_singleton(self, interface: type[T], instance: T) -> None:
        """Register a singleton instance."""
        self._services[interface] = instance

    def register_factory(self, interface: type[T], factory: Callable[[], T]) -> None:
        """Register a factory function."""
        self._factories[interface] = factory

    def get(self, interface: type[T]) -> T:
        """Get service instance."""
        # Check if singleton exists
        if interface in self._services:
            return self._services[interface]  # type: ignore[no-any-return]

        # Check if factory exists
        if interface in self._factories:
            instance = self._factories[interface]()
            # Cache as singleton
            self._services[interface] = instance
            return instance  # type: ignore[no-any-return]

        raise ValueError(f"No service registered for {interface}")

    def has(self, interface: type[T]) -> bool:
        """Check if service is registered."""
        return interface in self._services or interface in self._factories


# Global container instance
_container: DIContainer | None = None


def get_container() -> DIContainer:
    """Get the global DI container."""
    global _container
    if _container is None:
        _container = DIContainer()
    return _container
