// frontend/src/api.js
const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:5000';
// ^ reads your Vite env var we put in frontend/.env

export async function getResume() {
  const res = await fetch(`${API_BASE}/api/resume`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}
