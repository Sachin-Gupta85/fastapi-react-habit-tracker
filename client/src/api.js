const BASE = import.meta.env?.VITE_API_URL || "";
async function req(path, opts) {
  const res = await fetch(`${BASE}/api${path}`, {
    headers: { "Content-Type": "application/json" }, ...opts });
  if (!res.ok) throw new Error(`${res.status}`);
  return res.status === 204 ? null : res.json();
}
export const listHabits = () => req("/habits");
export const createHabit = (name) => req("/habits", { method: "POST", body: JSON.stringify({ name }) });
export const checkIn = (id, date) => req(`/habits/${id}/checkin`, { method: "POST", body: JSON.stringify({ date }) });
export const deleteHabit = (id) => req(`/habits/${id}`, { method: "DELETE" });
