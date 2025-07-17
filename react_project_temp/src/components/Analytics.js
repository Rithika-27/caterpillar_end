import React, { useEffect, useState } from "react";
import axios from "axios";
import "./Analytics.css";

export default function Analytics() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    axios
      .get("http://localhost:5000/api/analytics")
      .then((res) => setStats(res.data))
      .catch((err) => console.error("Analytics fetch error:", err));
  }, []);

  return (
    <div className="analytics-container">
      <h1 className="analytics-title">Fleet Analytics</h1>
      {stats ? (
        <div className="analytics-cards">
          <div className="analytics-card">
            <h3>Total Machines</h3>
            <p>{stats.total_machines}</p>
          </div>
          <div className="analytics-card">
            <h3>Total Fuel Used</h3>
            <p>{stats.total_fuel} L</p>
          </div>
          <div className="analytics-card">
            <h3>Avg Engine Hours</h3>
            <p>{stats.average_engine_hours}</p>
          </div>
          <div className="analytics-card">
            <h3>Tasks Completed</h3>
            <p>{stats.completed_tasks}</p>
          </div>
          <div className="analytics-card">
            <h3>In Progress</h3>
            <p>{stats.in_progress_tasks}</p>
          </div>
        </div>
      ) : (
        <p>Loading analytics...</p>
      )}
    </div>
  );
}
