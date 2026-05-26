from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from flask import Flask, jsonify, request

app = Flask(__name__)



SERVER_SECRET = os.environ.get("DEMO_SERVER_SECRET", "local-demo-secret").encode()
SESSIONS: Dict[str, bytes] = {}
EVENTS = []

DEFAULT_TPM_STATE: Dict[str, Any] = {
    "tpm_present": True,
    "secure_boot": True,
    "tee_agent_running": True,
    "sealed_key_available": True,
    "firmware_version": "TPM 2.0 / TEE Runtime 1.4.2",
    "device_id": "local-demo-device-001",
    "boot_counter": 28,
}
TPM_STATE = DEFAULT_TPM_STATE.copy()

TRUSTED_MEASUREMENT = "cross-chain-agent:v1.0.0"
SUPPORTED_CHAINS = ["Ethereum", "Arbitrum", "Optimism", "Polygon", "Base", "BSC"]
SUPPORTED_ASSETS = ["USDC", "ETH", "WETH", "DAI"]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_hex(data: str | bytes) -> str:
    if isinstance(data, str):
        data = data.encode()
    return hashlib.sha256(data).hexdigest()


def b64e(data: bytes) -> str:
    return base64.b64encode(data).decode()


def b64d(data: str) -> bytes:
    return base64.b64decode(data.encode())


def sign_like_tpm(payload: Dict[str, Any]) -> str:
    """Demo HMAC signature used to mimic TPM attestation signing."""
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode()
    return hmac.new(SERVER_SECRET, raw, hashlib.sha256).hexdigest()


def current_pcrs() -> Dict[str, str]:
    # PCR-like values are deterministic hashes of the current simulated state.
    pcr0_seed = "bios:clean" if TPM_STATE["tpm_present"] else "bios:missing"
    pcr7_seed = "secure_boot:on" if TPM_STATE["secure_boot"] else "secure_boot:off"
    pcr11_seed = TRUSTED_MEASUREMENT if TPM_STATE["tee_agent_running"] else "agent:stopped"
    return {
        "PCR0_boot_firmware": "0x" + sha256_hex(f"{pcr0_seed}:{TPM_STATE['boot_counter']}")[:16],
        "PCR7_secure_boot": "0x" + sha256_hex(f"{pcr7_seed}:{TPM_STATE['device_id']}")[:16],
        "PCR11_tee_agent": "0x" + sha256_hex(pcr11_seed)[:16],
    }


def build_quote(nonce: str | None = None) -> Dict[str, Any]:
    nonce = nonce or uuid.uuid4().hex[:16]
    pcrs = current_pcrs()
    quote_body = {
        "quote_id": "quote-" + uuid.uuid4().hex[:10],
        "nonce": nonce,
        "device_id": TPM_STATE["device_id"],
        "timestamp": now_iso(),
        "firmware_version": TPM_STATE["firmware_version"],
        "pcrs": pcrs,
        "measurement": TRUSTED_MEASUREMENT if TPM_STATE["tee_agent_running"] else "untrusted-or-stopped-agent",
        "claims": {
            "tpm_present": TPM_STATE["tpm_present"],
            "secure_boot": TPM_STATE["secure_boot"],
            "tee_agent_running": TPM_STATE["tee_agent_running"],
            "sealed_key_available": TPM_STATE["sealed_key_available"],
        },
    }
    quote_body["quote_hash"] = "0x" + sha256_hex(json.dumps(quote_body, sort_keys=True))
    quote_body["signature"] = "tpm-demo-hmac:" + sign_like_tpm(quote_body)
    quote_body["verified"] = verify_quote(quote_body)["ok"]
    return quote_body


