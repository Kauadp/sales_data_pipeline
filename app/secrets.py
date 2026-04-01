from pathlib import Path
from typing import Any, Mapping, Optional

try:
    import tomllib as toml
except ModuleNotFoundError:
    import toml  # type: ignore


_SECRETS_CACHE: Optional[Mapping[str, Any]] = None


def _find_secret_paths():
    project_root = Path(__file__).resolve().parents[1]
    return [
        project_root / "secrets.toml",
        project_root / ".streamlit" / "secrets.toml",
        Path(__file__).resolve().parent / "secrets.toml",
    ]


def load_secrets() -> Mapping[str, Any]:
    global _SECRETS_CACHE
    if _SECRETS_CACHE is not None:
        return _SECRETS_CACHE

    for path in _find_secret_paths():
        try:
            if path.exists():
                with path.open("rb") as fh:
                    _SECRETS_CACHE = toml.load(fh)
                    return _SECRETS_CACHE
        except Exception:
            continue

    _SECRETS_CACHE = {}
    return _SECRETS_CACHE


def get_secret(key: str, section: Optional[str] = None, default: Any = None) -> Any:
    # 1. Tenta via Streamlit (Funciona no Cloud e Local com .streamlit/secrets.toml)
    try:
        import streamlit as st
        if section:
            return st.secrets.get(section, {}).get(key, default)
        return st.secrets.get(key, default)
    except Exception:
        pass

    # 2. Fallback para arquivo manual (apenas se o streamlit não estiver rodando)
    data = load_secrets()
    if section:
        return data.get(section, {}).get(key, default)
    return data.get(key, default)