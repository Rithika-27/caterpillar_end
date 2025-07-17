import React, { useState, useEffect } from "react";
import axios from "axios";
import "./Dashboard.css";

export default function Dashboard() {
  const [allData, setAllData] = useState([]);
  const [operatorId, setOperatorId] = useState("");
  const [filteredData, setFilteredData] = useState([]);
  const [taskStatus, setTaskStatus] = useState({});

  useEffect(() => {
    axios
      .get("http://localhost:5000/api/machine-data")
      .then((res) => setAllData(res.data))
      .catch((err) => console.error("API Error:", err));
  }, []);

  const handleSearch = () => {
    const cleanedInput = operatorId.trim().toLowerCase();
    const result = allData.filter((entry) => {
      const storedId = (entry.operator_id || "").trim().toLowerCase();
      return storedId === cleanedInput;
    });
    setFilteredData(result);
  };

  const updateTaskStatus = async (taskKey, status, machineId, operatorId, task) => {
    const timestamp = new Date().toISOString();

    const updated = {
      ...taskStatus,
      [taskKey]: {
        ...(taskStatus[taskKey] || {}),
        status,
        ...(status === "in_progress"
          ? { startedAt: timestamp }
          : { endedAt: timestamp }),
      },
    };
    setTaskStatus(updated);
    localStorage.setItem("taskStatus", JSON.stringify(updated));

    try {
      await axios.post("http://localhost:5000/api/update-task-status", {
        operator_id: operatorId,
        machine_id: machineId,
        task,
        status,
        timestamp,
      });
    } catch (err) {
      console.error("Failed to update task status on server:", err);
    }
  };

  return (
    <div className="dashboard-container">
      <h1 className="title">Operator Dashboard</h1>

      <div className="input-section">
        <input
          type="text"
          placeholder="Enter your Operator ID"
          value={operatorId}
          onChange={(e) => setOperatorId(e.target.value)}
        />
        <button onClick={handleSearch}>Show Tasks</button>
      </div>

      <div className="cards-container">
        {filteredData.length > 0 ? (
          filteredData.map((entry, i) => {
            const machineId = entry.machine_id;
            const operator = entry.operator_id;
            const tasks = [];
            try {
              const parsed = JSON.parse(entry.tasks_scheduled.replace(/'/g, '"'));
              if (Array.isArray(parsed)) tasks.push(...parsed);
            } catch (e) {
              console.error("Invalid tasks_scheduled format", e);
            }

            // Get task_logs and create a set of completed task names
            const completedTasks = new Set(
              (entry.task_logs || [])
                .filter((t) => t.status === "completed")
                .map((t) => t.task)
            );

            const visibleTasks = tasks.filter((task) => !completedTasks.has(task));

            return (
              <div key={i} className="card">
                <h2>Machine ID: {machineId}</h2>
                <p><strong>Operator:</strong> {operator}</p>
                <hr />
                <h3>Scheduled Tasks:</h3>
                <ul>
                  {visibleTasks.length === 0 ? (
                    <p className="no-tasks-msg">All tasks completed</p>
                  ) : (
                    visibleTasks.map((task, idx) => {
                      const taskKey = `${machineId}-${task}`;
                      const statusObj = taskStatus[taskKey] || {};
                      return (
                        <li key={idx}>
                          <div className="task-row">
                            <span>{task}</span>
                            {statusObj.status === "in_progress" ? (
                              <>
                                <span className="status">In Progress</span>
                                <button
                                  onClick={() =>
                                    updateTaskStatus(
                                      taskKey,
                                      "completed",
                                      machineId,
                                      operator,
                                      task
                                    )
                                  }
                                >
                                  End
                                </button>
                              </>
                            ) : statusObj.status === "completed" ? (
                              <span className="status done">Completed</span>
                            ) : (
                              <button
                                onClick={() =>
                                  updateTaskStatus(
                                    taskKey,
                                    "in_progress",
                                    machineId,
                                    operator,
                                    task
                                  )
                                }
                              >
                                Start
                              </button>
                            )}
                          </div>
                          {statusObj.startedAt && (
                            <p className="timestamp">Start: {statusObj.startedAt}</p>
                          )}
                          {statusObj.endedAt && (
                            <p className="timestamp">End: {statusObj.endedAt}</p>
                          )}
                        </li>
                      );
                    })
                  )}
                </ul>
              </div>
            );
          })
        ) : operatorId.trim() ? (
          <p className="no-tasks-msg">No tasks found for Operator ID: {operatorId}</p>
        ) : null}
      </div>
    </div>
  );
}
