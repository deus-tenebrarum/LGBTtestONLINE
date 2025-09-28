import { useState } from "react";

function App() {
  const [shrInput, setShrInput] = useState("");
  const [result, setResult] = useState(null);

  const handleParse = async () => {
    try {
      const response = await fetch("http://127.0.0.1:5000/parse", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ shr: shrInput }),
      });
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setResult({ error: err.message });
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>SHR Parser</h1>
      <textarea
        rows="6"
        cols="60"
        value={shrInput}
        onChange={(e) => setShrInput(e.target.value)}
        placeholder="Вставь SHR-строку"
      />
      <br />
      <button onClick={handleParse} style={{ marginTop: "10px" }}>
        Распарсить
      </button>
      <pre style={{ marginTop: "20px" }}>
        {result ? JSON.stringify(result, null, 2) : "Результат появится здесь"}
      </pre>
    </div>
  );
}

export default App;
