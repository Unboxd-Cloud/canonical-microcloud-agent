"use client";

import { FormEvent, useState } from "react";

type Message = { role: "user" | "assistant"; text: string };

const defaultApiBase = process.env.NEXT_PUBLIC_AGENT_API_BASE ?? "http://127.0.0.1:8765";

export default function Page() {
  const [apiBase, setApiBase] = useState(defaultApiBase);
  const [input, setInput] = useState("Give me health status");
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", text: "Streaming chat is ready. Point this UI at the local agent API and start talking." }
  ]);
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    const question = input.trim();
    if (!question || loading) return;

    setLoading(true);
    setMessages((current) => [...current, { role: "user", text: question }, { role: "assistant", text: "" }]);
    setInput("");

    try {
      const response = await fetch(`${apiBase}/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: question })
      });

      if (!response.body) throw new Error("Streaming response body is not available.");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const events = buffer.split("\n\n");
        buffer = events.pop() ?? "";

        for (const eventChunk of events) {
          const line = eventChunk.split("\n").find((entry) => entry.startsWith("data: "));
          if (!line) continue;
          const payload = JSON.parse(line.slice(6)) as { delta?: string; done?: boolean };
          if (payload.delta) {
            setMessages((current) => {
              const next = [...current];
              const last = next[next.length - 1];
              next[next.length - 1] = { ...last, text: last.text + payload.delta };
              return next;
            });
          }
        }
      }
    } catch (error) {
      setMessages((current) => {
        const next = [...current];
        next[next.length - 1] = {
          role: "assistant",
          text: error instanceof Error ? error.message : "Streaming request failed."
        };
        return next;
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="shell">
      <section className="hero">
        <p className="hint">Next.js chat template</p>
        <h1 className="title">Canonical MicroCloud Agent UI</h1>
        <p className="subtitle">
          Stream chat responses from the local agent API, inspect workflow output, and use the same backend for
          operations, OIDC, OpenAPI, and Mattermost-aware automation.
        </p>
      </section>

      <section className="grid">
        <aside className="panel stack">
          <div className="stack">
            <label htmlFor="apiBase">Agent API base URL</label>
            <input id="apiBase" value={apiBase} onChange={(e) => setApiBase(e.target.value)} />
          </div>
          <div className="stack">
            <div className="hint">Useful endpoints</div>
            <div className="msg assistant">GET /health{"\n"}GET /openapi.json{"\n"}POST /chat{"\n"}POST /chat/stream</div>
          </div>
        </aside>

        <section className="panel stack">
          <div className="messages stack">
            {messages.map((message, index) => (
              <div key={index} className={`msg ${message.role}`}>
                {message.text || (loading && index === messages.length - 1 ? "..." : "")}
              </div>
            ))}
          </div>
          <form className="stack" onSubmit={onSubmit}>
            <textarea value={input} onChange={(e) => setInput(e.target.value)} />
            <div className="row">
              <button type="submit">{loading ? "Streaming..." : "Send"}</button>
            </div>
          </form>
        </section>
      </section>
    </main>
  );
}
