

import logging
import aiohttp
import asyncio
import base64
import hmac
import hashlib
import uuid
from datetime import datetime
from vrage_api.vrage_api import VRageAPI



# Wrapper für vrage-api, um die alte Schnittstelle beizubehalten
class SpaceEngineersRemoteClient:
    def __init__(self, uri, key=None, api_endpoint="/vrageremote"):
        # Normalize scheme: REST endpoints use http/https (not ws)
        if uri.startswith("ws://"):
            uri = "http://" + uri[len("ws://"):]
        elif uri.startswith("wss://"):
            uri = "https://" + uri[len("wss://"):]
        self.uri = uri.rstrip('/')
        self.key = key
        self.api_endpoint = api_endpoint
        self.client = VRageAPI(self.uri, self.key, api_endpoint=self.api_endpoint)
        self.connected = False
        # Health metrics
        self.consecutive_failures: int = 0
        self.last_success_utc: float | None = None
        self.last_failure_utc: float | None = None
        self.last_error: str | None = None
        self._last_state_logged: bool | None = None
        self._last_log_utc: float = 0.0

    async def connect(self):
        # Log attempts only when state changes or at throttled intervals
        self._log_throttled(logging.INFO, f"[SE-Remote] Attempting to connect to {self.uri}")
        try:
            # Testverbindung: Status-Endpunkt aufrufen
            resp = await self.get_status()
            if resp is not None:
                self.connected = True
                self.consecutive_failures = 0
                self.last_success_utc = asyncio.get_event_loop().time()
                logging.info(f"[SE-Remote] Connected to {self.uri}")
            else:
                self.connected = False
                self.consecutive_failures += 1
                self.last_failure_utc = asyncio.get_event_loop().time()
                self._log_throttled(logging.WARNING, f"[SE-Remote] Could not connect to {self.uri} (no status response)")
        except Exception as e:
            self.connected = False
            self.consecutive_failures += 1
            self.last_failure_utc = asyncio.get_event_loop().time()
            self.last_error = str(e)
            self._log_throttled(logging.ERROR, f"[SE-Remote] Connection failed: {e}")

    async def disconnect(self):
        logging.info(f"[SE-Remote] Disconnect called for {self.uri}")
        # vrage-api verwaltet Sessions selbst, kein explizites Close nötig
        self.connected = False

    def get_health_summary(self) -> str:
        """Return a short human-readable health summary for logging or UI."""
        parts = [f"connected={self.connected}"]
        if self.consecutive_failures:
            parts.append(f"failures={self.consecutive_failures}")
        if self.last_error:
            parts.append(f"last_error={self.last_error}")
        return " ".join(parts)

    def _log_throttled(self, level, message: str, min_interval_sec: float = 30.0):
        """Avoid spamming logs by enforcing a minimum interval between similar logs.
        Still logs immediately when connection state changes.
        """
        now = asyncio.get_event_loop().time()
        # Always log when state changes
        state = self.connected
        state_changed = (self._last_state_logged is None) or (self._last_state_logged != state)
        if state_changed or (now - self._last_log_utc) >= min_interval_sec:
            logging.log(level, f"{message} | health: {self.get_health_summary()}")
            self._last_log_utc = now
            self._last_state_logged = state

    def _build_headers(self, endpoint: str) -> dict:
        """Build HMAC headers exactly like VRageAPI for async requests."""
        now = datetime.utcnow()
        nonce = uuid.uuid4().hex + uuid.uuid1().hex
        date = now.strftime("%a, %d %b %Y %H:%M:%S")
        pre_hash_str = f"""{endpoint}\r\n{nonce}\r\n{date}\r\n"""
        hmac_obj = hmac.new(base64.b64decode(self.key), pre_hash_str.encode("utf-8"), hashlib.sha1)
        hmac_encoded = base64.b64encode(hmac_obj.digest()).decode()
        return {
            "Content-Type": "application/json",
            "Date": date,
            "Authorization": f"{nonce}:{hmac_encoded}",
        }

    async def _request_json(self, method: str, endpoint: str):
        """Unified async request helper returning parsed JSON or None."""
        url = f"{self.uri}{endpoint}"
        headers = self._build_headers(endpoint)
        self._log_throttled(logging.INFO, f"[SE-Remote] [REQUEST] {method.upper()} {endpoint}")
        try:
            timeout = aiohttp.ClientTimeout(total=6)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.request(method.upper(), url, headers=headers) as resp:
                    text = await resp.text()
                    if resp.status == 200:
                        logging.debug(f"[SE-Remote] [RESPONSE 200] {text}")
                        try:
                            return await resp.json()
                        except Exception:
                            logging.error(f"[SE-Remote] Failed to parse JSON: {text}")
                            return None
                    else:
                        logging.error(f"[SE-Remote] HTTP {resp.status} | Body: {text}")
                        return None
        except asyncio.TimeoutError:
            logging.error("[SE-Remote] Request timed out")
            return None
        except Exception as e:
            logging.error(f"[SE-Remote] Request failed: {e}", exc_info=True)
            return None

    async def get_json(self, endpoint: str):
        """Public GET JSON helper for future endpoints."""
        return await self._request_json("GET", endpoint)

    async def post_json(self, endpoint: str, payload: dict | None = None):
        """Public POST JSON helper placeholder; switches to request helper when body is needed."""
        # For now, no payload posting is implemented as SE endpoints are mostly GET for status.
        # Extend as needed.
        return await self._request_json("POST", endpoint)

    async def get_status(self):
        """Async, non-blocking status check using aiohttp to avoid blocking the event loop.
        Tries versioned fallback (/v1) if base path fails.
        """
        primary = f"{self.api_endpoint}/server"
        # If api_endpoint already includes "/v1", do single attempt
        if "/v1" in self.api_endpoint:
            return await self._request_json("GET", primary)

        # Try base first, then versioned fallback
        data = await self._request_json("GET", primary)
        if data is not None:
            return data

        fallback_base = f"{self.api_endpoint}/v1"
        fallback = f"{fallback_base}/server"
        logging.info("[SE-Remote] Falling back to versioned endpoint: /v1")
        data = await self._request_json("GET", fallback)
        if data is not None:
            # Persist working endpoint for future calls
            old = self.api_endpoint
            self.api_endpoint = fallback_base
            logging.info(f"[SE-Remote] Using versioned endpoint '{self.api_endpoint}' (was '{old}')")
        return data


