import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [supports, setSupports] = useState([]);
  const [spans, setSpans] = useState([]);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post('http://localhost:5000/api/beam-analysis', {
        supports: supports,
        spans: spans
      });

      setResults(response.data);
    } catch (err) {
      setError("Error fetching results.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Beam Analysis</h1>

      {/* UI for user input (supports and spans) */}
      <div>
        <label>Supports:</label>
        <input
          type="text"
          value={supports}
          onChange={(e) => setSupports(e.target.value)}
          placeholder="Enter supports data"
        />
      </div>

      <div>
        <label>Spans:</label>
        <input
          type="text"
          value={spans}
          onChange={(e) => setSpans(e.target.value)}
          placeholder="Enter spans data"
        />
      </div>

      <button onClick={handleSubmit}>Submit</button>

      {loading && <p>Loading...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}

      {/* Display the results */}
      {results && (
        <div>
          <h2>Results</h2>
          <h3>Fixed-End Moments (FEM)</h3>
          <pre>{JSON.stringify(results.fem_results, null, 2)}</pre>
          
          <h3>Slope Deflection Results</h3>
          <pre>{JSON.stringify(results.slope_deflection_results, null, 2)}</pre>
          
          <h3>Adjusted Results</h3>
          <pre>{JSON.stringify(results.adjusted_results, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default App;
