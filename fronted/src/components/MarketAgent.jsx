import { useState } from 'react';
import axios from 'axios';

const MarketAgent = () => {
  const [input, setInput] = useState('');
  const [chatLog, setChatLog] = useState([
    {
      role: 'agent',
      message:
        'Welcome to your Market Intelligence Agent! I can help you analyze market trends, predict opportunities, and provide data-driven insights.',
    },
  ]);
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;
    setChatLog([...chatLog, { role: 'user', message: input }]);
    setLoading(true);

    let reply = '[!] Failed to fetch response.';

    try {
      if (input.toLowerCase().includes('youtube')) {
        const res = await axios.get(`http://localhost:8000/analyze-youtube/`, {
          params: {
            video_url_or_query: input,
            question: input,
          },
        });
        reply = res.data.response;
      } else if (input.toLowerCase().includes('http')) {
        const res = await axios.get(`http://localhost:8000/analyze-website/`, {
          params: {
            url: input,
            question: input,
          },
        });
        reply = res.data.response;
      } else {
        reply = "Please enter a valid YouTube query or website URL.";
      }
    } catch (err) {
      reply = '[!] Error fetching data. Backend not reachable?';
    }

    setChatLog((prev) => [...prev, { role: 'agent', message: reply }]);
    setInput('');
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0f172a] to-[#1e293b] text-white p-6">
      <div className="flex items-center justify-between mb-6">
        <a href="/" className="text-blue-400 hover:underline text-sm">&larr; Back to Home</a>
        <h2 className="text-xl font-bold">📊 Market Intelligence Agent</h2>
        <div className="text-green-400 text-sm bg-green-800 px-3 py-1 rounded-full">Online</div>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        {/* Sidebar */}
        <aside className="space-y-6">
          <div className="bg-[#1e293b] rounded-xl p-5 shadow">
            <h3 className="text-lg font-semibold mb-3">Quick Actions</h3>
            <ul className="space-y-2 text-sm text-gray-300">
              <li>📈 Market Trends</li>
              <li>📊 Data Analysis</li>
              <li>🧠 AI Insights</li>
            </ul>
          </div>
          <div className="bg-[#1e293b] rounded-xl p-5 shadow">
            <h3 className="text-lg font-semibold mb-3">Market Status</h3>
            <ul className="text-sm text-gray-300 space-y-1">
              <li>Markets: <span className="text-green-400">Open</span></li>
              <li>Data Feed: <span className="text-blue-400">Live</span></li>
              <li>AI Engine: <span className="text-purple-400">Active</span></li>
            </ul>
          </div>
        </aside>

        {/* Chat Box */}
        <main className="col-span-2 flex flex-col justify-between bg-[#1f2a3e] rounded-2xl p-6 shadow h-[600px]">
          <div className="space-y-4 overflow-y-auto pr-2">
            {chatLog.map((chat, i) => (
              <div key={i} className="flex items-start gap-3">
                <div className={`rounded-full h-8 w-8 flex items-center justify-center text-white text-sm ${chat.role === 'agent' ? 'bg-blue-500' : 'bg-cyan-500'}`}>
                  {chat.role === 'agent' ? '🤖' : '🧑'}
                </div>
                <div className="bg-[#2a395a] px-4 py-3 rounded-xl text-sm max-w-lg whitespace-pre-wrap">
                  {chat.message}
                </div>
              </div>
            ))}
            {loading && <p className="text-sm text-gray-400">Analyzing...</p>}
          </div>

          <div className="mt-6 flex border-t border-gray-600 pt-4">
            <input
              className="flex-grow bg-[#2a395a] text-white px-4 py-3 rounded-l-lg placeholder-gray-400 focus:outline-none"
              placeholder="Ask about market trends, website or YouTube analysis..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            />
            <button
              onClick={handleSend}
              className="bg-cyan-500 hover:bg-cyan-400 px-6 py-3 rounded-r-lg text-white"
              disabled={loading}
            >
              ➤
            </button>
          </div>
        </main>
      </div>
    </div>
  );
};

export default MarketAgent;
