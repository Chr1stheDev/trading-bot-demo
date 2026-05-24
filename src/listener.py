"""
listener.py
-----------
Async messaging interface listener.
Receives plain-text commands and passes them to the orchestrator.
"""

import asyncio
import os
from telethon import TelegramClient, events
from src.orchestrator import Orchestrator


class Listener:

    def __init__(self, orchestrator: Orchestrator):
        self.orchestrator = orchestrator
        self._client = TelegramClient(
            session="bot_session",
            api_id=int(os.environ["API_ID"]),
            api_hash=os.environ["API_HASH"],
        )
        self._authorized_user = int(os.environ["AUTHORIZED_USER_ID"])

    async def start(self):
        await self._client.start()
        print("[Listener] Started — waiting for commands...")

        @self._client.on(events.NewMessage(from_users=self._authorized_user))
        async def handler(event):
            text = event.message.text.strip()
            if not text:
                return

            print(f"[Listener] Received: {text}")
            response = await self.orchestrator.handle(text)
            await event.reply(response)

        await self._client.run_until_disconnected()

    async def stop(self):
        await self._client.disconnect()
        print("[Listener] Stopped")
