import { useEffect, useState } from "react";

const DrowsinessMonitor = () => {
  const [status, setStatus] = useState("Initializing...");

  useEffect(() => {
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
    <div style={{ position: "fixed", top: 10, right: 20, background: "#fff", padding: "10px", border: "1px solid #ccc", borderRadius: "10px", zIndex: 9999 }}>
      <strong>Status:</strong>{" "}
      <span style={{ color: status.includes("Drowsy") ? "red" : "green" }}>
        {status}
      </span>
    </div>
  );
};

export default DrowsinessMonitor;