def verify_quote(quote: Dict[str, Any]) -> Dict[str, Any]:
    claims = quote.get("claims", {})
    reasons = []
    if not claims.get("tpm_present"):
        reasons.append("TPM is not present")
    if not claims.get("secure_boot"):
        reasons.append("Secure Boot is disabled")
    if not claims.get("tee_agent_running"):
        reasons.append("TEE relay agent is not running")
    if not claims.get("sealed_key_available"):
        reasons.append("TPM-sealed key is unavailable")
    if quote.get("measurement") != TRUSTED_MEASUREMENT:
        reasons.append("TEE agent measurement does not match trusted baseline")
    return {"ok": len(reasons) == 0, "reasons": reasons}


def error(message: str, status: int = 400):
    response = jsonify({"ok": False, "error": message})
    response.status_code = status
    return response


@app.after_request
def add_cors_headers(response):
    # Minimal CORS support for Vite dev server.
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"ok": True, "service": "secure-crosschain-tpm-demo", "time": now_iso()})



@app.route("/api/crypto/encrypt", methods=["POST", "OPTIONS"])
def encrypt_message():
    if request.method == "OPTIONS":
        return ("", 204)

    data = request.get_json(force=True)
    message = data.get("message", "")
    source_chain = data.get("source_chain", "Ethereum")
    target_chain = data.get("target_chain", "Arbitrum")
    receiver = data.get("receiver", "")

    if not message.strip():
        return error("message is required")

    if not TPM_STATE["sealed_key_available"]:
        return error("TPM-sealed key is unavailable, cannot encrypt message")

    session_id = "sess-" + uuid.uuid4().hex[:12]
    key = AESGCM.generate_key(bit_length=128)
    SESSIONS[session_id] = key

    aad = f"{source_chain}->{target_chain}|{receiver}".encode()
    nonce = os.urandom(12)
    cipher = AESGCM(key).encrypt(nonce, message.encode(), aad)

    return jsonify({
        "ok": True,
        "session_id": session_id,
        "algorithm": "AES-GCM-128 demo session key sealed by simulated TPM",
        "source_chain": source_chain,
        "target_chain": target_chain,
        "receiver": receiver,
        "aad": aad.decode(),
        "nonce": b64e(nonce),
        "ciphertext": b64e(cipher),
        "message_hash": "0x" + sha256_hex(message),
        "packet_hash": "0x" + sha256_hex(aad + nonce + cipher),
    })


@app.route("/api/crypto/decrypt", methods=["POST", "OPTIONS"])
def decrypt_message():
    if request.method == "OPTIONS":
        return ("", 204)

    data = request.get_json(force=True)
    session_id = data.get("session_id")
    nonce = data.get("nonce")
    ciphertext = data.get("ciphertext")
    aad = data.get("aad", "")

    if session_id not in SESSIONS:
        return error("unknown session_id, demo backend has no matching TPM-sealed session key")

    try:
        plain = AESGCM(SESSIONS[session_id]).decrypt(b64d(nonce), b64d(ciphertext), aad.encode())
        return jsonify({"ok": True, "plaintext": plain.decode(), "message_hash": "0x" + sha256_hex(plain)})
    except Exception:
        return error("decrypt failed: ciphertext, nonce, aad, or session key does not match")



@app.route("/api/tpm/status", methods=["GET"])
def tpm_status():
    quote = build_quote()
    verification = verify_quote(quote)
    return jsonify({
        "ok": True,
        "state": TPM_STATE,
        "pcrs": current_pcrs(),
        "trusted_measurement": TRUSTED_MEASUREMENT,
        "quote_preview": quote,
        "verification": verification,
    })


@app.route("/api/tpm/quote", methods=["POST", "OPTIONS"])
def tpm_quote():
    if request.method == "OPTIONS":
        return ("", 204)
    data = request.get_json(silent=True) or {}
    quote = build_quote(data.get("nonce"))
    return jsonify({"ok": True, "quote": quote, "verification": verify_quote(quote)})


