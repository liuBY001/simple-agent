import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Message, StreamOutput, Input, FormRequest, FormResult, FormRow, ChoiceRequest, ChoiceResult } from '../types/api';
import './ChatPanel.css';

interface ChatPanelProps {
  messages: Input[];
  processMessages: StreamOutput[];
  onSendMessage: (message: string | FormResult | ChoiceResult) => void;
  isLoading: boolean;
  streamingContent?: string;
}

const FormRequestItem = ({ request, onSubmit, disabled }: { request: FormRequest, onSubmit: (res: FormResult) => void, disabled: boolean }) => {
  const [rows, setRows] = useState<FormRow[]>(request.rows.map(r => ({ ...r })));

  const handleChange = (index: number, val: string) => {
    const newRows = [...rows];
    newRows[index] = { ...newRows[index], content: val };
    setRows(newRows);
  };

  const handleSubmit = () => {
    onSubmit({ type: 'form_result', rows });
  };

  return (
    <div className="message message-assistant form-request">
      <div className="form-title">Please fill in the following information:</div>
      {rows.map((row, idx) => (
        <div key={idx} className="form-row">
          <label>{row.header}</label>
          <input 
            value={row.content} 
            onChange={e => handleChange(idx, e.target.value)} 
            disabled={disabled}
            placeholder={`Please enter ${row.header}`}
          />
        </div>
      ))}
      {!disabled && <button onClick={handleSubmit}>Submit Form</button>}
    </div>
  );
};

const FormResultItem = ({ result }: { result: FormResult }) => {
  return (
    <div className="message message-user form-result">
      <div className="form-title">Submitted Information:</div>
      {result.rows.map((row, idx) => (
        <div key={idx} className="form-row-display">
          <strong>{row.header}:</strong> <span>{row.content}</span>
        </div>
      ))}
    </div>
  );
};

const ChoiceRequestItem = ({ request, onSubmit, disabled }: { request: ChoiceRequest, onSubmit: (res: ChoiceResult) => void, disabled: boolean }) => {
  const [selected, setSelected] = useState<string[]>([]);

  const handleSelect = (option: string) => {
    if (disabled) return;
    
    if (request.single_choice) {
      setSelected([option]);
    } else {
      if (selected.includes(option)) {
        setSelected(selected.filter(s => s !== option));
      } else {
        setSelected([...selected, option]);
      }
    }
  };

  const handleSubmit = () => {
    if (selected.length === 0) return;
    onSubmit({ type: 'choice_result', chosen: selected });
  };

  return (
    <div className="message message-assistant form-request">
      <div className="form-title">{request.single_choice ? "Please select one:" : "Please select multiple:"}</div>
      <div className="choice-list">
        {request.options.map((option, idx) => {
            const isSelected = selected.includes(option);
            return (
                <div 
                  key={idx} 
                  className={`choice-option ${isSelected ? 'selected' : ''} ${disabled ? 'disabled' : ''}`}
                  onClick={() => handleSelect(option)}
                >
                    <div className="choice-checkbox">
                        {isSelected ? '✓' : ''}
                    </div>
                    <span>{option}</span>
                </div>
            );
        })}
      </div>
      {!disabled && <button onClick={handleSubmit} disabled={selected.length === 0}>Submit Selection</button>}
    </div>
  );
};

const ChoiceResultItem = ({ result }: { result: ChoiceResult }) => {
    return (
        <div className="message message-user form-result">
          <div className="form-title">Selected:</div>
          <div className="choice-result-list">
             {result.chosen.map((c, i) => (
                 <div key={i} className="choice-result-tag">{c}</div>
             ))}
          </div>
        </div>
      );
}


