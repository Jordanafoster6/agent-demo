// Simple in-memory store (swap for Redis or DB later)
// This stores session-specific context objects to simulate persistent memory.
type AgentContext = Record<string, any>;

const contextStore: Map<string, AgentContext> = new Map();

export function getContext(sessionId: string): AgentContext {
  return contextStore.get(sessionId) ?? {};
}

export function setContext(sessionId: string, context: AgentContext) {
  contextStore.set(sessionId, context);
}
