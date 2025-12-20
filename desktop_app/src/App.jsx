import { useState, useEffect, useRef } from 'react';
import { Download, Search, Film, Activity, Terminal, Scissors } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// Components
import VideoDownloader from './components/VideoDownloader';
import ImageScraper from './components/ImageScraper';
import YTClips from './components/YTClips';
import Converter from './components/Converter';

function App() {
  const [activeTab, setActiveTab] = useState('downloader');
  const [logs, setLogs] = useState([]);
  const [progress, setProgress] = useState(null);
  const [working, setWorking] = useState(false); // Global busy state
  const ws = useRef(null);
  const logEndRef = useRef(null);

  // Connect to WebSocket
  useEffect(() => {
    connectWs();
    return () => {
      if (ws.current) ws.current.close();
    };
  }, []);

  // Auto-scroll logs
  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  const connectWs = () => {
    ws.current = new WebSocket("ws://localhost:8000/ws");

    ws.current.onopen = () => {
      addLog("System", "Connected to Backend High-Speed Link.");
    };

    ws.current.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.type === 'progress') {
        const data = msg.data;

        // Handle Global Progress
        if (data.status === 'downloading' || data.status === 'downloading_safe' || data.status === 'converting' || data.status === 'uploading') {
          setProgress(data);
          setWorking(true);
        } else if (data.status === 'completed') {
          setWorking(false);
          setProgress(null);
          addLog("Success", data.output ? `Completed: ${data.output}` : "Operation Completed Successfully.");
          new Notification("Task Complete", { body: "Your operation is finished." });
        } else if (data.status === 'error') {
          setWorking(false);
          addLog("Error", data.error);
        } else if (data.message) {
          addLog("Info", data.message);
        }
      }
    };

    ws.current.onclose = () => {
      addLog("System", "Connection lost. Reconnecting...");
      setTimeout(connectWs, 3000);
    };
  };

  const addLog = (source, message) => {
    setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] [${source}] ${message}`]);
  };

  return (
    <div className="app-container">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="brand">
          <Activity className="w-6 h-6 text-blue-500" />
          <span>TurboDL</span>
        </div>

        <nav>
          <div className={`nav-item ${activeTab === 'downloader' ? 'active' : ''}`} onClick={() => setActiveTab('downloader')}>
            <Download size={20} />
            <span>Downloader</span>
          </div>
          <div className={`nav-item ${activeTab === 'scraper' ? 'active' : ''}`} onClick={() => setActiveTab('scraper')}>
            <Search size={20} />
            <span>Scraper</span>
          </div>
          <div className={`nav-item ${activeTab === 'clips' ? 'active' : ''}`} onClick={() => setActiveTab('clips')}>
            <Scissors size={20} />
            <span>YT Clips</span>
          </div>
          <div className={`nav-item ${activeTab === 'converter' ? 'active' : ''}`} onClick={() => setActiveTab('converter')}>
            <Film size={20} />
            <span>Converter</span>
          </div>
        </nav>
      </div>

      {/* Main Content */}
      <div className="main-content">

        {/* Tab Content */}
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.2 }}
          >
            {activeTab === 'downloader' && (
              <VideoDownloader
                addLog={addLog}
                downloading={working}
                setDownloading={setWorking}
              />
            )}
            {activeTab === 'scraper' && (
              <ImageScraper
                addLog={addLog}
                working={working}
                setWorking={setWorking}
              />
            )}
            {activeTab === 'clips' && (
              <YTClips
                addLog={addLog}
                working={working}
                setWorking={setWorking}
              />
            )}
            {activeTab === 'converter' && (
              <Converter
                addLog={addLog}
                working={working}
                setWorking={setWorking}
              />
            )}
          </motion.div>
        </AnimatePresence>

        {/* Global Progress Bar */}
        <AnimatePresence>
          {progress && (
            <motion.div
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 50 }}
              className="fixed bottom-8 right-8 w-80 bg-slate-800 border border-blue-500/30 rounded-lg p-4 shadow-2xl z-50"
            >
              <div className="flex justify-between items-center mb-2">
                <span className="text-blue-400 font-semibold text-sm flex items-center gap-2">
                  <Activity size={14} className="animate-spin" />
                  {progress.status.toUpperCase().replace('_', ' ')}
                </span>
                <span className="text-gray-400 text-xs">{progress.eta ? `${progress.eta}s rem` : ''}</span>
              </div>

              <div className="w-full bg-slate-700 h-2 rounded-full overflow-hidden mb-2">
                <div
                  className="h-full bg-blue-500 transition-all duration-300"
                  style={{ width: `${progress.percent}%` }}
                />
              </div>

              <div className="flex justify-between text-xs font-mono text-gray-400">
                <span>{progress.percent ? progress.percent.toFixed(1) : 0}%</span>
                <span>{progress.speed ? (typeof progress.speed === 'number' ? progress.speed.toFixed(2) + ' MB/s' : progress.speed) : ''}</span>
              </div>
              {progress.message && <p className="text-xs text-gray-400 mt-1 truncate">{progress.message}</p>}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Logs Console */}
        <div className="terminal mt-12 border-t border-slate-700/50 pt-4">
          <h3 className="text-gray-500 text-xs font-bold uppercase mb-2 flex items-center gap-2">
            <Terminal size={12} /> System Output
          </h3>
          <div className="h-40 overflow-y-auto text-xs font-mono text-green-400/80 bg-black/40 p-4 rounded-lg">
            {logs.length === 0 && <span className="opacity-30">Waiting for commands...</span>}
            {logs.map((log, i) => (
              <div key={i}>{log}</div>
            ))}
            <div ref={logEndRef} />
          </div>
        </div>

      </div>
    </div>
  );
}

export default App;
