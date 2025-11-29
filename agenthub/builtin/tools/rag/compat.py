"""
Compatibility helpers for older llama-index releases.

Some dataclasses in upstream llama-index (e.g. RefDocInfo,
SimpleVectorStoreData, SimpleGraphStoreData) inherit from DataClassJsonMixin
but in certain releases the mixin does not inject ``to_dict`` /
``from_dict`` helpers.  The persistence layer in our RAG tools expects those
methods to exist, so we patch them in when missing.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, is_dataclass
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


def _ensure_serialization_api(cls: type[T]) -> None:
    """Override ``to_dict`` / ``from_dict`` helpers for llama-index dataclasses."""

    if not is_dataclass(cls):
        return

    def _to_dict(self: T, **kwargs: Any) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def _from_dict(cls_: type[T], data: Any) -> T:
        if isinstance(data, str):
            data = json.loads(data)
        return cls_(**data)

    cls.to_dict = _to_dict  # type: ignore[attr-defined]
    cls.from_dict = _from_dict  # type: ignore[attr-defined]


def patch_llama_index_dataclasses() -> None:
    """Patch known llama-index dataclasses that miss serialization helpers."""

    targets = []

    try:
        from llama_index.core.storage.docstore.types import RefDocInfo

        targets.append(RefDocInfo)
    except Exception:  # pragma: no cover - defensive guard
        logger.debug(
            "Unable to import RefDocInfo for compatibility patch", exc_info=True
        )

    try:
        from llama_index.core.vector_stores.simple import SimpleVectorStoreData

        targets.append(SimpleVectorStoreData)
    except Exception:  # pragma: no cover
        logger.debug(
            "Unable to import SimpleVectorStoreData for compatibility patch",
            exc_info=True,
        )

    try:
        from llama_index.core.graph_stores.simple import SimpleGraphStoreData

        targets.append(SimpleGraphStoreData)
    except Exception:  # pragma: no cover
        logger.debug(
            "Unable to import SimpleGraphStoreData for compatibility patch",
            exc_info=True,
        )

    try:
        from llama_index.core.data_structs import IndexDict

        targets.append(IndexDict)
    except Exception:  # pragma: no cover
        logger.debug(
            "Unable to import IndexDict for compatibility patch",
            exc_info=True,
        )

    for cls in targets:
        _ensure_serialization_api(cls)


# Apply patches as soon as the module is imported.
patch_llama_index_dataclasses()
