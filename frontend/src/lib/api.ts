const BASE_HTTP_URL: string =
  import.meta.env.VITE_BACKEND_HTTP_URL ?? 'https://agentweaver-ve9r.onrender.com';

export interface ChatMessageResponse {
  workflow_id: string;
}

export async function sendChatMessage(message: string): Promise<ChatMessageResponse> {
  const res = await fetch(`${BASE_HTTP_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  });

  if (!res.ok) {
    throw new Error(`HTTP ${res.status}`);
  }

  return res.json() as Promise<ChatMessageResponse>;
}
