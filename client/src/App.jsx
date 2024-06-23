import React, { useEffect, useState } from "react";
import { listHabits, createHabit, checkIn, deleteHabit } from "./api.js";

const today = () => new Date().toISOString().slice(0, 10);

export default function App() {
  const [habits, setHabits] = useState([]);
  const [name, setName] = useState("");

  async function refresh() { setHabits(await listHabits()); }
  useEffect(() => { refresh(); }, []);

  async function onAdd(e) {
    e.preventDefault();
    if (!name.trim()) return;
    await createHabit(name.trim());
    setName(""); refresh();
  }

  return (
    <main style={{ maxWidth: 560, margin: "2rem auto", fontFamily: "system-ui" }}>
      <h1>🔥 Habit Tracker</h1>
      <form onSubmit={onAdd} style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        <input aria-label="name" placeholder="New habit" value={name} onChange={(e) => setName(e.target.value)} style={{ flex: 1 }} />
        <button type="submit">Add</button>
      </form>
      <ul style={{ listStyle: "none", padding: 0 }}>
        {habits.map((h) => (
          <li key={h.id} style={{ border: "1px solid #ddd", borderRadius: 8, padding: 12, marginBottom: 8 }}>
            <strong>{h.name}</strong>{" "}
            <span>🔥 {h.current_streak} (best {h.longest_streak})</span>
            <button onClick={async () => { await checkIn(h.id, today()); refresh(); }} style={{ marginLeft: 8 }}>
              Check in today
            </button>
            <button onClick={async () => { await deleteHabit(h.id); refresh(); }} style={{ float: "right" }}>Delete</button>
          </li>
        ))}
      </ul>
    </main>
  );
}
