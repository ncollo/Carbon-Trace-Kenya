import { useState, useRef, useEffect, useCallback } from "react";
import { api } from "../api/client";

const WELCOME = {
  role: "model",
  content: "Hello! I'm the **CarbonTrace Kenya AI Assistant**.\n\nI can help you navigate the platform, explain emission metrics, and diagnose errors. What would you like to know?",
};

function formatMsg(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\n/g, "<br/>");
}

function loadSessions() {
  try { return JSON.parse(localStorage.getItem("ct_chats") || "[]"); } catch { return []; }
}
function saveSessions(sessions) {
  try { localStorage.setItem("ct_chats", JSON.stringify(sessions.slice(0, 20))); } catch {}
}

export default function Chatbot() {
  const [open, setOpen]         = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [sessions, setSessions] = useState(loadSessions);
  const [activeId, setActiveId] = useState(null);
  const [messages, setMessages] = useState([WELCOME]);
  const [input, setInput]       = useState("");
  const [thinking, setThinking] = useState(false);
  const bottomRef = useRef();
  const inputRef  = useRef();

  useEffect(() => {
    if (open) {
      bottomRef.current?.scrollIntoView({ behavior: "smooth" });
      inputRef.current?.focus();
    }
  }, [messages, open]);

  const persistSession = useCallback((msgs, id) => {
    const title = msgs.find(m => m.role === "user")?.content?.slice(0, 48) || "New chat";
    const session = { id, title, updatedAt: Date.now(), messages: msgs };
    setSessions(prev => {
      const filtered = prev.filter(s => s.id !== id);
      const updated = [session, ...filtered];
      saveSessions(updated);
      return updated;
    });
  }, []);

  const startNew = () => {
    const id = Date.now().toString();
    setActiveId(id);
    setMessages([WELCOME]);
    setInput("");
    setShowHistory(false);
  };

  const loadSession = (session) => {
    setActiveId(session.id);
    setMessages(session.messages);
    setShowHistory(false);
  };

  const send = async () => {
    const text = input.trim();
    if (!text || thinking) return;
    const id = activeId || Date.now().toString();
    if (!activeId) setActiveId(id);

    const userMsg = { role: "user", content: text };
    const next = [...messages, userMsg];
    setMessages(next);
    setInput("");
    setThinking(true);

    try {
      const history = messages.slice(1).map(m => ({ role: m.role, content: m.content }));
      const { reply } = await api.chat(text, history);
      const final = [...next, { role: "model", content: reply }];
      setMessages(final);
      persistSession(final, id);
    } catch (e) {
      const final = [...next, { role: "model", content: `**Error:** ${e.message}` }];
      setMessages(final);
    } finally {
      setThinking(false);
    }
  };

  return (
    <>
      {/* Toggle button */}
      <button
        onClick={() => setOpen(o => !o)}
        title="CarbonTrace AI Assistant"
        style={{
          position:"fixed", bottom:24, right:24, zIndex:1000,
          width:56, height:56, borderRadius:"50%", border:"none", cursor:"pointer",
          background:"linear-gradient(135deg,#22c55e 0%,#16a34a 100%)",
          boxShadow:"0 4px 24px rgba(34,197,94,0.45)",
          display:"flex", alignItems:"center", justifyContent:"center",
          transition:"transform 0.2s, box-shadow 0.2s",
        }}
        onMouseEnter={e => e.currentTarget.style.transform="scale(1.08)"}
        onMouseLeave={e => e.currentTarget.style.transform="scale(1)"}
      >
        {open
          ? <span style={{ fontSize:22, color:"#030712", fontWeight:700, lineHeight:1 }}>×</span>
          : <svg width="24" height="24" fill="none" viewBox="0 0 24 24">
              <path d="M20 2H4a2 2 0 0 0-2 2v18l4-4h14a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2Z" fill="#030712"/>
            </svg>
        }
      </button>

      {/* Chat panel */}
      {open && (
        <div style={{
          position:"fixed", bottom:92, right:24, zIndex:999,
          width:400, height:560, borderRadius:18,
          background:"var(--surface)", border:"1px solid var(--border-2)",
          boxShadow:"0 12px 48px rgba(0,0,0,0.5)",
          display:"flex", overflow:"hidden",
          fontFamily:"inherit",
        }}>

          {/* History sidebar */}
          {showHistory && (
            <div style={{
              width:160, borderRight:"1px solid var(--border)", flexShrink:0,
              display:"flex", flexDirection:"column", background:"var(--surface-2)",
            }}>
              <div style={{ padding:"12px 12px 8px", borderBottom:"1px solid var(--border)" }}>
                <div style={{ fontSize:11, fontWeight:600, color:"var(--text-mute)", textTransform:"uppercase", letterSpacing:"0.08em" }}>
                  Past chats
                </div>
              </div>
              <div style={{ flex:1, overflowY:"auto", padding:"6px 0" }}>
                {sessions.length === 0 ? (
                  <div style={{ fontSize:11, color:"var(--text-mute)", padding:"12px", textAlign:"center" }}>
                    No history yet
                  </div>
                ) : sessions.map(s => (
                  <button key={s.id} onClick={() => loadSession(s)} style={{
                    width:"100%", textAlign:"left", padding:"8px 12px",
                    background: s.id === activeId ? "var(--inset)" : "transparent",
                    border:"none", cursor:"pointer", borderRadius:0,
                    borderLeft: s.id === activeId ? "2px solid #22c55e" : "2px solid transparent",
                  }}>
                    <div style={{ fontSize:11, color:"var(--text)", fontWeight:500, overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>
                      {s.title}
                    </div>
                    <div style={{ fontSize:10, color:"var(--text-mute)", marginTop:2 }}>
                      {new Date(s.updatedAt).toLocaleDateString()}
                    </div>
                  </button>
                ))}
              </div>
              <div style={{ padding:"8px 10px", borderTop:"1px solid var(--border)" }}>
                <button onClick={startNew} style={{
                  width:"100%", padding:"6px 0", borderRadius:7, border:"1px solid var(--border-2)",
                  background:"transparent", color:"var(--text)", fontSize:11,
                  cursor:"pointer", fontWeight:500,
                }}>
                  + New chat
                </button>
              </div>
            </div>
          )}

          {/* Main chat area */}
          <div style={{ flex:1, display:"flex", flexDirection:"column", minWidth:0 }}>

            {/* Header */}
            <div style={{
              padding:"12px 14px", borderBottom:"1px solid var(--border)",
              background:"var(--surface-2)",
              display:"flex", alignItems:"center", gap:10, flexShrink:0,
            }}>
              <div style={{
                width:36, height:36, borderRadius:10, flexShrink:0,
                background:"linear-gradient(135deg,#22c55e,#16a34a)",
                display:"flex", alignItems:"center", justifyContent:"center",
              }}>
                <svg width="18" height="18" fill="none" viewBox="0 0 24 24">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2Zm-1 14H9V8h2v8Zm4 0h-2V8h2v8Z" fill="#030712"/>
                </svg>
              </div>
              <div style={{ flex:1, minWidth:0 }}>
                <div style={{ fontSize:13, fontWeight:700, color:"var(--text)", letterSpacing:"-0.01em" }}>
                  CarbonTrace Assistant
                </div>
                <div style={{ fontSize:10, color:"#22c55e", marginTop:1 }}>
                  ● Online · Gemini AI · EPRA 2026
                </div>
              </div>
              <div style={{ display:"flex", gap:4 }}>
                <button onClick={() => setShowHistory(h => !h)} title="Chat history" style={{
                  width:30, height:30, borderRadius:7, border:"1px solid var(--border)",
                  background: showHistory ? "var(--inset)" : "transparent",
                  color:"var(--text-mute)", cursor:"pointer", fontSize:14,
                  display:"flex", alignItems:"center", justifyContent:"center",
                }}>☰</button>
                <button onClick={startNew} title="New chat" style={{
                  width:30, height:30, borderRadius:7, border:"1px solid var(--border)",
                  background:"transparent", color:"var(--text-mute)", cursor:"pointer", fontSize:16,
                  display:"flex", alignItems:"center", justifyContent:"center",
                }}>+</button>
              </div>
            </div>

            {/* Messages */}
            <div style={{ flex:1, overflowY:"auto", padding:"14px 14px 8px", display:"flex", flexDirection:"column", gap:12 }}>
              {messages.map((m, i) => (
                <div key={i} style={{ display:"flex", justifyContent: m.role === "user" ? "flex-end" : "flex-start", gap:8 }}>
                  {m.role === "model" && (
                    <div style={{
                      width:26, height:26, borderRadius:8, flexShrink:0, marginTop:2,
                      background:"linear-gradient(135deg,#22c55e,#16a34a)",
                      display:"flex", alignItems:"center", justifyContent:"center",
                      fontSize:10, fontWeight:700, color:"#030712",
                    }}>CT</div>
                  )}
                  <div style={{
                    maxWidth:"78%", padding:"9px 13px", borderRadius:14, fontSize:12.5,
                    lineHeight:1.6,
                    background: m.role === "user"
                      ? "linear-gradient(135deg,#22c55e,#16a34a)"
                      : "var(--surface-3)",
                    color: m.role === "user" ? "#030712" : "var(--text)",
                    border: m.role === "model" ? "1px solid var(--border)" : "none",
                    borderBottomRightRadius: m.role === "user" ? 4 : 14,
                    borderBottomLeftRadius:  m.role === "model" ? 4 : 14,
                  }}
                    dangerouslySetInnerHTML={{ __html: formatMsg(m.content) }}
                  />
                </div>
              ))}
              {thinking && (
                <div style={{ display:"flex", gap:8, alignItems:"center" }}>
                  <div style={{
                    width:26, height:26, borderRadius:8, flexShrink:0,
                    background:"linear-gradient(135deg,#22c55e,#16a34a)",
                    display:"flex", alignItems:"center", justifyContent:"center",
                    fontSize:10, fontWeight:700, color:"#030712",
                  }}>CT</div>
                  <div style={{
                    padding:"10px 16px", borderRadius:14, borderBottomLeftRadius:4,
                    background:"var(--surface-3)", border:"1px solid var(--border)",
                    display:"flex", gap:4, alignItems:"center",
                  }}>
                    {[0,1,2].map(n => (
                      <div key={n} style={{
                        width:6, height:6, borderRadius:"50%", background:"var(--text-mute)",
                        animation:"pulse 1.2s ease-in-out infinite",
                        animationDelay:`${n * 0.2}s`,
                      }}/>
                    ))}
                  </div>
                </div>
              )}
              <div ref={bottomRef} />
            </div>

            {/* Input */}
            <div style={{
              padding:"10px 12px 12px", borderTop:"1px solid var(--border)",
              background:"var(--surface-2)", flexShrink:0,
            }}>
              <div style={{
                display:"flex", gap:8, alignItems:"flex-end",
                background:"var(--inset)", borderRadius:12, padding:"8px 8px 8px 14px",
                border:"1px solid var(--border-2)",
              }}>
                <textarea
                  ref={inputRef}
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } }}
                  placeholder="Ask anything or paste an error…"
                  rows={1}
                  style={{
                    flex:1, background:"transparent", border:"none", outline:"none",
                    fontSize:12.5, color:"var(--text)", resize:"none", lineHeight:1.5,
                    fontFamily:"inherit", maxHeight:80, overflowY:"auto",
                  }}
                />
                <button
                  onClick={send}
                  disabled={!input.trim() || thinking}
                  style={{
                    width:32, height:32, borderRadius:8, border:"none", flexShrink:0,
                    background: input.trim() && !thinking
                      ? "linear-gradient(135deg,#22c55e,#16a34a)"
                      : "var(--surface-3)",
                    color: input.trim() && !thinking ? "#030712" : "var(--text-mute)",
                    cursor: input.trim() && !thinking ? "pointer" : "default",
                    display:"flex", alignItems:"center", justifyContent:"center",
                    transition:"background 0.15s",
                  }}
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M2.01 21 23 12 2.01 3 2 10l15 2-15 2z"/>
                  </svg>
                </button>
              </div>
              <div style={{ fontSize:10, color:"var(--text-mute)", textAlign:"center", marginTop:6 }}>
                Enter to send · Shift+Enter for new line
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
