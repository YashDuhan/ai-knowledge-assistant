'use client';

import { useState, useRef, useEffect } from 'react';
import type { ChangeEvent } from 'react';

type Message = { role: 'user' | 'assistant'; content: string; sources?: string[] };

/** Split text into segments and insert citation chips between sentences. */
function segmentsWithChips(text: string, sourceCount: number): Array<{ type: 'text'; value: string } | { type: 'chip'; idx: number }> {
  const result: Array<{ type: 'text'; value: string } | { type: 'chip'; idx: number }> = [];
  if (!text.trim()) return result;
  if (sourceCount === 0) return [{ type: 'text', value: text }];

  const sentences = text.split(/(?<=[.!?])\s+/).filter(Boolean);
  let chipIdx = 0;

  sentences.forEach((sent, i) => {
    result.push({ type: 'text', value: sent + (i < sentences.length - 1 ? ' ' : '') });
    if (i < sentences.length - 1) {
      result.push({ type: 'chip', idx: (chipIdx % sourceCount) + 1 });
      chipIdx++;
    }
  });
  return result;
}

function CitationChip({ idx, sources }: { idx: number; sources: string[] }) {
  const [show, setShow] = useState(false);

  const source = sources[idx - 1] || 'Unknown source';

  const toggle = () => setShow((s) => !s);
  const handleMouseEnter = () => setShow(true);
  const handleMouseLeave = () => setShow(false);

  return (
    <span className="citation-chip-wrapper">
      <span
        className="citation-chip"
        onClick={toggle}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && toggle()}
        aria-label={`Citation ${idx}`}
      >
        [{idx}]
      </span>
      {(show || false) && (
        <div
          className="citation-popover"
          onMouseEnter={handleMouseEnter}
          onMouseLeave={handleMouseLeave}
        >
          {source}
        </div>
      )}
    </span>
  );
}

function AnswerWithChips({ text, sources }: { text: string; sources: string[] }) {
  const segs = segmentsWithChips(text, sources.length);
  return (
    <span className="answer-text">
      {segs.map((s, i) =>
        s.type === 'text' ? (
          <span key={i}>{s.value}</span>
        ) : (
          <CitationChip key={`chip-${i}`} idx={s.idx} sources={sources} />
        )
      )}
    </span>
  );
}

type WaitingStatus = 'searching' | 'generating' | null;

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [waitingStatus, setWaitingStatus] = useState<WaitingStatus>(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages, loading]);

  async function handleSend() {
    if (!input.trim() || loading) return;
    const question = input.trim();
    setInput('');
    setMessages((m) => [...m, { role: 'user', content: question }]);
    setLoading(true);
    setWaitingStatus('searching');

    try {
      const res = await fetch(`/api/ask/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
        cache: 'no-store',
      });
      if (!res.ok) throw new Error(res.statusText);
      const reader = res.body?.getReader();
      const decoder = new TextDecoder();
      let text = '';
      let srcs: string[] = [];
      let lastEvent = '';
      let buffer = '';

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() ?? '';
          for (const line of lines) {
            if (line.startsWith('event: ')) {
              lastEvent = line.slice(7).trim();
            } else if (line.startsWith('data: ')) {
              const raw = line.slice(6).trim();
              if (!raw || raw === '[DONE]') continue;
              try {
                const parsed = JSON.parse(raw);
                if (parsed.status) {
                  setWaitingStatus(parsed.status === 'searching' ? 'searching' : 'generating');
                } else if (parsed.t !== undefined) {
                  setWaitingStatus(null);
                  text += parsed.t;
                } else if (Array.isArray(parsed)) {
                  srcs = parsed;
                }
              } catch {
                if (lastEvent === 'token') text += raw;
              }
            }
          }
          setMessages((m) => {
            const next = [...m];
            const last = next[next.length - 1];
            if (last?.role === 'assistant') {
              next[next.length - 1] = { ...last, content: text, sources: srcs.length ? srcs : last.sources };
            } else {
              next.push({ role: 'assistant', content: text, sources: srcs });
            }
            return next;
          });
        }
      }
    } catch (e) {
      setMessages((m) => [
        ...m,
        { role: 'assistant', content: `Error: ${e instanceof Error ? e.message : 'Unknown error'}`, sources: [] },
      ]);
    } finally {
      setLoading(false);
      setWaitingStatus(null);
    }
  }

  async function handleUpload(e: ChangeEvent<HTMLInputElement>) {
    const files = e.target.files;
    if (!files?.length) return;
    setUploadStatus('Uploading...');
    try {
      const formData = new FormData();
      for (let i = 0; i < files.length; i++) formData.append('files', files[i]);
      const res = await fetch(`/api/upload`, { method: 'POST', body: formData });
      if (!res.ok) throw new Error('Upload failed');
      const data = await res.json();
      setUploadStatus(`Uploaded: ${(data.uploaded || []).join(', ')}`);
    } catch {
      setUploadStatus('Upload failed');
    }
    e.target.value = '';
  }

  return (
    <div className="chat-layout">
      <header className="chat-header">
        <div className="header-left">
          <div className="brand-mark" aria-hidden="true" />
          <div className="brand-text">
            <h1>AI Knowledge Assistant</h1>
            <div className="subtitle">Streaming answers over your docs</div>
          </div>
        </div>
        <div className="header-actions">
          <span className="pill" title="Server-Sent Events">
            SSE streaming
          </span>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleUpload}
            multiple
            accept=".pdf,.txt"
            style={{ display: 'none' }}
          />
          <button type="button" onClick={() => fileInputRef.current?.click()} className="btn-upload">
            Upload PDF/TXT
          </button>
          {uploadStatus && <span className="upload-status">{uploadStatus}</span>}
        </div>
      </header>

      <main className="chat-main">
        <div className="chat-messages">
          {messages.length === 0 && !loading && (
            <div className="chat-empty">
              <div className="empty-card">
                <div className="empty-title">Drop in context, then ask away</div>
                <div className="empty-subtitle">
                  Upload PDFs/TXTs and ask questions. You’ll see tokens stream in as the answer is generated.
                </div>
                <div className="empty-actions">
                  <button type="button" onClick={() => fileInputRef.current?.click()} className="btn-upload btn-upload-ghost">
                    Upload documents
                  </button>
                </div>
              </div>
            </div>
          )}
          {messages.map((msg, i) => (
            <div key={i} className={`chat-row ${msg.role}`}>
              <div className="avatar" aria-hidden="true" />
              <div className={`chat-bubble ${msg.role}`}>
                <div className="bubble-content">
                  {msg.role === 'user' ? msg.content : <AnswerWithChips text={msg.content} sources={msg.sources || []} />}
                </div>
              </div>
            </div>
          ))}
          {loading && (
            <div className="chat-row assistant">
              <div className="avatar" aria-hidden="true" />
              <div className="chat-bubble assistant">
                <div className="bubble-content typing">
                  <span className="typing-indicator" />
                  {waitingStatus === 'searching' && 'Searching documents…'}
                  {waitingStatus === 'generating' && 'Generating answer…'}
                  {!waitingStatus && 'Working…'}
                </div>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        <div className="chat-input-row">
          <input
            type="text"
            placeholder="Ask a question about your uploaded docs…"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
            disabled={loading}
            className="chat-input"
          />
          <button type="button" onClick={handleSend} disabled={loading || !input.trim()} className="btn-send">
            Send
          </button>
        </div>
      </main>
    </div>
  );
}
