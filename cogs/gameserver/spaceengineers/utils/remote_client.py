

import logging
from vrage_api.vrage_api import VRageAPI



# Wrapper für vrage-api, um die alte Schnittstelle beizubehalten
class SpaceEngineersRemoteClient:
    def __init__(self, uri, key=None):
        self.uri = uri.rstrip('/')
        self.key = key
        self.client = VRageAPI(self.uri, self.key)
        self.connected = False

    async def connect(self):
        logging.info(f"[SE-Remote] Attempting to connect to {self.uri}")
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
        logging.info(f"[SE-Remote] Disconnect called for {self.uri}")
        # vrage-api verwaltet Sessions selbst, kein explizites Close nötig
        self.connected = False

    async def get_status(self):
        logging.info(f"[SE-Remote] [REQUEST] GET /vrageremote/v1/server (client={self.client})")
        try:
            # get_server_info entspricht dem Status-Endpunkt
            resp = self.client.get_server_info()
            logging.info(f"[SE-Remote] [RESPONSE] {type(resp)}: {resp}")
            return resp
        except Exception as e:
            logging.error(f"[SE-Remote] Status request failed: {e}", exc_info=True)
            return None


