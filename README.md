# Simple Agent

A simple implementation of LLM agent, using Openai/Gemini/Claude APIs.


## Usage

Create a .env file by copying .env.example, while providing the actual api key(s).

```bash
sh ./start.sh
```

Then visit http://localhost:3000/

## Agent Ablity Scope

The ability of the agent is bounded by the set of tools that it can call. The list below describes what the agent ability 

- [x] write html report
- [x] provide choices for user to choose
- [x] provide forms for user to complete
- [ ] update html report


## Repo Structure

### Backend

The backend part is just an agent FastAPI service. The schema which defines the interaction between frontend and backend is also defined.

### Frontend

AI assistant frontend interface built with React + TypeScript + Vite. Completedly written by AI.

