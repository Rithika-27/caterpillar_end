import React from "react";
import "./ELearning.css";

export default function ELearning() {
  const videos = [
    {
      title: "How to Operate a Backhoe",
      url: "https://www.youtube.com/embed/v6oxM2oOvbM",
    },
    {
      title: "Using a Motor Grader Effectively",
      url: "https://www.youtube.com/embed/MrMR9Ezm3NU",
    },
    {
      title: "Tips for Safe Excavator Operation",
      url: "https://www.youtube.com/embed/UJKm0-6w-DY",
    },
  ];

  return (
    <div className="elearning-container">
      <h1>E-Learning: Machine Operation Videos</h1>
      <div className="video-grid">
        {videos.map((video, index) => (
          <div className="video-card" key={index}>
            <h3>{video.title}</h3>
            <iframe
              width="100%"
              height="200"
              src={video.url}
              title={video.title}
              frameBorder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            ></iframe>
          </div>
        ))}
      </div>
    </div>
  );
}