@app.route("/api/tpm/update", methods=["POST", "OPTIONS"])
def update_tpm_state():
    if request.method == "OPTIONS":
        return ("", 204)
    data = request.get_json(force=True)
    for key in ["tpm_present", "secure_boot", "tee_agent_running", "sealed_key_available"]:
        if key in data:
            TPM_STATE[key] = bool(data[key])
    if "firmware_version" in data:
        TPM_STATE["firmware_version"] = str(data["firmware_version"])
    return jsonify({"ok": True, "state": TPM_STATE, "pcrs": current_pcrs()})


@app.route("/api/tpm/reset", methods=["POST", "OPTIONS"])
def reset_tpm_state():
    if request.method == "OPTIONS":
        return ("", 204)
    TPM_STATE.clear()
    TPM_STATE.update(DEFAULT_TPM_STATE.copy())
    TPM_STATE["boot_counter"] += 1
    return jsonify({"ok": True, "state": TPM_STATE, "pcrs": current_pcrs()})



@app.route("/api/crosschain/submit", methods=["POST", "OPTIONS"])
def submit_crosschain_message():
    if request.method == "OPTIONS":
        return ("", 204)

    data = request.get_json(force=True)
    source_chain = data.get("source_chain", "Ethereum")
    target_chain = data.get("target_chain", "Arbitrum")
    asset = data.get("asset", "USDC")
    receiver = data.get("receiver", "")
    amount = float(data.get("amount", 0) or 0)
    packet_hash = data.get("packet_hash", "")
    risk_level = data.get("risk_level", "low")

    quote = build_quote(nonce=sha256_hex(f"{source_chain}:{target_chain}:{packet_hash}")[:16])
    quote_verification = verify_quote(quote)

    reasons = []
    if source_chain == target_chain:
        reasons.append("source_chain and target_chain cannot be the same")
    if source_chain not in SUPPORTED_CHAINS or target_chain not in SUPPORTED_CHAINS:
        reasons.append("unsupported chain")
    if asset not in SUPPORTED_ASSETS:
        reasons.append("unsupported asset")
    if amount <= 0:
        reasons.append("amount must be greater than zero")
    if amount > 50000:
        reasons.append("amount exceeds demo policy limit 50,000")
    if not receiver:
        reasons.append("receiver is required")
    if not packet_hash.startswith("0x"):
        reasons.append("encrypted packet hash is missing or malformed")
    if risk_level == "high":
        reasons.append("manual risk policy is high")
    if not quote_verification["ok"]:
        reasons.extend(quote_verification["reasons"])

    approved = len(reasons) == 0
    tx_material = json.dumps({
        "source_chain": source_chain,
        "target_chain": target_chain,
        "asset": asset,
        "amount": amount,
        "receiver": receiver,
        "packet_hash": packet_hash,
        "quote_hash": quote["quote_hash"],
        "time": time.time(),
    }, sort_keys=True)
    tx_hash = "0x" + sha256_hex(tx_material)

    event = {
        "event": "TrustedCrossChainMessageAccepted" if approved else "TrustedCrossChainMessageRejected",
        "approved": approved,
        "source_chain": source_chain,
        "target_chain": target_chain,
        "asset": asset,
        "amount": amount,
        "receiver": receiver,
        "packet_hash": packet_hash,
        "attestation_quote_hash": quote["quote_hash"],
        "tx_hash": tx_hash,
        "reasons": reasons,
        "timestamp": now_iso(),
    }
    EVENTS.insert(0, event)
    del EVENTS[20:]

    return jsonify({
        "ok": True,
        "approved": approved,
        "event": event,
        "quote": quote,
        "verification": quote_verification,
        "policy": {
            "max_amount": 50000,
            "allowed_risk_levels": ["low", "medium"],
            "supported_chains": SUPPORTED_CHAINS,
            "supported_assets": SUPPORTED_ASSETS,
        },
    })


@app.route("/api/crosschain/events", methods=["GET"])
def crosschain_events():
    return jsonify({"ok": True, "events": EVENTS})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
