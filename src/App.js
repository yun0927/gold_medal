import React, { useState } from "react";

const events = [
  "Free50", "Free100", "Fly50", "Fly100", "Back50", "Back100", "Breast50", "Breast100"
];

const ages = ["20-24", "25-29"];
const genders = ["M", "F"];

function timeToSeconds(timeStr) {
  // "1:30" → 90초 변환
  if (!timeStr) return null;
  const parts = timeStr.split(":");
  if (parts.length === 2) {
    const min = parseInt(parts[0], 10);
    const sec = parseFloat(parts[1]);
    if (isNaN(min) || isNaN(sec)) return null;
    return min * 60 + sec;
  }
  return parseFloat(timeStr);
}

export default function App() {
  const [gender, setGender] = useState("M");
  const [age, setAge] = useState("20-24");
  const [event, setEvent] = useState("Free50");
  const [timeInput, setTimeInput] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const onSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    const time_sec = timeToSeconds(timeInput);

    try {
      const response = await fetch("http://localhost:8000/predict_rank", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ gender, age, event, time_sec }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "API 요청 실패");
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 480, margin: "auto", padding: 20 }}>
      <h2>수영 기록 순위 예측</h2>
      <form onSubmit={onSubmit}>
        <label>
          성별:
          <select value={gender} onChange={(e) => setGender(e.target.value)}>
            {genders.map((g) => (
              <option key={g} value={g}>{g}</option>
            ))}
          </select>
        </label>
        <br />
        <label>
          연령대:
          <select value={age} onChange={(e) => setAge(e.target.value)}>
            {ages.map((a) => (
              <option key={a} value={a}>{a}</option>
            ))}
          </select>
        </label>
        <br />
        <label>
          종목:
          <select value={event} onChange={(e) => setEvent(e.target.value)}>
            {events.map((ev) => (
              <option key={ev} value={ev}>{ev}</option>
            ))}
          </select>
        </label>
        <br />
        <label>
          기록 (mm:ss 또는 초):
          <input
            type="text"
            placeholder="예: 1:30 또는 90"
            value={timeInput}
            onChange={(e) => setTimeInput(e.target.value)}
          />
        </label>
        <br />
        <button type="submit" disabled={loading}>
          {loading ? "예측중..." : "순위 예측 / 조회"}
        </button>
      </form>

      {error && <p style={{ color: "red" }}>에러: {error}</p>}

      {result && (
        <div style={{ marginTop: 20 }}>
          {"user_rank" in result ? (
            <>
              <h3>예측 결과</h3>
              <p>
                입력 기록 순위: {result.user_rank} / {result.total_participants}명 중
              </p>
            </>
          ) : (
            <h3>상위 3명 기록 (입력 기록 없음)</h3>
          )}
          <table border="1" cellPadding="5" cellSpacing="0" style={{ width: "100%", marginTop: 10 }}>
            <thead>
              <tr>
                <th>종목</th>
                <th>연령</th>
                <th>성별</th>
                <th>대회명</th>
                <th>기록</th>
              </tr>
            </thead>
            <tbody>
              {result.top3.map((row, i) => (
                <tr key={i}>
                  <td>{row.event}</td>
                  <td>{row.age}</td>
                  <td>{row.gender}</td>
                  <td>{row.meet}</td>
                  <td>{row.time}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}





