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
