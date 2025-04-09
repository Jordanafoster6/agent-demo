## AI Product Builder Setup
An AI-driven application powered by OpenAI (GPT-4o, DALL-E 3) and Printify APIs creates customized products from natural language input. Featuring a multi-agent architecture with an orchestrator and specialized agents for UI, product research, design, and configuration, it uses React with TypeScript, and Material UI for the frontend, and Express.js with TypeScript for the backend. `Zod` is also used for shared typing between the frontend and backend. Users interact via a chat interface to design and configure products, with the system handling image generation, product selection, and Printify integration.

The agent microservice is a FastAPI-based application designed to handle user interactions with Printify’s product catalog via an AI-driven conversational agent. It uses a modular architecture with a central orchestrator agent (`orchestrator_agent.py`) along with a design agent (`design_agent.py`) using DALL-E to generate artwork from user descriptions for a product, and a specialized Printify agent (`printify_agent.py`) to manage product-related tasks. The system integrates with the OpenAI API using DALL-E to generate artwork from user descriptions later used for product creation in Printify, and the Printify API to fetch blueprints, print providers, and variants, and finally product creation leveraging tools and context management to maintain state across requests. The microservice processes user inputs through a single /agent endpoint, orchestrates tool calls, and returns structured responses to a frontend client.

### Backend Setup
- Install Deps: `npm i`
- Startup Backend: `npx ts-node-dev --respawn --require tsconfig-paths/register src/index.ts`

## Frontend Setup
- Install deps: `npm i`
- Startup frontend: `npm start`

### Agent Service Setup
You'll need to set up a Python virtual environment (venv) with the required dependencies:

1. Install Python with Homebrew
   - `brew install python`

2. Navigate to the agent-service directory
   - `cd agent-service`

3. Create a virtual environment
   - `python -m venv .venv`

4. Activate the virtual environment
   - `source .venv/bin/activate`
   - Your prompt should now show `(agent-service)` at the beginning

5. Install pip if not available in the virtual environment
   - `python -m ensurepip --upgrade`

6. Install dependencies from requirements.txt
   - `python -m pip install -r requirements.txt`
   - If requirements.txt doesn't exist, install the required packages:
     - `python -m pip install fastapi uvicorn openai-agents tenacity cachetools`
     - Create requirements.txt for future use: `python -m pip freeze > requirements.txt`

7. Startup the Micro-Service
   - `python -m uvicorn main:app --port 5100 --reload`

8. To deactivate the virtual environment when done
   - `deactivate`