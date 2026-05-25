import { useEffect, useReducer, useRef, useCallback } from 'react';
import { sendChatMessage } from '../lib/api';

// ─── Types ────────────────────────────────────────────────────────────────────

export type ConnectionState = 'connecting' | 'connected' | 'disconnected';

export type AgentStatus = 'idle' | 'busy';

export interface AgentState {
  id: string;
  status: AgentStatus;
  currentTask: string | null;
}

export interface TimelineEvent {
  id: string;
  timestamp: string;
  agentId: string | null;
  type: 'workflow_started' | 'step_completed' | 'workflow_completed' | 'agent_update' | 'system';
  label: string;
  detail: string | null;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  workflowId?: string;
  latestOutputs?: Record<string, unknown>;
  executionTime?: number;
}

export interface WorkflowState {
  connection: ConnectionState;
  agents: Record<string, AgentState>;
  timeline: TimelineEvent[];
  progress: number;
  isRunning: boolean;
  completionTime: number | null;
  workflowStartedAt: number | null;
  messages: ChatMessage[];
  latestOutputs: Record<string, unknown>;
  synthesisMarkdown: string | null;
  activeWorkflowId: string | null;
}

// ─── Initial State ─────────────────────────────────────────────────────────

const AGENT_IDS = ['text_analyzer', 'data_processor', 'api_client'];

const AGENT_LABELS: Record<string, string> = {
  text_analyzer: 'Text Analyzer',
  data_processor: 'Data Processor',
  api_client: 'API Client',
};

function makeInitialAgents(): Record<string, AgentState> {
  const agents: Record<string, AgentState> = {};
  for (const id of AGENT_IDS) {
    agents[id] = { id, status: 'idle', currentTask: null };
  }
  return agents;
}

const initialState: WorkflowState = {
  connection: 'disconnected',
  agents: makeInitialAgents(),
  timeline: [],
  progress: 0,
  isRunning: false,
  completionTime: null,
  workflowStartedAt: null,
  messages: [],
  latestOutputs: {},
  synthesisMarkdown: null,
  activeWorkflowId: null,
};

// ─── Reducer ───────────────────────────────────────────────────────────────

type Action =
  | { type: 'SET_CONNECTION'; state: ConnectionState }
  | { type: 'WS_MESSAGE'; raw: string }
  | { type: 'SEND_USER_MESSAGE'; content: string };

let eventCounter = 0;
function makeId() {
  return `ev-${++eventCounter}`;
}

let msgCounter = 0;
function makeMsgId() {
  return `msg-${++msgCounter}`;
}

function fmt(ts: string): string {
  try {
    const d = new Date(ts);
    return d.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
  } catch {
    return ts;
  }
}

