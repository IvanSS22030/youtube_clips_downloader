import { useState } from 'react';
import { Scissors, Youtube } from 'lucide-react';

export default function YTClips({ addLog, wsProgress, working, setWorking }) {
    const [url, setUrl] = useState('');

    const handleDownload = async () => {
        if (!url) return;
        setWorking(true);
        addLog("Clips", `Starting clip download: ${url}`);

        try {
            await fetch(`http://localhost:8000/download-clip`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url })
            });
        } catch (e) {
            setWorking(false);
            addLog("Error", `Clip request failed: ${e.message}`);
        }
    };

    return (
        <div className="max-w-4xl mx-auto">
            <div className="mb-8">
                <h1 className="text-3xl font-bold mb-2">YouTube Clips</h1>
                <p className="text-gray-400">Download specific segments from YouTube videos.</p>
            </div>

            <div className="card">
                <div className="flex items-start gap-4 mb-6 p-4 bg-yellow-900/20 border border-yellow-500/20 rounded-lg text-yellow-200 text-sm">
                    <Scissors className="shrink-0 mt-1" />
                    <div>
                        <p className="font-bold mb-1">How to get a Clip URL:</p>
                        <ol className="list-decimal list-inside space-y-1 opacity-80">
                            <li>Go to a YouTube video</li>
                            <li>Click the "Clip" button (scissors icon)</li>
                            <li>Select your start/end times</li>
                            <li>Share -&gt; Copy Link</li>
                        </ol>
                    </div>
                </div>

                <div className="input-group">
                    <input
                        type="text"
                        className="glass-input"
                        placeholder="Paste YouTube Clip URL here..."
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                    />
                    <Youtube className="absolute right-4 top-4 text-red-500" />
                </div>

                <button
                    className={`btn-primary ${working ? 'opacity-70' : ''}`}
                    onClick={handleDownload}
                    disabled={working}
                >
                    {working ? 'Downloading Clip...' : 'Download Clip'}
                </button>
            </div>
        </div>
    );
}
