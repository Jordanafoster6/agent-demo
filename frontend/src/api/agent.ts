import { AgentRequest, AgentResponse, ChatContext } from "@shared/types";

export async function askAgent(input: string, sessionId: string, context: ChatContext = {}): Promise<AgentResponse> {
  const res = await fetch('http://localhost:3001/api/agent', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ input, sessionId, context } satisfies AgentRequest),
  });
  return await res.json();
}