export const ChatPanel: React.FC<ChatPanelProps> = ({
  messages,
  processMessages,
  onSendMessage,
  isLoading,
  streamingContent
}) => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll logic with smart stickiness and stability
  useEffect(() => {
    if (!containerRef.current || !messagesEndRef.current) return;

    const container = containerRef.current;
    const { scrollTop, scrollHeight, clientHeight } = container;
    
    // Check if user is near the bottom (within 50px threshold)
    const isNearBottom = scrollHeight - scrollTop - clientHeight < 50;

    if (isNearBottom) {
      // Use 'auto' behavior for instant scrolling during rapid streaming updates
      // This prevents the "jumping" effect caused by smooth scroll animation conflicts
      messagesEndRef.current.scrollIntoView({ behavior: 'auto', block: 'end' });
    }
  }, [messages, processMessages, streamingContent]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input.trim());
      setInput('');
      // Force smooth scroll to bottom when user sends a message
      setTimeout(() => {
          messagesEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
      }, 50);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Enter to send, Shift + Enter for new line
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (input.trim() && !isLoading) {
        onSendMessage(input.trim());
        setInput('');
        // Force smooth scroll to bottom when user sends a message
        setTimeout(() => {
            messagesEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
        }, 50);
      }
    }
  };

  const renderProcessMessage = (msg: StreamOutput, index: number) => {
    const typeClass = `process-message-${msg.type}`;
    const iconMap: Record<string, string> = {
      thinking: '💭',
      tool_call: '🔧',
      tool_response: '✅',
      message: '💬',
      form_request: '📋',
      choice_request: '🔢',
      streaming_display: '📺'
    };
    const icon = iconMap[msg.type] || '❓';

    let content = '';
    if ('content' in msg && msg.content) {
        content = msg.content;
    } else if (msg.type === 'form_request') {
        content = 'Generating form request...';
    } else if (msg.type === 'choice_request') {
        content = 'Generating choice request...';
    }

    return (
      <div key={`process-${index}`} className={`process-message ${typeClass}`}>
        <span className="process-icon">{icon}</span>
        <span className="process-content">{content}</span>
      </div>
    );
  };

  return (
    <div className="chat-panel">
      <div className="chat-header">
        <h2>💬 HTML Report Chat</h2>
      </div>

      <div className="messages-container" ref={containerRef}>
        {messages.map((msg, index) => {
          if (msg.type === 'form_request') {
             const isAnswered = messages.slice(index + 1).some(m => m.type === 'form_result');
             const disabled = isAnswered || isLoading; 
             return (
                 <FormRequestItem 
                     key={`msg-${index}`} 
                     request={msg} 
                     onSubmit={onSendMessage} 
                     disabled={disabled}
                 />
             );
          } else if (msg.type === 'form_result') {
             return <FormResultItem key={`msg-${index}`} result={msg} />;
          } else if (msg.type === 'choice_request') {
             const isAnswered = messages.slice(index + 1).some(m => m.type === 'choice_result');
             const disabled = isAnswered || isLoading;
             return (
                 <ChoiceRequestItem
                    key={`msg-${index}`}
                    request={msg}
                    onSubmit={onSendMessage}
                    disabled={disabled}
                 />
             );
          } else if (msg.type === 'choice_result') {
             return <ChoiceResultItem key={`msg-${index}`} result={msg} />;
          } else {
             // It is a Message
             const message = msg as Message;
             return (
              <div key={`msg-${index}`} className={`message message-${message.role}`}>
                <div className="message-avatar">
                  {message.role === 'user' ? '👤' : '🤖'}
                </div>
                <div className="message-content">
                  <div className="message-role">{message.role === 'user' ? 'User' : 'AI Assistant'}</div>
                  {message.details && message.details.length > 0 && (
                    <details className="message-details">
                      <summary className="message-details-summary">
                        Thinking Process & Tool Calls
                      </summary>
                      <div className="message-details-content">
                        {message.details.map((detail, detailIndex) => 
                          renderProcessMessage(detail, detailIndex)
                        )}
                      </div>
                    </details>
                  )}
                  <div className="message-text">
                    {/* @ts-ignore - ReactMarkdown types compatibility issue */}
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {message.content}
                    </ReactMarkdown>
                  </div>
                </div>
              </div>
            );
          }
        })}

        {processMessages.length > 0 && (
          <div className="process-messages">
            <div className="process-title">Processing:</div>
            {processMessages.map(renderProcessMessage)}
          </div>
        )}

        {isLoading && processMessages.length === 0 && !streamingContent && (
          <div className="loading-indicator">
            <div className="loading-spinner"></div>
            <span>AI is thinking...</span>
          </div>
        )}

        {streamingContent && (
            <div className="streaming-bar">
                <div className="streaming-content">{streamingContent}</div>
            </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <form className="input-container" onSubmit={handleSubmit}>
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Please enter your HTML report requirements or content... (Enter to send, Shift + Enter for new line)"
          disabled={isLoading}
          className="message-input"
          rows={1}
        />
        <button
          type="submit"
          disabled={isLoading || !input.trim()}
          className="send-button"
        >
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  );
};
