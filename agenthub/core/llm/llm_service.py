"""Deprecated compatibility shim over :mod:`agenthub.core.llm.service`.

``CoreLLMService`` subclasses :class:`LLMService` so existing type hints and
``isinstance`` checks keep working. New code should use ``LLMService``.

``get_shared_llm_service`` remains the supported process-wide accessor (it
is the de-facto composition root across the codebase) and now returns an
``LLMService``, created lazily and thread-safely.
"""

import logging
import threading
import warnings

from .service import LLMService
from .types import ModelDescriptor

logger = logging.getLogger(__name__)

_shared_llm_service: LLMService | None = None
_shared_lock = threading.Lock()


class CoreLLMService(LLMService):
    """Deprecated: use :class:`agenthub.core.llm.LLMService`.

    Kept one release for backward compatibility. Behavioral change from the
    legacy implementation: failures raise
    :class:`~agenthub.core.llm.errors.LLMError` instead of returning the
    literal string ``"AISuite not available"``.
    """

    def __init__(self, model: str | None = None, auto_detect: bool = True):
        warnings.warn(
            "CoreLLMService is deprecated; use agenthub.core.llm.LLMService",
            DeprecationWarning,
            stacklevel=2,
        )
        # auto_detect is retained for signature compatibility; detection is
        # always lazy now, so eager auto-detection no longer exists.
        del auto_detect
        super().__init__(model=model)

    def is_local_model(self) -> bool:
        """Deprecated: whether the selected model runs locally."""
        _, descriptor = self._selection()
        return descriptor.is_local

    def get_model_info(self) -> ModelDescriptor:
        """Deprecated: descriptor of the selected model."""
        _, descriptor = self._selection()
        return descriptor


def get_shared_llm_service(
    model: str | None = None, auto_detect: bool = True
) -> LLMService:
    """Get or create the shared LLM service instance (thread-safe).

    ``model``/``auto_detect`` only apply on first creation and are kept for
    backward compatibility.
    """
    del auto_detect
    global _shared_llm_service
    with _shared_lock:
        if _shared_llm_service is None:
            _shared_llm_service = LLMService(model=model)
            logger.debug("Created shared LLMService instance")
        return _shared_llm_service


def reset_shared_llm_service() -> None:
    """Reset the shared LLM service instance."""
    global _shared_llm_service
    with _shared_lock:
        _shared_llm_service = None
        logger.debug("Reset shared LLMService instance")
