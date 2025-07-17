from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
CORS(app)

# MongoDB connection
client = MongoClient("mongodb+srv://vikasinigokulakrishnan:VeXkTMqqSkKqkhaL@cluster0.tatpwb4.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["cat_db"]
collection = db["operator_tasks"]
status_collection = db["task_status"]  # For tracking status separately

@app.route("/api/machine-data", methods=["GET"])
def get_machine_data():
    data = list(collection.find({}, {"_id": 0}))
    return jsonify(data)
@app.route("/api/update-task-status", methods=["POST"])
def update_task_status():
    data = request.json
    required_fields = {"operator_id", "machine_id", "task", "status", "timestamp"}
    
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    machine = collection.find_one({
        "operator_id": data["operator_id"],
        "machine_id": data["machine_id"]
    })

    if not machine:
        return jsonify({"error": "Machine entry not found"}), 404

    # Initialize task_logs if it doesn't exist
    task_logs = machine.get("task_logs", [])

    # Try to find the task log entry
    updated = False
    for task in task_logs:
        if task["task"] == data["task"]:
            if data["status"] == "in_progress":
                task["status"] = "in_progress"
                task["started_at"] = data["timestamp"]
            elif data["status"] == "completed":
                task["status"] = "completed"
                task["ended_at"] = data["timestamp"]
            updated = True
            break

    # If task not found in logs, add new
    if not updated:
        new_entry = {
            "task": data["task"],
            "status": data["status"],
            "started_at": data["timestamp"] if data["status"] == "in_progress" else None,
            "ended_at": data["timestamp"] if data["status"] == "completed" else None
        }
        task_logs.append(new_entry)

    # Update the document
    collection.update_one(
        {"_id": machine["_id"]},
        {"$set": {"task_logs": task_logs}}
    )

    return jsonify({"message": "Task status updated", "task_logs": task_logs})

@app.route("/api/task-status", methods=["GET"])
def get_all_status():
    tasks = list(status_collection.find({}, {"_id": 0}))
    return jsonify(tasks)


@app.route("/api/analytics", methods=["GET"])
def get_analytics():
    data = list(collection.find())

    total_machines = len(set(d["machine_id"] for d in data if "machine_id" in d))
    total_fuel = sum(float(d.get("fuel_used", 0)) for d in data)
    avg_engine_hours = (
        sum(float(d.get("engine_hours", 0)) for d in data) / len(data)
        if data else 0
    )

    completed_tasks = 0
    in_progress_tasks = 0

    for doc in data:
        if isinstance(doc.get("task_logs"), list):
            for log in doc["task_logs"]:
                if log.get("status") == "completed":
                    completed_tasks += 1
                elif log.get("status") == "in_progress":
                    in_progress_tasks += 1

    return jsonify({
        "total_machines": total_machines,
        "total_fuel": round(total_fuel, 2),
        "average_engine_hours": round(avg_engine_hours, 2),
        "completed_tasks": completed_tasks,
        "in_progress_tasks": in_progress_tasks
    })


if __name__ == "__main__":
    app.run(debug=True)
