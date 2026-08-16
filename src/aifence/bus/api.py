# SPDX-License-Identifier: AGPL-3.0-or-later
# SAGE is dual-licensed under AGPL-3.0-or-later and a commercial license.
# Contact sage@digitalacre.org for commercial licensing.
from __future__ import annotations

from fastapi import APIRouter, Depends

from .api_learning import router as learning_router
from .api_memory import router as memory_router
from .api_semantic import router as semantic_router
from .api_transport import router as transport_router
from .security import require_api_key

router = APIRouter(prefix="/v1", dependencies=[Depends(require_api_key)])
for child in (transport_router, memory_router, learning_router, semantic_router):
    router.include_router(child)
