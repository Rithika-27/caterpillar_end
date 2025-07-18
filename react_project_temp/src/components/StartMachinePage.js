import React, { useEffect, useState } from "react";

const StartMachinePage = () => {
  const [status, setStatus] = useState("Initializing...");

  useEffect(() => {
    // Start drowsiness detection backend thread
    fetch("http://localhost:5000/start-drowsiness");

    const interval = setInterval(() => {
      fetch("http://localhost:5000/drowsiness-status")
        .then((res) => res.json())
        .then((data) => setStatus(data.status))
        .catch(() => setStatus("Error"));
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ textAlign: "center", marginTop: "50px" }}>
      <h2>✅ Machine Started</h2>
      <p>You may proceed with operations.</p>
      <h3>
        Drowsiness Status:{" "}
        <span style={{ color: status.includes("Drowsy") ? "red" : "green" }}>
          {status}
        </span>
      </h3>
    </div>
  );
};

export default StartMachinePage;
