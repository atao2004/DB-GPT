"""Valkey vector store.

Requires a Valkey server with the valkey-search module loaded for vector
similarity search. Uses the valkey-glide client library.

To run Valkey with the search module::

    docker run -d --name valkey -p 6379:6379 valkey/valkey:latest \\
        --loadmodule /usr/lib/valkey/modules/valkey-search.so
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from dbgpt.core import Chunk, Embeddings
from dbgpt.core.awel.flow import Parameter, ResourceCategory, register_resource
from dbgpt.storage.vector_store.base import (
    _COMMON_PARAMETERS,
    _VECTOR_STORE_COMMON_PARAMETERS,
    VectorStoreBase,
    VectorStoreConfig,
)
from dbgpt.storage.vector_store.filters import (
    FilterCondition,
    FilterOperator,
    MetadataFilters,
)
from dbgpt.util.i18n_utils import _

logger = logging.getLogger(__name__)

_VALKEY_DEFAULT_INDEX_TYPE = "HNSW"
_VALKEY_DEFAULT_DISTANCE_METRIC = "COSINE"
_VALKEY_DEFAULT_KEY_PREFIX = "dbgpt_vec:"
_VALKEY_VECTOR_FIELD = "vector"
_VALKEY_CONTENT_FIELD = "content"
_VALKEY_METADATA_FIELD = "metadata"
_VALKEY_CHUNK_ID_FIELD = "chunk_id"
_VALKEY_METADATA_PREFIX = "meta_"


    def _create_client(self) -> Any:
        """Create a Valkey-glide client."""
        from glide import GlideClient, GlideClientConfiguration, NodeAddress

        config = self._vector_store_config
        node = NodeAddress(host=config.host, port=config.port)

        if config.password:
            from glide import ServerCredentials

            client_config = GlideClientConfiguration(
                addresses=[node],
                use_tls=config.use_ssl,
                request_timeout=config.request_timeout,
                credentials=ServerCredentials(password=config.password),
                client_name="dbgpt_vector_store_client",
            )
        else:
            client_config = GlideClientConfiguration(
                addresses=[node],
                use_tls=config.use_ssl,
                request_timeout=config.request_timeout,
                client_name="dbgpt_vector_store_client",
            )

        # GlideClient.create() is async — run it in our dedicated loop
        return self._loop.run_until_complete(GlideClient.create(client_config))
