## Agent-demo startup
- Agent-service:    `uvicorn main:app --port 5100 --reload`
- Backend:    `npx ts-node-dev --respawn --require tsconfig-paths/register src/index.ts`
- Frontend:    `npm run dev`
