import React, { useState } from 'react';
import { ChatPanel } from './components/ChatPanel';
import { ReportPanel } from './components/ReportPanel';
import { Input, Message, StreamOutput, FormResult, FormRequest, ChoiceRequest, ChoiceResult, MessageDelta, StreamingDisplayOutput } from './types/api';
import { agentService } from './services/agent';
import './App.css';

function App() {
  const [messages, setMessages] = useState<Input[]>([]);
  const [processMessages, setProcessMessages] = useState<StreamOutput[]>([]);
  const [streamingContent, setStreamingContent] = useState<string>('');
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
        let isStreamingMessage = false;
        let currentStreamingText = '';

        for await (const output of stream) {
          if (output.type === 'message') {
             // Final message received. Replace streaming content.
             assistantContent = output.content;
             
             if (isStreamingMessage) {
                 const lastMsg = currentMessages[currentMessages.length - 1] as Message;
                 lastMsg.content = assistantContent;
             } else {
                 const assistantMessage: Message = {
                    role: 'assistant',
                    content: assistantContent,
                    type: 'message',
                    details: [...currentProcessMessages]
                };
                currentMessages.push(assistantMessage);
                isStreamingMessage = true;
             }
             setMessages([...currentMessages]);

          } else if (output.type === 'message_delta') {
            assistantContent += output.content;
            
            // Handle streaming update for message content
            if (isStreamingMessage) {
                const lastMsg = currentMessages[currentMessages.length - 1] as Message;
                lastMsg.content = assistantContent;
            } else {
                const assistantMessage: Message = {
                    role: 'assistant',
                    content: assistantContent,
                    type: 'message',
                    details: [...currentProcessMessages]
                };
                currentMessages.push(assistantMessage);
                isStreamingMessage = true;
                // We keep currentProcessMessages in case we need to append more details later
            }
            setMessages([...currentMessages]);

          } else if (output.type === 'streaming_display') {
             currentStreamingText += output.content;
             if (currentStreamingText.length > 20) {
                 currentStreamingText = currentStreamingText.slice(-20);
             }
             setStreamingContent(currentStreamingText);
          } else if (output.type === 'form_request') {
             isStreamingMessage = false;
             assistantContent = '';
             currentProcessMessages = []; 
             
            const formRequest: FormRequest = {
                type: 'form_request',
                rows: output.rows
            };
            currentMessages.push(formRequest);
            setMessages([...currentMessages]);
            
          } else if (output.type === 'choice_request') {
             isStreamingMessage = false;
             assistantContent = '';
             currentProcessMessages = [];

             const choiceRequest: ChoiceRequest = {
                 type: 'choice_request',
                 options: output.options,
                 single_choice: output.single_choice
             };
             currentMessages.push(choiceRequest);
             setMessages([...currentMessages]);

          } else {
            // Process message (thinking, tool_call, tool_response)
            currentProcessMessages.push(output);
            setProcessMessages([...currentProcessMessages]);
            
            // If we are currently streaming a message, attach this detail to it as well
            if (isStreamingMessage) {
                const lastMsg = currentMessages[currentMessages.length - 1] as Message;
                if (!lastMsg.details) lastMsg.details = [];
                lastMsg.details.push(output);
                setMessages([...currentMessages]);
            }
          }
        }

        // Add final assistant message logic is handled by streaming updates, 
        // but if the loop finishes and we have content that wasn't added (unlikely with streaming logic, but safe to keep)
        if (assistantContent && !isStreamingMessage) {
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
        setStreamingContent(''); // Clear streaming display

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
        setStreamingContent('');
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
              streamingContent={streamingContent}
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
