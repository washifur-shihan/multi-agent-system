from typing import Any, Optional
from app.config import settings

try:
    from supabase import create_client
except ImportError:
    create_client = None  # type: ignore


def _init_supabase() -> Optional[Any]:
    if not settings.has_supabase or create_client is None:
        return None
    try:
        return create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY,
        )
    except Exception as exc:
        print(f"⚠️ Supabase initialization skipped ({exc})")
        return None


supabase: Optional[Any] = _init_supabase()
