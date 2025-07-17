import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Dashboard from "./components/Dashboard";
import ELearning from "./components/ELearning";
import Analytics from "./components/Analytics"; 

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/elearning" element={<ELearning />} />
        <Route path="/analytics" element={<Analytics />} />
      </Routes>
    </Router>
    
  );
}

export default App;
