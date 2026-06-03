from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
import hashlib
import hmac
from datetime import UTC, datetime
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

from ..settings import PipelineConfig
from ..shared.models import PipelineStep


def _publish_targets(config: PipelineConfig, *, include_product_history: bool = False) -> dict[Path, str]:
    prefix = config.r2_object_prefix.strip("/")
    targets: dict[Path, str] = {
        config.store_day_publish: f"{prefix}/salg_fra_22_pr_dag_med_total.json",
        config.seller_day_publish: f"{prefix}/salg_pr_selger_fra_22_pr_dag.json",
        config.stock_publish: f"{prefix}/merged_stock_orders.json",
        config.meta_publish: f"{prefix}/tid.json",
    }
    if include_product_history and config.product_history_publish:
        targets[config.product_history_publish] = f"{prefix}/product_history.json"
    if config.product_day_publish:
        targets[config.product_day_publish] = f"{prefix}/product_day.json"
    return targets


def _resolve_access_keys() -> tuple[str, str] | None:
    access_key = os.getenv("HIBERNIAN_R2_ACCESS_KEY_ID") or os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("HIBERNIAN_R2_SECRET_ACCESS_KEY") or os.getenv("AWS_SECRET_ACCESS_KEY")
    if access_key and secret_key:
        return access_key, secret_key
    return None


def _request_json(url: str, *, method: str, token: str, payload: bytes | None = None, content_type: str | None = None) -> Any:
    headers = {
        "Authorization": f"Bearer {token}",
    }
    if content_type:
        headers["Content-Type"] = content_type

    request = Request(url, data=payload, method=method, headers=headers)
    try:
        with urlopen(request) as response:
            body = response.read()
    except HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Cloudflare R2 request failed ({exc.code} {exc.reason}): {error_body}") from exc

    if not body:
        return {}
    return json.loads(body.decode("utf-8"))


def _sign(key: bytes, message: str) -> bytes:
    return hmac.new(key, message.encode("utf-8"), hashlib.sha256).digest()


def _signing_key(secret_key: str, date_stamp: str, region: str, service: str) -> bytes:
    key_date = _sign(f"AWS4{secret_key}".encode("utf-8"), date_stamp)
    key_region = hmac.new(key_date, region.encode("utf-8"), hashlib.sha256).digest()
    key_service = hmac.new(key_region, service.encode("utf-8"), hashlib.sha256).digest()
    return hmac.new(key_service, b"aws4_request", hashlib.sha256).digest()


def _upload_via_s3(config: PipelineConfig, object_key: str, payload: bytes, access_key: str, secret_key: str) -> dict[str, Any]:
    region = "auto"
    service = "s3"
    host = f"{config.cloudflare_account_id}.r2.cloudflarestorage.com"
    encoded_key = quote(object_key, safe="/")
    canonical_uri = f"/{config.r2_bucket_name}/{encoded_key}"
    url = f"https://{host}{canonical_uri}"

    now = datetime.now(UTC)
    amz_datetime = now.strftime("%Y%m%dT%H%M%SZ")
    date_stamp = now.strftime("%Y%m%d")
    payload_hash = hashlib.sha256(payload).hexdigest()

    canonical_headers = (
        f"host:{host}\n"
        f"x-amz-content-sha256:{payload_hash}\n"
        f"x-amz-date:{amz_datetime}\n"
    )
    signed_headers = "host;x-amz-content-sha256;x-amz-date"
    canonical_request = (
        f"PUT\n{canonical_uri}\n\n{canonical_headers}\n{signed_headers}\n{payload_hash}"
    )
    credential_scope = f"{date_stamp}/{region}/{service}/aws4_request"
    string_to_sign = (
        "AWS4-HMAC-SHA256\n"
        f"{amz_datetime}\n"
        f"{credential_scope}\n"
        f"{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"
    )
    signature = hmac.new(
        _signing_key(secret_key, date_stamp, region, service),
        string_to_sign.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    authorization = (
        "AWS4-HMAC-SHA256 "
        f"Credential={access_key}/{credential_scope}, "
        f"SignedHeaders={signed_headers}, "
        f"Signature={signature}"
    )

    request = Request(
        url,
        data=payload,
        method="PUT",
        headers={
            "Authorization": authorization,
            "Content-Type": "application/json; charset=utf-8",
            "Host": host,
            "x-amz-content-sha256": payload_hash,
            "x-amz-date": amz_datetime,
        },
    )
    try:
        with urlopen(request) as response:
            return {
                "status": response.status,
                "etag": response.headers.get("ETag", "").strip('"'),
                "version_id": response.headers.get("x-amz-version-id"),
            }
    except HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Cloudflare R2 S3 upload failed ({exc.code} {exc.reason}): {error_body}") from exc


def _upload_url(config: PipelineConfig, object_key: str) -> str:
    encoded_key = quote(object_key, safe="/")
    return (
        f"https://api.cloudflare.com/client/v4/accounts/{config.cloudflare_account_id}"
        f"/r2/buckets/{config.r2_bucket_name}/objects/{encoded_key}"
    )


def _public_url(config: PipelineConfig, object_key: str) -> str:
    encoded_key = quote(object_key, safe="/")
    return f"{config.r2_public_base_url.rstrip('/')}/{encoded_key}"


def publish_to_r2(config: PipelineConfig, *, include_product_history: bool = False) -> list[dict[str, Any]]:
    token = os.getenv("HIBERNIAN_CLOUDFLARE_API_TOKEN") or os.getenv("CLOUDFLARE_API_TOKEN")
    access_keys = _resolve_access_keys()
    uploaded: list[dict[str, Any]] = []

    for source, object_key in _publish_targets(config, include_product_history=include_product_history).items():
        if not source.exists():
            continue

        payload = source.read_bytes()
        result: Any
        mode: str
        if access_keys:
            access_key, secret_key = access_keys
            result = _upload_via_s3(config, object_key, payload, access_key, secret_key)
            mode = "s3"
        elif token:
            result = _request_json(
                _upload_url(config, object_key),
                method="PUT",
                token=token,
                payload=payload,
                content_type="application/json; charset=utf-8",
            )
            mode = "api"
        else:
            raise RuntimeError(
                "Missing R2 credentials. Set either HIBERNIAN_R2_ACCESS_KEY_ID/HIBERNIAN_R2_SECRET_ACCESS_KEY or HIBERNIAN_CLOUDFLARE_API_TOKEN."
            )
        uploaded.append(
            {
                "source": str(source),
                "object_key": object_key,
                "public_url": _public_url(config, object_key),
                "size": len(payload),
                "mode": mode,
                "result": result.get("result", result),
            }
        )

    return uploaded


def describe_step(config: PipelineConfig) -> PipelineStep:
    targets = _publish_targets(config)
    return PipelineStep(
        name="publish_r2",
        description="Upload publish artifacts to the Cloudflare R2 beta bucket.",
        inputs=tuple(str(source) for source in targets),
        outputs=tuple(_public_url(config, object_key) for object_key in targets.values()),
    )
