import { useState } from "react";

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000";

export default function App() {
  const [jdText, setJdText] = useState(
    "We need a Frontend Developer with React, JavaScript, HTML/CSS. Backend Python/Flask and SQL/PostgreSQL a plus. Experience with APIs and Git."
  );
  const [jdSkills, setJdSkills] = useState([]);
  const [match, setMatch] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function extractSkills() {
    setLoading(true);
    setError("");
    setMatch(null);
    try {
      const res = await fetch(`${API}/api/job/parse`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: jdText }),
      });
      const data = await res.json();
      setJdSkills(data.skills || []);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }

  async function doMatch() {
    setLoading(true);
    setError("");
    try {
      const resume = await fetch(`${API}/api/resume`).then(r => r.json());
      const res = await fetch(`${API}/api/match`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ resume, jdSkills }),
      });
      const data = await res.json();
      setMatch(data);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 900, margin: "40px auto", padding: 24, color: "#ddd" }}>
      <h1 style={{ marginBottom: 4 }}>Tristan Tenyay</h1>
      <p style={{ marginTop: 0 }}>Full-Stack Developer</p>

      <hr style={{ opacity: 0.2 }} />

      <h2 style={{ marginTop: 24 }}>Paste a Job Description</h2>
      <textarea
        value={jdText}
        onChange={(e) => setJdText(e.target.value)}
        rows={8}
        style={{ width: "100%", background: "#1e1e1e", color: "#ddd", padding: 12, borderRadius: 8, border: "1px solid #333" }}
      />

      <div style={{ display: "flex", gap: 12, marginTop: 12 }}>
        <button onClick={extractSkills} disabled={loading} style={{ padding: "8px 14px", borderRadius: 8 }}>
          Extract skills
        </button>
        <button onClick={doMatch} disabled={loading || jdSkills.length === 0} style={{ padding: "8px 14px", borderRadius: 8 }}>
          Match to my resume
        </button>
      </div>

      {loading && <p style={{ marginTop: 12 }}>Loading…</p>}
      {error && <p style={{ marginTop: 12, color: "salmon" }}>Error: {error}</p>}

      <div style={{ marginTop: 16 }}>
        <h3>Extracted JD skills</h3>
        {jdSkills.length ? <code>{JSON.stringify(jdSkills)}</code> : <p>(none yet)</p>}
      </div>

      <div style={{ marginTop: 16 }}>
        <h3>Match result</h3>
        {match ? (
          <div>
            <p><b>Score:</b> {match.score}</p>
            <p><b>Matched:</b> {match.coverage?.matched?.join(", ") || "(none)"}</p>
            <p><b>Missing:</b> {match.coverage?.missing?.join(", ") || "(none)"}</p>
            <div>
              <b>Top bullets:</b>
              <ul>
                {(match.topBullets || []).map((b, i) => (
                  <li key={i}>
                    <i>{b.text}</i> — <small>{b.reason}</small>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        ) : (
          <p>(run “Match to my resume”)</p>
        )}
      </div>
    </div>
  );
}
