# AI Agent UI Service

A modern AI assistant frontend interface built with React + TypeScript + Vite.

## Features

- 🎨 **Modern UI Design**: Gradient colors, smooth animations, responsive layout
- 💬 **Real-time Chat**: Smooth conversation with AI assistant
- 📊 **Real-time Reports**: Display HTML analysis reports in real-time on the right side
- 🔄 **Streaming**: Real-time streaming data display based on SSE
- 📱 **Responsive Design**: Perfect support for desktop and mobile devices

## Tech Stack

- **Frontend Framework**: React 18
- **Language**: TypeScript
- **Build Tool**: Vite 5
- **Backend**: FastAPI + Python
- **AI Model**: OpenAI GPT-4.1

## Project Structure

```
frontend/
├── src/
│   ├── components/         # React components
│   │   ├── ChatPanel.tsx   # Chat panel
│   │   ├── ChatPanel.css
│   │   ├── ReportPanel.tsx # Report panel
│   │   └── ReportPanel.css
│   ├── services/           # API services
│   │   └── agent.ts        # Agent service wrapper
│   ├── types/              # TypeScript type definitions
│   │   └── api.ts
│   ├── App.tsx             # Main application component
│   ├── App.css
│   ├── main.tsx            # Application entry
│   └── index.css
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

## Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start Backend Service

In the project root directory:

```bash
python agent_service.py
```

Backend service will run at http://localhost:8000

### 3. Start Frontend Development Server

```bash
npm run dev
```

Frontend service will run at http://localhost:3000

### 4. Access Application

Open browser and visit: http://localhost:3000

## Build for Production

```bash
npm run build
```

Build artifacts will be generated in the `dist/` directory

## API Endpoints

### POST /trigger

Send message to AI assistant

**Request Body**:
```json
{
  "context": [
    {
      "role": "user",
      "content": "Hello"
    }
  ]
}
```

**Response**: Server-Sent Events (SSE) stream

Response types:
- `thinking`: AI thinking process
- `tool_call`: Tool call information
- `tool_response`: Tool return results
- `message`: AI reply message

### GET /html_report.html

Get HTML report content

## Feature Description

### Chat Interface (Left Side)

- ✅ Message history
- ✅ User input box
- ✅ Send button
- ✅ Real-time display of AI processing
- ✅ Visualization of thinking, tool calls, and tool responses
- ✅ Elegant message animations

### Report Interface (Right Side)

- ✅ Load HTML reports from local files
- ✅ Real-time refresh
- ✅ Beautiful style overrides
- ✅ Error handling and retry mechanism

### User Experience Optimization

- ✅ Smooth gradient color theme
- ✅ Auto-scroll to latest message
- ✅ Loading state indicators
- ✅ Responsive layout (supports mobile)
- ✅ Smooth transition animations
- ✅ Custom scrollbar styles

## Development Guide

### Adding New Features

1. Define types in `src/types/api.ts`
2. Implement API calls in `src/services/`
3. Create UI components in `src/components/`
4. Integrate new features in `App.tsx`

### Customizing Styles

- Theme colors are defined in each `.css` file
- Use gradient colors to create a modern feel
- Follow unified design standards

## Browser Support

- Chrome >= 90
- Firefox >= 88
- Safari >= 14
- Edge >= 90

## License

MIT
