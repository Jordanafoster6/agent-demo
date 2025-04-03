import { Router } from 'express';
import axios from 'axios';
import { getContext, setContext } from '../contextStore';
import { AgentRequestSchema, AgentResponseSchema } from '@shared/types';

const router = Router();

router.post('/', async (req, res) => {
  const parsed = AgentRequestSchema.safeParse(req.body);
  if (!parsed.success) return res.status(400).json(parsed.error);

  const { input, sessionId } = parsed.data;
  const context = getContext(sessionId);

  try {
    const response = await axios.post('http://localhost:5100/agent', {
      input,
      sessionId,
      context,
    });

    const { messages, context: updatedContext } = response.data;
    setContext(sessionId, updatedContext);

    const result = AgentResponseSchema.parse({ messages, sessionId, context: updatedContext });
    res.json(result);
  } catch (err) {
    console.error('🔥 Agent error:', err);
    res.status(500).send('Agent error');
  }
});

export default router;
