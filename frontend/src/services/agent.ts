import { UIContext, StreamOutput } from '../types/api';

export class AgentService {
  // In development, connect directly to backend to avoid Vite proxy buffering issues
  // @ts-ignore - Vite env variables
  private baseUrl = import.meta.env.DEV ? `http://${window.location.hostname}:8000` : '';

  async *streamChat(context: UIContext): AsyncGenerator<StreamOutput, void, unknown> {
    const response = await fetch(`${this.baseUrl}/trigger`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Cache-Control': 'no-cache',
      },
      body: JSON.stringify(context),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No response body');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === 'done') {
              return;
            }
            try {
              const parsed = JSON.parse(data) as StreamOutput;
              yield parsed;
            } catch (e) {
              console.error('Failed to parse SSE data:', e);
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  async loadHtmlReport(userId?: string): Promise<string> {
    // Add timestamp parameter to prevent browser caching
    const timestamp = new Date().getTime();
    let url = `${this.baseUrl}/temp/html_report.html?t=${timestamp}`;
    if (userId) {
      url += `&user_id=${encodeURIComponent(userId)}`;
    }
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Failed to load HTML report: ${response.status}`);
    }
    return await response.text();
  }
}

export const agentService = new AgentService();

