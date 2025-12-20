import { useState } from 'react';
import { Search, Image as ImageIcon, Code, Layers } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function ImageScraper({ addLog, wsProgress, working, setWorking }) {
    const [url, setUrl] = useState('');
    const [mode, setMode] = useState('images'); // 'images' or 'scripts'
    const [results, setResults] = useState([]);

    const handleScrape = async () => {
        if (!url) return;
        setWorking(true);
        setResults([]);

        const endpoint = mode === 'images' ? 'scrape-images' : 'scrape-scripts';
        const label = mode === 'images' ? 'Images' : 'Scripts';

        addLog("Scraper", `Starting ${label} scrape for: ${url}`);

        try {
            await fetch(`http://localhost:8000/${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url })
            });
            // The actual results come via WebSocket 'completed' event for now, 
            // or we can implement a list return. 
            // For this v1, the backend sends "files" in the "completed" WS message.
        } catch (e) {
            setWorking(false);
            addLog("Error", `Scrape failed: ${e.message}`);
        }
    };

    // Listen for completion to show results? 
    // currently App.jsx handles WS messages globally. 
    // We might want to pass a "lastResult" prop or similar if we want to show them here.
    // For now, let's rely on the logs and the file system.
    // But to make it "Premium", we should ideally show the downloaded images.

    return (
        <div className="max-w-4xl mx-auto">
            <div className="mb-8">
                <h1 className="text-3xl font-bold mb-2">Asset Scraper</h1>
                <p className="text-gray-400">Extract images, scripts, and stylesheets from any website.</p>
            </div>

            <div className="card">
                <div className="flex gap-4 mb-4">
                    <button
                        onClick={() => setMode('images')}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg transition ${mode === 'images' ? 'bg-blue-600 text-white' : 'bg-slate-700 text-gray-400 hover:bg-slate-600'}`}
                    >
                        <ImageIcon size={18} /> Images
                    </button>
                    <button
                        onClick={() => setMode('scripts')}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg transition ${mode === 'scripts' ? 'bg-blue-600 text-white' : 'bg-slate-700 text-gray-400 hover:bg-slate-600'}`}
                    >
                        <Code size={18} /> Scripts
                    </button>
                </div>

                <div className="input-group">
                    <input
                        type="text"
                        className="glass-input"
                        placeholder={`Paste URL to scrape ${mode}...`}
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                    />
                </div>

                <button
                    className={`btn-primary ${working ? 'opacity-70' : ''}`}
                    onClick={handleScrape}
                    disabled={working}
                >
                    {working ? 'Scraping...' : `Scrape ${mode === 'images' ? 'Images' : 'Scripts'}`}
                </button>
            </div>

            {/* Results placeholder - In a real app we would display the images here */}
            <div className="p-4 rounded-lg bg-blue-900/20 border border-blue-500/20 text-center text-blue-300">
                <Layers className="mx-auto w-12 h-12 mb-2 opacity-50" />
                <p>Downloaded assets will appear in your <code>downloads/</code> folder.</p>
            </div>

        </div>
    );
}
