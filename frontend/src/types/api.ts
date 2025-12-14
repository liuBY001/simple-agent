// API types matching the backend

export interface FormRow {
  header: string;
  content: string;
}

export interface FormRequest {
  type: 'form_request';
  rows: FormRow[];
}

export interface FormResult {
  type: 'form_result';
  rows: FormRow[];
}

export interface ChoiceRequest {
  type: 'choice_request';
  options: string[];
  single_choice: boolean;
}

export interface ChoiceResult {
  type: 'choice_result';
  chosen: string[];
}

export interface Message {
  type?: 'message'; // Optional for backward compatibility if needed, but backend uses it
  role: 'user' | 'assistant';
  content: string;
  details?: StreamOutput[];
}

export type Input = Message | FormRequest | FormResult | ChoiceRequest | ChoiceResult;

export interface UIContext {
  context: Input[];
  user_id?: string;
}

export type OutputType = 'message' | 'thinking' | 'tool_call' | 'tool_response' | 'form_request' | 'choice_request';

export interface BaseOutput {
  type: OutputType;
  content?: string; // Content is optional because FormRequest/ChoiceRequest use other fields
}

export interface MessageOutput extends BaseOutput {
  type: 'message';
  role: 'assistant';
  content: string;
}

export interface ThinkingOutput extends BaseOutput {
  type: 'thinking';
  content: string;
}

export interface ToolCallOutput extends BaseOutput {
  type: 'tool_call';
  content: string;
}

export interface ToolResponseOutput extends BaseOutput {
  type: 'tool_response';
  content: string;
}

export interface FormRequestOutput {
  type: 'form_request';
  rows: FormRow[];
}

export interface ChoiceRequestOutput {
  type: 'choice_request';
  options: string[];
  single_choice: boolean;
}

export type StreamOutput = MessageOutput | ThinkingOutput | ToolCallOutput | ToolResponseOutput | FormRequestOutput | ChoiceRequestOutput;
