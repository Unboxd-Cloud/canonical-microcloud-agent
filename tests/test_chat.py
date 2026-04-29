from __future__ import annotations

import unittest

from microcloud_agent.service import AgentService


class ChatTests(unittest.TestCase):
    def test_chat_returns_response(self) -> None:
        service = AgentService()
        payload = service.chat("what workflows do you have?")
        self.assertIn("Available workflows", payload["response"])

    def test_stream_chat_returns_chunks(self) -> None:
        service = AgentService()
        chunks = service.stream_chat("health")
        self.assertTrue(chunks)
        self.assertTrue(any(chunk.strip() for chunk in chunks))
