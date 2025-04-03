import express from 'express';
import cors from 'cors';
import agentRouter from './routes/agent';


const app = express();
app.use(cors());
app.use(express.json());
app.use('/api/agent', agentRouter);

const PORT = 3001;

app.get('/', (_, res) => {
  res.send('Backend is running ✅');
});
app.listen(PORT, () => {
  console.log(`Backend running on http://localhost:${PORT}`);
});
