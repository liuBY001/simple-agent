import React, { useState } from 'react';
import { ChatPanel } from './components/ChatPanel';
import { ReportPanel } from './components/ReportPanel';
import { Input, Message, StreamOutput, FormResult, FormRequest, ChoiceRequest, ChoiceResult } from './types/api';
import { agentService } from './services/agent';
import './App.css';

function App() {
  const [messages, setMessages] = useState<Input[]>([]);
  const [processMessages, setProcessMessages] = useState<StreamOutput[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [reportRefresh, setReportRefresh] = useState(0);
  const [userId, setUserId] = useState<string>('');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [usernameInput, setUsernameInput] = useState('');

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (usernameInput.trim()) {
      setUserId(usernameInput.trim());
      setIsLoggedIn(true);
    }
  };

  const handleSendMessage = (content: string | FormResult | ChoiceResult) => {
    // Add user message
    let newMessages: Input[] = [...messages];
    if (typeof content === 'string') {
       newMessages.push({ role: 'user', content, type: 'message' });
    } else {
       newMessages.push(content);
    }
    
    setMessages(newMessages);
    setProcessMessages([]);
    setIsLoading(true);

    const streamContext = { context: newMessages, user_id: userId };

    const processStream = async () => {
      try {
        // Stream response from agent service
        const stream = agentService.streamChat(streamContext);

        let assistantContent = '';
        // We use a local copy to append form requests during the stream
        let currentMessages = [...newMessages];
        let currentProcessMessages: StreamOutput[] = [];

        for await (const output of stream) {
          if (output.type === 'message') {
            assistantContent += output.content;
          } else if (output.type === 'form_request') {
            // If there is pending text, add it as a message first
            if (assistantContent) {
                const assistantMessage: Message = {
                    role: 'assistant',
                    content: assistantContent,
                    type: 'message',
                    details: [...currentProcessMessages]
                };
                currentMessages.push(assistantMessage);
                assistantContent = '';
                currentProcessMessages = []; // Clear details for next message segment
            }
            
            const formRequest: FormRequest = {
                type: 'form_request',
                rows: output.rows
            };
            currentMessages.push(formRequest);
            setMessages([...currentMessages]);
            
          } else if (output.type === 'choice_request') {
             // If there is pending text, add it as a message first
             if (assistantContent) {
                const assistantMessage: Message = {
                    role: 'assistant',
                    content: assistantContent,
                    type: 'message',
                    details: [...currentProcessMessages]
                };
                currentMessages.push(assistantMessage);
                assistantContent = '';
                currentProcessMessages = []; // Clear details for next message segment
             }

             const choiceRequest: ChoiceRequest = {
                 type: 'choice_request',
                 options: output.options,
                 single_choice: output.single_choice
             };
             currentMessages.push(choiceRequest);
             setMessages([...currentMessages]);

          } else {
            currentProcessMessages.push(output);
            setProcessMessages([...currentProcessMessages]);
          }
        }

        // Add final assistant message to history if there is content
        if (assistantContent) {
          const assistantMessage: Message = {
            role: 'assistant',
            content: assistantContent,
            type: 'message',
            details: currentProcessMessages
          };
          currentMessages.push(assistantMessage);
          setMessages([...currentMessages]);
        }

        // Clear process messages after completion
        setProcessMessages([]);

        // Trigger report refresh
        setReportRefresh((prev) => prev + 1);
      } catch (error) {
        console.error('Error sending message:', error);
        const errorMessage: Message = {
          role: 'assistant',
          content: `Sorry, an error occurred: ${error instanceof Error ? error.message : 'Unknown error'}`,
          type: 'message'
        };
        setMessages([...newMessages, errorMessage]);
      } finally {
        setIsLoading(false);
      }
    };

    void processStream();
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>📝 HTML Report Writing Assistant</h1>
      </header>

      <main className="app-main">
        <div className="panel-container">
          <div className="panel panel-left">
            <ChatPanel
              messages={messages}
              processMessages={processMessages}
              onSendMessage={handleSendMessage}
              isLoading={isLoading}
            />
          </div>

          <div className="panel panel-right">
            <ReportPanel refreshTrigger={reportRefresh} userId={userId} />
          </div>
        </div>
      </main>

      {!isLoggedIn && (
        <div className="login-overlay">
          <div className="login-box">
            <h2>Welcome to HTML Report Writing Assistant</h2>
            <p style={{ fontSize: '14px', color: '#666', marginBottom: '20px' }}>
              Write and organize beautifully structured HTML reports with professional formatting
            </p>
            <form onSubmit={handleLogin}>
              <input
                type="text"
                className="login-input"
                placeholder="Please enter username"
                value={usernameInput}
                onChange={(e) => setUsernameInput(e.target.value)}
                autoFocus
              />
              <button type="submit" className="login-button">
                Get Started
              </button>
            </form>
          </div>
        </div>
      )}

      <footer className="app-footer">
        <p>Powered by OpenAI GPT</p>
      </footer>
    </div>
  );
}

export default App;
