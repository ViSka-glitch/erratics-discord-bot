import asyncio
import json
import websockets
import logging

class SpaceEngineersRemoteClient:
    def __init__(self, uri, key=None):
        self.uri = uri
        self.key = key
        self.ws = None
        self.connected = False
        self._listener_task = None
        self._message_queue = asyncio.Queue()

    async def connect(self):
        try:
            self.ws = await websockets.connect(self.uri)
            self.connected = True
            logging.info(f"[SE-Remote] Connected to {self.uri}")
            if self.key:
                await self.send_command({"Type": "Auth", "Password": self.key})
            self._listener_task = asyncio.create_task(self._listener())
        except Exception as e:
            logging.error(f"[SE-Remote] Connection failed: {e}")
            self.connected = False

    async def disconnect(self):
        if self.ws:
            await self.ws.close()
        self.connected = False
        if self._listener_task:
            self._listener_task.cancel()

    async def send_command(self, data):
        if self.ws and self.connected:
            await self.ws.send(json.dumps(data))

    async def _listener(self):
        try:
            async for message in self.ws:
                await self._message_queue.put(message)
        except Exception as e:
            logging.error(f"[SE-Remote] Listener error: {e}")
            self.connected = False

    async def get_message(self, timeout=5):
        try:
            return await asyncio.wait_for(self._message_queue.get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None
