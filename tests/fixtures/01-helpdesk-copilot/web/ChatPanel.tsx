import { useState } from "react";

export function ChatPanel({ debug = false }) {
  const [msgs, setMsgs] = useState<any[]>([]);
  async function send(q: string) {
    const r = await fetch("/chat", { method: "POST", body: JSON.stringify({ tenant_id: window.TENANT, question: q }) });
    const data = await r.json();
    setMsgs([...msgs, { q, a: data.answer, sources: data.sources }]);
  }
  return (
    <div className="chat">
      <div className="chat-header">Ask Lumi ✨</div>
      {msgs.map((m, i) => (
        <div key={i}>
          <p className="q">{m.q}</p>
          <p className="a">{m.a}</p>
          {debug && <ul>{m.sources.map((s: any) => <li key={s.id}>{s.title}</li>)}</ul>}
        </div>
      ))}
    </div>
  );
}
