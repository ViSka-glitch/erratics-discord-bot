
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
        try:
            headers = {"Authorization": self.key} if self.key else {}
            async with self.session.get(f"{self.uri}/status", headers=headers, timeout=5) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    logging.error(f"[SE-Remote] Status HTTP {resp.status}")
                    return None
        except Exception as e:
            logging.error(f"[SE-Remote] Status request failed: {e}")
            return None


