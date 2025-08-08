

import logging
from vrage_api import VRageRemoteClient



# Wrapper für vrage-api, um die alte Schnittstelle beizubehalten
class SpaceEngineersRemoteClient:
    def __init__(self, uri, key=None):
        self.uri = uri.rstrip('/')
        self.key = key
        self.client = VRageRemoteClient(self.uri, self.key)
        self.connected = False

    async def connect(self):
        try:
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
        # vrage-api verwaltet Sessions selbst, kein explizites Close nötig
        self.connected = False

    async def get_status(self):
        try:
            logging.info(f"[SE-Remote] [REQUEST] GET /vrageremote/status")
            resp = await self.client.status()
            logging.info(f"[SE-Remote] [RESPONSE] {resp}")
            return resp
        except Exception as e:
            logging.error(f"[SE-Remote] Status request failed: {e}")
            return None


