import { useState } from 'react';
import { Search, Activity, Download } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function VideoDownloader({ addLog, wsProgress, downloading, setDownloading }) {
    const [url, setUrl] = useState('');
    const [analyzing, setAnalyzing] = useState(false);
    const [videos, setVideos] = useState([]);

    const handleAnalyze = async () => {
        if (!url) return;
        setAnalyzing(true);
        setVideos([]);
        addLog("Analysis", `Scanning URL: ${url}`);

        try {
            const res = await fetch(`http://localhost:8000/analyze`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url })
            });
            const data = await res.json();

            if (data.found && data.videos) {
                setVideos(data.videos);
                addLog("Analysis", `Found ${data.videos.length} videos.`);
            } else {
                addLog("Analysis", "No videos found.");
            }
        } catch (e) {
            addLog("Error", `Analysis failed: ${e.message}`);
        } finally {
            setAnalyzing(false);
        }
    };

    const handleDownload = async (video, formatIdx) => {
        setDownloading(true);
        addLog("Download", `Starting download: ${video.title}`);

        try {
            await fetch(`http://localhost:8000/download`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ video, format_idx: formatIdx })
            });
        } catch (e) {
            setDownloading(false);
            addLog("Error", `Download request failed: ${e.message}`);
        }
    };

    return (
        <div className="max-w-4xl mx-auto">
            <div className="mb-8">
                <h1 className="text-3xl font-bold mb-2">Any Video Downloader</h1>
                <p className="text-gray-400">Turbo-charged engine with multi-thread acceleration.</p>
            </div>

            <div className="card">
                <div className="input-group">
                    <input
                        type="text"
                        className="glass-input"
                        placeholder="Paste URL here (YouTube, Cuevana, etc)..."
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleAnalyze()}
                    />
                    <Search className="absolute right-4 top-4 text-gray-500" />
                </div>

                <button
                    className={`btn-primary ${analyzing ? 'opacity-70' : ''}`}
                    onClick={handleAnalyze}
                    disabled={analyzing}
                >
                    {analyzing ? 'Scanning...' : 'Analyze URL'}
                </button>
            </div>

            <AnimatePresence>
                {videos.map((video, idx) => (
                    <motion.div
                        key={idx}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        className="card border-l-4 border-l-blue-500"
                    >
                        <div className="flex justify-between items-start mb-4">
                            <div>
                                <h3 className="text-xl font-bold text-white mb-1">{video.title}</h3>
                                <p className="text-sm text-gray-400">Duration: {video._format_duration_hack || "Unknown"}</p>
                            </div>
                            <div className="bg-blue-900/30 text-blue-400 px-3 py-1 rounded-full text-xs font-mono">
                                {video.formats.length} Formats
                            </div>
                        </div>

                        <div className="space-y-2">
                            {video.formats.slice(0, 5).map((fmt, fIdx) => (
                                <div key={fIdx} className="flex items-center justify-between bg-slate-800/50 p-3 rounded hover:bg-slate-700 transition cursor-pointer">
                                    <div className="flex items-center gap-3">
                                        <div className="w-8 h-8 rounded bg-blue-600/20 flex items-center justify-center text-blue-400 font-bold text-xs">
                                            {fmt.ext}
                                        </div>
                                        <div>
                                            <p className="font-semibold text-sm">{fmt.quality}</p>
                                            <p className="text-xs text-gray-500">{fmt.resolution || 'Unknown Res'} • {fmt.filesize ? (fmt.filesize / (1024 * 1024)).toFixed(1) + ' MB' : 'Unknown Size'}</p>
                                        </div>
                                    </div>

                                    <button
                                        onClick={() => handleDownload(video, fIdx + 1)}
                                        className={`px-4 py-2 rounded text-sm font-semibold transition ${downloading ? 'bg-gray-700 text-gray-500 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-500 text-white'}`}
                                        disabled={downloading}
                                    >
                                        {downloading ? 'Busy' : 'Download'}
                                    </button>
                                </div>
                            ))}
                        </div>
                    </motion.div>
                ))}
            </AnimatePresence>
        </div>
    );
}
