
import aiohttp
import asyncio
import logging

import hmac
import hashlib
import base64
import random
import string
from datetime import datetime, timezone


class SpaceEngineersRemoteClient:
    def __init__(self, uri, key=None):
        self.uri = uri.rstrip('/')
        self.key = key
        self.session = None
        self.connected = False

    async def connect(self):
        logging.info(f"[SE-Remote] Attempting to connect to {self.uri} (session open: {self.session is not None})")
        try:
            if self.session:
                await self.disconnect()
            self.session = aiohttp.ClientSession()
            logging.info(f"[SE-Remote] ClientSession created: {self.session}")
            # Testverbindung: Status-Endpunkt aufrufen
            resp = await self.get_status()
            if resp is not None:
                self.connected = True
                logging.info(f"[SE-Remote] Connected to {self.uri}")
            else:
                self.connected = False
                logging.warning(f"[SE-Remote] Could not connect to {self.uri} (no status response)")
        except Exception as e:
            logging.error(f"[SE-Remote] Connection failed: {e}")
            self.connected = False

    async def disconnect(self):
        if self.session:
            logging.info(f"[SE-Remote] Closing ClientSession: {self.session}")
            await self.session.close()
            logging.info(f"[SE-Remote] ClientSession closed.")
        else:
            logging.info(f"[SE-Remote] No ClientSession to close.")
        self.connected = False


    def _generate_auth_headers(self, method_url: str, query_params: dict = None):
        # method_url: z.B. /vrageremote/status
        # query_params: dict of query params (optional)
        nonce = str(random.randint(0, 2**31-1))
        date = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        message = method_url
        if query_params:
            items = sorted(query_params.items())
            message += '?' + '&'.join(f"{k}={v}" for k, v in items)
        message += '\n' + nonce + '\n' + date
        message_bytes = message.encode('utf-8')
        key_bytes = self.key.encode('utf-8') if self.key else b''
        digest = hmac.new(key_bytes, message_bytes, hashlib.sha1).digest()
        hash_b64 = base64.b64encode(digest).decode('utf-8')
        auth_header = f"{nonce}:{hash_b64}"
        return {
            "Authorization": auth_header,
            "Date": date,
            "nonce": nonce
        }

    async def get_status(self):
        if not self.session:
            logging.warning(f"[SE-Remote] get_status called but session is None!")
            return None
        # Die API erwartet den Pfad ab /vrageremote
        method_url = "/vrageremote/status"
        url = f"{self.uri}/vrageremote/status" if not self.uri.endswith("/vrageremote") else f"{self.uri}/status"
        headers = self._generate_auth_headers(method_url)
        try:
            logging.info(f"[SE-Remote] [REQUEST] GET {url} headers={headers}")
            import time
            start = time.perf_counter()
            async with self.session.get(url, headers=headers, timeout=5) as resp:
                elapsed = time.perf_counter() - start
                text = await resp.text()
                logging.info(f"[SE-Remote] [RESPONSE] HTTP {resp.status} in {elapsed:.3f}s | Response: {text}")
                if resp.status == 200:
                    return await resp.json()
                else:
                    logging.error(f"[SE-Remote] Status HTTP {resp.status} | Response: {text}")
                    return None
        except Exception as e:
            logging.error(f"[SE-Remote] Status request failed: {e} | URL: {url} | headers: {headers}")
            return None


