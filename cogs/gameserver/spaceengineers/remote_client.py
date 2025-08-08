
import aiohttp
import asyncio
import logging


class SpaceEngineersRemoteClient:
    def __init__(self, uri, key=None):
        self.uri = uri.rstrip('/')
        self.key = key
        self.session = None
        self.connected = False

    async def connect(self):
        try:
            self.session = aiohttp.ClientSession()
            # Testverbindung: Status-Endpunkt aufrufen
            resp = await self.get_status()
            if resp is not None:
                self.connected = True
                logging.info(f"[SE-Remote] Connected to {self.uri}")
            else:
                self.connected = False
        except Exception as e:
            logging.error(f"[SE-Remote] Connection failed: {e}")
            self.connected = False

    async def disconnect(self):
        if self.session:
            await self.session.close()
        self.connected = False


    async def get_status(self):
        if not self.session:
            return None
        url = f"{self.uri}/status"
        headers = {"Authorization": self.key} if self.key else {}
        try:
            logging.info(f"[SE-Remote] GET {url} headers={headers}")
            async with self.session.get(url, headers=headers, timeout=5) as resp:
                text = await resp.text()
                if resp.status == 200:
                    logging.info(f"[SE-Remote] Status response: {text}")
                    return await resp.json()
                else:
                    logging.error(f"[SE-Remote] Status HTTP {resp.status} | Response: {text}")
                    return None
        except Exception as e:
            logging.error(f"[SE-Remote] Status request failed: {e} | URL: {url} | headers: {headers}")
            return None


