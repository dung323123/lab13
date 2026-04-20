from __future__ import annotations

import os
from typing import Any

try:
    from langfuse import get_client, observe

    class _LangfuseContextAdapter:
        def __init__(self) -> None:
            self._client = get_client()

        def update_current_trace(self, **kwargs: Any) -> None:
            self._client.update_current_trace(**kwargs)

        def update_current_observation(self, **kwargs: Any) -> None:
            # Langfuse v3 span updates do not accept "usage_details".
            # Preserve this data by attaching it to metadata.
            metadata = kwargs.get("metadata")
            usage_details = kwargs.get("usage_details")
            if usage_details is not None:
                merged_metadata: dict[str, Any] = {}
                if isinstance(metadata, dict):
                    merged_metadata.update(metadata)
                elif metadata is not None:
                    merged_metadata["metadata_raw"] = metadata
                merged_metadata["usage_details"] = usage_details
                metadata = merged_metadata

            allowed_keys = {"name", "input", "output", "metadata", "version", "level", "status_message"}
            span_kwargs = {k: v for k, v in kwargs.items() if k in allowed_keys}
            if metadata is not None:
                span_kwargs["metadata"] = metadata

            self._client.update_current_span(**span_kwargs)

    langfuse_context = _LangfuseContextAdapter()
except Exception:  # pragma: no cover
    def observe(*args: Any, **kwargs: Any):
        def decorator(func):
            return func
        return decorator

    class _DummyContext:
        def update_current_trace(self, **kwargs: Any) -> None:
            return None

        def update_current_observation(self, **kwargs: Any) -> None:
            return None

    langfuse_context = _DummyContext()


def tracing_enabled() -> bool:
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))