function reducer(state: WorkflowState, action: Action): WorkflowState {
  if (action.type === 'SET_CONNECTION') {
    return { ...state, connection: action.state };
  }

  if (action.type === 'SEND_USER_MESSAGE') {
    const userMsg: ChatMessage = {
      id: makeMsgId(),
      role: 'user',
      content: action.content,
      workflowId: 'pending',
    };
    return {
      ...state,
      messages: [...state.messages, userMsg],
      activeWorkflowId: 'pending',
    };
  }

  if (action.type === 'WS_MESSAGE') {
    let msg: Record<string, unknown>;
    try {
      msg = JSON.parse(action.raw) as Record<string, unknown>;
    } catch {
      return state;
    }

    const msgType = msg.type as string;

    if (msgType === 'connection_established' || msgType === 'system_status') {
      return state;
    }

    if (msgType === 'workflow_update') {
      const event = msg.event as string;
      const progress = typeof msg.progress === 'number' ? msg.progress : state.progress;
      const details = (msg.details ?? {}) as Record<string, unknown>;
      const ts = (msg.timestamp as string) ?? new Date().toISOString();

      if (event === 'workflow_started') {
        const workflowId = (msg.workflow_id as string) ?? makeId();
        const ev: TimelineEvent = {
          id: makeId(),
          timestamp: fmt(ts),
          agentId: null,
          type: 'workflow_started',
          label: 'Workflow started',
          detail: `ID: ${workflowId.slice(-8)}`,
        };
        return {
          ...state,
          isRunning: true,
          completionTime: null,
          workflowStartedAt: Date.now(),
          progress: 0,
          timeline: [ev],
          latestOutputs: {},
          synthesisMarkdown: null,
          activeWorkflowId: workflowId,
        };
      }

      if (event === 'step_completed') {
        const stepData = (details.step_data ?? {}) as Record<string, unknown>;
        const stepName = (details.step as string) ?? (msg.current_step as string) ?? 'step';
        const ev: TimelineEvent = {
          id: makeId(),
          timestamp: fmt(ts),
          agentId: null,
          type: 'step_completed',
          label: `Step complete — ${stepName.replace(/_/g, ' ')}`,
          detail: null,
        };
        const newOutputs = { ...state.latestOutputs, [stepName]: stepData };
        const newSynthesis =
          stepName === 'synthesis'
            ? ((stepData as { reply_markdown?: string }).reply_markdown ?? state.synthesisMarkdown)
            : state.synthesisMarkdown;
        return {
          ...state,
          progress,
          timeline: [...state.timeline, ev],
          latestOutputs: newOutputs,
          synthesisMarkdown: newSynthesis,
        };
      }

      if (event === 'workflow_completed') {
        const execTime = details.execution_time as number | undefined;
        const elapsed = state.workflowStartedAt ? (Date.now() - state.workflowStartedAt) / 1000 : null;
        const timeVal = execTime ?? elapsed ?? null;
        const ev: TimelineEvent = {
          id: makeId(),
          timestamp: fmt(ts),
          agentId: null,
          type: 'workflow_completed',
          label: 'Workflow complete',
          detail: timeVal !== null ? `${timeVal.toFixed(1)}s total` : null,
        };
        const replyContent = state.synthesisMarkdown ?? '_No synthesis received._';
        const assistantMsg: ChatMessage = {
          id: makeMsgId(),
          role: 'assistant',
          content: replyContent,
          workflowId: state.activeWorkflowId ?? undefined,
          latestOutputs: { ...state.latestOutputs },
          executionTime: timeVal ?? undefined,
        };
        return {
          ...state,
          progress: 1,
          isRunning: false,
          completionTime: timeVal,
          timeline: [...state.timeline, ev],
          messages: [...state.messages, assistantMsg],
        };
      }

      return state;
    }

    if (msgType === 'agent_update') {
      const agentId = msg.agent_id as string;
      const status = (msg.status as AgentStatus) ?? 'idle';
      const details = (msg.details ?? {}) as Record<string, unknown>;
      const currentTask = (details.current_task as string | null) ?? null;
      const ts = (msg.timestamp as string) ?? new Date().toISOString();

      const updatedAgents = {
        ...state.agents,
        [agentId]: {
          id: agentId,
          status,
          currentTask: status === 'idle' ? null : currentTask,
        },
      };

      if (status === 'busy' && currentTask) {
        const ev: TimelineEvent = {
          id: makeId(),
          timestamp: fmt(ts),
          agentId,
          type: 'agent_update',
          label: AGENT_LABELS[agentId] ?? agentId,
          detail: currentTask,
        };
        return { ...state, agents: updatedAgents, timeline: [...state.timeline, ev] };
      }

      return { ...state, agents: updatedAgents };
    }

    return state;
  }

  return state;
}

// ─── Hook ──────────────────────────────────────────────────────────────────

const WS_URL: string =
  import.meta.env.VITE_BACKEND_WS_URL ?? 'wss://agentweaver-ve9r.onrender.com/ws/updates';

export function useWorkflowStream() {
  const [state, dispatch] = useReducer(reducer, initialState);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const mountedRef = useRef(true);

  const connect = useCallback(() => {
    if (!mountedRef.current) return;
    if (wsRef.current && wsRef.current.readyState < 2) return;

    dispatch({ type: 'SET_CONNECTION', state: 'connecting' });

    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      if (!mountedRef.current) return;
      dispatch({ type: 'SET_CONNECTION', state: 'connected' });
    };

    ws.onmessage = (e: MessageEvent) => {
      if (!mountedRef.current) return;
      dispatch({ type: 'WS_MESSAGE', raw: e.data as string });
    };

    ws.onerror = () => {
      // Intentionally no-op — onclose handles reconnection
    };

    ws.onclose = () => {
      if (!mountedRef.current) return;
      dispatch({ type: 'SET_CONNECTION', state: 'disconnected' });
      reconnectTimer.current = setTimeout(() => {
        if (mountedRef.current) connect();
      }, 4000);
    };
  }, []);

  useEffect(() => {
    mountedRef.current = true;
    connect();
    return () => {
      mountedRef.current = false;
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
      wsRef.current?.close();
    };
  }, [connect]);

  const sendMessage = useCallback((content: string) => {
    dispatch({ type: 'SEND_USER_MESSAGE', content });
    sendChatMessage(content).catch(() => {
      // WS stream is source of truth; HTTP failure is non-blocking
    });
  }, []);

  return { ...state, sendMessage };
}
