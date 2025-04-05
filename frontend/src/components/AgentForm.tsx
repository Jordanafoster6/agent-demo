import { v4 as uuidv4 } from 'uuid';
import { askAgent } from '../api/agent';
import React, { useState, useEffect } from 'react';
import { TextField, Button, CircularProgress } from '@mui/material';
import { ChatWindow } from './ChatWindow';
import { ChatContext, AgentMessage } from '@shared/types';

export default function AgentForm() {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState('');
  const [messages, setMessages] = useState<AgentMessage[]>([]);
  const [context, setContext] = useState<ChatContext>({});

  useEffect(() => {
    setSessionId(uuidv4()); // create unique session per mount
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    const res = await askAgent(input, sessionId, context);
    console.log(res);
    setMessages((prev) => [...prev, ...res.messages]);
    setContext(res.context ?? {});
    setLoading(false);
  };

  return (
    <div>
      <TextField
        fullWidth
        label="Describe the product..."
        value={input}
        onChange={(e) => setInput(e.target.value)}
        margin="normal"
      />
      <div style={{ display: 'flex', gap: '10px' }}>
        <Button onClick={handleSubmit} variant="contained" disabled={loading}>
          {loading ? <CircularProgress size={24} /> : 'Send'}
        </Button>
        <Button onClick={() => setInput('i want a shirt with a smiling robot on it')} variant="contained">
          Add Product
        </Button>
        <Button onClick={() => setInput('741')} variant="contained">
          Choose Product
        </Button>
      </div>
      {messages && <ChatWindow messages={messages} />}
    </div>
  );
}
