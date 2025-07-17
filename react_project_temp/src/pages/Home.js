import React from "react";
import { useNavigate } from "react-router-dom";
import "./Home.css";

export default function Home() {
  const navigate = useNavigate();

  return (
    <div className="home-container">
      <h1 className="home-title">Welcome to CAT Operator Panel</h1>
      <div className="card-wrapper">
        <div className="card" onClick={() => navigate("/dashboard")}>
          <h2>Schedule</h2>
          <p>View and manage your assigned machine tasks.</p>
        </div>

        <div className="card" onClick={() => navigate("/elearning")}>
          <h2>E-Learning</h2>
          <p>Learn how to operate machines through Caterpillar videos.</p>
        </div>

        <div className="card" onClick={() => navigate("/analytics")}>
          <h2>Analytics</h2>
          <p>Fuel usage and engine efficiency insights.</p>
        </div>
      </div>
    </div>
  );
}
