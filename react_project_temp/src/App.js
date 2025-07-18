import React from "react";
import { BrowserRouter as Router, Routes, Route, useNavigate } from "react-router-dom";
import Home from "./pages/Home.js";
import Dashboard from "./components/Dashboard";
import ELearning from "./components/ELearning";
import Analytics from "./components/Analytics"; 
import WebcamCapture from "./components/WebcamCapture";
import StartMachinePage from "./components/StartMachinePage.js"; // ✅ import
import HelmetDetection from "./components/HelmetDetection"; // ✅ add this

function StartPage() {
  const navigate = useNavigate();

  const handleStart = () => {
    navigate("/capture");
  };

  return (
    <div style={{ textAlign: "center", marginTop: "50px" }}>
      <button onClick={handleStart}>Get Started</button>
    </div>
  );
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/Home" element={<Home />} />
        <Route path="/" element={<StartPage />} />
        <Route path="/capture" element={<WebcamCapture />} />
        <Route path="/start-machine" element={<StartMachinePage />} /> {/* ✅ works now */}
        <Route path="/helmet-check" element={<HelmetDetection />} /> {/* ✅ new page */}
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/elearning" element={<ELearning />} />
        <Route path="/analytics" element={<Analytics />} />
      </Routes>
    </Router>
    
  );
}

export default App;
