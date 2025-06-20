import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import FeaturesSection from './components/FeaturesSection';
import MarketAgent from './components/MarketAgent';

function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-tr from-[#0f172a] to-[#1e293b] text-white px-6 py-12">
      <div className="max-w-5xl mx-auto text-center space-y-8">
        <div className="inline-block bg-[#1e3a8a] text-sm px-4 py-1 rounded-full tracking-wide shadow">
          🚀 AI-Powered Market Intelligence
        </div>

        <h1 className="text-4xl md:text-6xl font-extrabold leading-tight tracking-tight">
          Transform <span className="text-cyan-400">Market Data</span><br /> Into Strategic Intelligence
        </h1>

        <p className="text-gray-300 max-w-2xl mx-auto text-lg">
          Use AI to analyze trends, predict opportunities, and empower decision-making with precision and speed.
        </p>

        <div className="flex flex-col sm:flex-row justify-center gap-4">
          <button
            onClick={() => navigate('/chat')}
            className="bg-cyan-500 hover:bg-cyan-400 px-6 py-3 rounded-xl text-white font-semibold shadow-lg transition"
          >
            Get Started Free
          </button>
          <button className="bg-white text-blue-700 px-6 py-3 rounded-xl font-semibold shadow">
            Watch Demo
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 text-gray-300 mt-10">
          <div>
            <p className="text-3xl font-bold text-white">99.9%</p>
            <p>Accuracy Rate</p>
          </div>
          <div>
            <p className="text-3xl font-bold text-white">10M+</p>
            <p>Data Points Analyzed</p>
          </div>
          <div>
            <p className="text-3xl font-bold text-white">24/7</p>
            <p>Real-time Monitoring</p>
          </div>
        </div>
      </div>

      <FeaturesSection />
    </div>
  );
}

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/chat" element={<MarketAgent />} />
      </Routes>
    </Router>
  );
}
