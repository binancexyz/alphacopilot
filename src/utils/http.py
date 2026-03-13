from __future__ import annotations


def make_httpx_client(*, error_cls=RuntimeError, error_msg="httpx is required", **kwargs):
    try:
        import httpx  # type: ignore
    except ModuleNotFoundError as exc:
        raise error_cls(error_msg) from exc
    return httpx.Client(**kwargs)
