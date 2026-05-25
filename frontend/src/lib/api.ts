const BASE_URL: string =
  import.meta.env.VITE_BACKEND_URL ?? 'https://agentweaver-ve9r.onrender.com';

export interface DemoWorkflowResponse {
  message: string;
  workflow_id: string;
  check_dashboard: string;
}

export async function triggerDemoWorkflow(): Promise<DemoWorkflowResponse> {
  const res = await fetch(`${BASE_URL}/api/test/demo-workflow`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });

  if (!res.ok) {
    throw new Error(`HTTP ${res.status}`);
  }

  return res.json() as Promise<DemoWorkflowResponse>;
}
