"use client";
import { useState, useRef } from "react";
import ReactMarkdown from 'react-markdown'
const API = "http://localhost:8000/api/v1";

type Message = {
  role: "user" | "assistant";
  content: string;
  needs_approval?: boolean;
  compliance?: string;
  status?: string;
};

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);

  async function sendQuestion() {
    if (!question.trim() || loading) return;
    const userMsg: Message = { role: "user", content: question };
    setMessages(prev => [...prev, userMsg]);
    const currentQuestion = question;
    setQuestion("");
    setLoading(true);

    const assistantMsg: Message = {
      role: "assistant",
      content: "",
      status: "Searching documents..."
    };
    setMessages(prev => [...prev, assistantMsg]);

    try {
      const response = await fetch(`${API}/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: currentQuestion })
      });

      const reader = response.body!.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const text = decoder.decode(value);
        const lines = text.split("\n").filter(l => l.startsWith("data: "));

        for (const line of lines) {
          try {
            const data = JSON.parse(line.replace("data: ", ""));

            if (data.type === "status") {
              setMessages(prev => {
                const updated = [...prev];
                updated[updated.length - 1] = {
                  ...updated[updated.length - 1],
                  status: data.content
                };
                return updated;
              });
            }

            if (data.type === "token") {
              setMessages(prev => {
                const updated = [...prev];
                updated[updated.length - 1] = {
                  ...updated[updated.length - 1],
                  content: updated[updated.length - 1].content + data.content,
                  status: ""
                };
                return updated;
              });
            }

            if (data.type === "compliance") {
              setMessages(prev => {
                const updated = [...prev];
                updated[updated.length - 1] = {
                  ...updated[updated.length - 1],
                  needs_approval: data.needs_approval,
                  compliance: data.content
                };
                return updated;
              });
            }
          } catch (e) {
            // skip malformed chunks
          }
        }
      }
    } catch (e) {
      setMessages(prev => {
        const updated = [...prev];
        updated[updated.length - 1] = {
          ...updated[updated.length - 1],
          content: "Error connecting to Enclave backend.",
          status: ""
        };
        return updated;
      });
    }
    setLoading(false);
  }

  async function uploadFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setUploadStatus("Uploading...");
    const form = new FormData();
    form.append("file", file);
    try {
      const res = await fetch(`${API}/upload`, { method: "POST", body: form });
      const data = await res.json();
      setUploadStatus(`✓ ${data.filename} — ${data.chunks_ingested} chunks ingested`);
    } catch (e) {
      setUploadStatus("✗ Upload failed");
    }
    setUploading(false);
  }

  return (
    <div style={{ display: "flex", height: "100vh", background: "#f8f8f6" }}>
      {/* Sidebar */}
      <div style={{
        width: 260, background: "#fff", borderRight: "1px solid #e8e8e4",
        display: "flex", flexDirection: "column", padding: "24px 16px"
      }}>
        <div style={{ marginBottom: 32 }}>
          <h1 style={{ fontSize: 20, fontWeight: 600, letterSpacing: "-0.5px" }}>Enclave.AI</h1>
          <p style={{ fontSize: 12, color: "#888", marginTop: 4 }}>Privacy-first enterprise AI</p>
        </div>

        <div style={{ marginBottom: 24 }}>
          <p style={{ fontSize: 11, fontWeight: 500, color: "#888", marginBottom: 8, textTransform: "uppercase", letterSpacing: "0.5px" }}>Documents</p>
          <button
            onClick={() => fileRef.current?.click()}
            disabled={uploading}
            style={{
              width: "100%", padding: "10px 12px", background: "#1a1a1a",
              color: "#fff", border: "none", borderRadius: 8, fontSize: 13,
              cursor: uploading ? "not-allowed" : "pointer", fontWeight: 500
            }}
          >
            {uploading ? "Uploading..." : "+ Upload PDF"}
          </button>
          <input ref={fileRef} type="file" accept=".pdf" onChange={uploadFile} style={{ display: "none" }} />
          {uploadStatus && (
            <p style={{ fontSize: 11, color: uploadStatus.startsWith("✓") ? "#2d7a4f" : "#c0392b", marginTop: 8, lineHeight: 1.4 }}>
              {uploadStatus}
            </p>
          )}
        </div>

        <div style={{ marginTop: "auto" }}>
          <p style={{ fontSize: 11, fontWeight: 500, color: "#888", marginBottom: 8, textTransform: "uppercase", letterSpacing: "0.5px" }}>Services</p>
          {["Llama 3.1 8B", "Qdrant", "BGE Embeddings"].map(s => (
            <div key={s} style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 6 }}>
              <div style={{ width: 6, height: 6, borderRadius: "50%", background: "#2d7a4f" }} />
              <span style={{ fontSize: 12, color: "#555" }}>{s}</span>
            </div>
          ))}
          <div style={{ marginTop: 12, padding: "8px 10px", background: "#f0faf4", borderRadius: 6, border: "1px solid #c8e6d4" }}>
            <p style={{ fontSize: 11, color: "#2d7a4f", fontWeight: 500 }}>100% On-Premise</p>
            <p style={{ fontSize: 10, color: "#5a9a72", marginTop: 2 }}>No data leaves your server</p>
          </div>
        </div>
      </div>

      {/* Main */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
        <div style={{ padding: "20px 32px", borderBottom: "1px solid #e8e8e4", background: "#fff" }}>
          <h2 style={{ fontSize: 15, fontWeight: 500 }}>Document Intelligence</h2>
          <p style={{ fontSize: 12, color: "#888", marginTop: 2 }}>Upload documents and ask questions — answers stay within your infrastructure</p>
        </div>

        <div style={{ flex: 1, overflowY: "auto", padding: "24px 32px" }}>
          {messages.length === 0 && (
            <div style={{ textAlign: "center", marginTop: 80, color: "#aaa" }}>
              <p style={{ fontSize: 32, marginBottom: 12 }}>🔒</p>
              <p style={{ fontSize: 15, fontWeight: 500, color: "#555" }}>Upload a PDF and start asking questions</p>
              <p style={{ fontSize: 13, marginTop: 6 }}>All processing happens locally — nothing sent to the cloud</p>
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i} style={{ marginBottom: 20, display: "flex", justifyContent: msg.role === "user" ? "flex-end" : "flex-start" }}>
              <div style={{
                maxWidth: "70%", padding: "12px 16px",
                background: msg.role === "user" ? "#1a1a1a" : "#fff",
                color: msg.role === "user" ? "#fff" : "#1a1a1a",
                borderRadius: msg.role === "user" ? "16px 16px 4px 16px" : "16px 16px 16px 4px",
                border: msg.role === "assistant" ? "1px solid #e8e8e4" : "none",
                fontSize: 14, lineHeight: 1.6
              }}>
                {msg.status && (
                  <p style={{ fontSize: 12, color: "#999", fontStyle: "italic", marginBottom: msg.content ? 8 : 0 }}>
                    {msg.status}
                  </p>
                )}
                {msg.content && (
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                )}
                {msg.compliance && (
                  <div style={{ marginTop: 10, padding: "8px 10px", background: msg.needs_approval ? "#fff8e6" : "#f0faf4", borderRadius: 6, border: `1px solid ${msg.needs_approval ? "#f0d080" : "#c8e6d4"}` }}>
                    <p style={{ fontSize: 11, color: msg.needs_approval ? "#b8860b" : "#2d7a4f", fontWeight: 500 }}>
                      {msg.needs_approval ? "⚠ Requires human approval" : "✓ Compliance passed"}
                    </p>
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && messages[messages.length - 1]?.role === "user" && (
            <div style={{ display: "flex", gap: 6, padding: "12px 16px", background: "#fff", border: "1px solid #e8e8e4", borderRadius: 16, width: "fit-content" }}>
              {[0, 1, 2].map(i => (
                <div key={i} style={{
                  width: 8, height: 8, borderRadius: "50%", background: "#aaa",
                }} />
              ))}
            </div>
          )}
        </div>

        <div style={{ padding: "16px 32px", borderTop: "1px solid #e8e8e4", background: "#fff" }}>
          <div style={{ display: "flex", gap: 12 }}>
            <input
              value={question}
              onChange={e => setQuestion(e.target.value)}
              onKeyDown={e => e.key === "Enter" && sendQuestion()}
              placeholder="Ask a question about your documents..."
              style={{
                flex: 1, padding: "12px 16px", border: "1px solid #e8e8e4",
                borderRadius: 10, fontSize: 14, outline: "none",
                background: "#f8f8f6"
              }}
            />
            <button
              onClick={sendQuestion}
              disabled={loading || !question.trim()}
              style={{
                padding: "12px 24px", background: loading ? "#ccc" : "#1a1a1a",
                color: "#fff", border: "none", borderRadius: 10,
                fontSize: 14, fontWeight: 500,
                cursor: loading ? "not-allowed" : "pointer"
              }}
            >
              {loading ? "..." : "Ask"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}