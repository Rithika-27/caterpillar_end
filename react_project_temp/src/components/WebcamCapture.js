import React, { useRef, useEffect, useState } from "react";
import Webcam from "react-webcam";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const WebcamCapture = () => {
  const webcamRef = useRef(null);
  const [seatbeltDetected, setSeatbeltDetected] = useState(false);
  const [result, setResult] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const interval = setInterval(() => {
      capture();
    }, 3000); // every 3 seconds

    return () => clearInterval(interval);
  }, []);

  const capture = async () => {
    const imageSrc = webcamRef.current.getScreenshot();
    try {
      const response = await axios.post("http://localhost:5000/detect_seatbelt", {
        image: imageSrc,
      });

      const detected = response.data.seatbelt_detected;
      setSeatbeltDetected(detected);
      setResult(detected ? "Seatbelt: YES" : "Seatbelt: NO");
    } catch (err) {
      console.error("Error:", err);
    }
  };

  const handleNext = () => {
    navigate("/helmet-check");
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
        onClick={handleNext}
        disabled={!seatbeltDetected}
        style={{
          padding: "10px 20px",
          fontSize: "16px",
          marginTop: "20px",
          backgroundColor: seatbeltDetected ? "#28a745" : "#ccc",
          color: seatbeltDetected ? "white" : "#333",
          border: "none",
          cursor: seatbeltDetected ? "pointer" : "not-allowed",
        }}
      >
        Next
      </button>
    </div>
  );
};

export default WebcamCapture;
