import React, { useRef, useEffect, useState } from "react";
import Webcam from "react-webcam";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const HelmetDetection = () => {
  const webcamRef = useRef(null);
  const [helmetDetected, setHelmetDetected] = useState(false);
  const [result, setResult] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const interval = setInterval(() => {
      capture();
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const capture = async () => {
    const imageSrc = webcamRef.current.getScreenshot();
    try {
      const response = await axios.post("http://localhost:5000/detect_helmet", {
        image: imageSrc,
      });
      const detected = response.data.helmet_detected;
      setHelmetDetected(detected);
      setResult(detected ? "Helmet: YES" : "Helmet: NO");
    } catch (err) {
      console.error("Error:", err);
    }
  };

  const handleStartMachine = () => {
    navigate("/Home")
  };

  return (
    <div style={{ textAlign: "center", padding: "20px" }}>
      <Webcam
        audio={false}
        ref={webcamRef}
        screenshotFormat="image/jpeg"
        width={640}
        height={480}
      />
      <h2>{result}</h2>
      <button
        onClick={handleStartMachine}
        disabled={!helmetDetected}
        style={{
          padding: "10px 20px",
          fontSize: "16px",
          marginTop: "20px",
          backgroundColor: helmetDetected ? "#007bff" : "#ccc",
          color: helmetDetected ? "white" : "#333",
          border: "none",
          cursor: helmetDetected ? "pointer" : "not-allowed",
        }}
      >
        Start Machine
      </button>
    </div>
  );
};

export default HelmetDetection;
