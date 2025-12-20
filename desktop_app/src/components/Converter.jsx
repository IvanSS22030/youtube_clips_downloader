import { useState } from 'react';
import { RefreshCw, FileVideo, Settings } from 'lucide-react';

export default function Converter({ addLog, wsProgress, working, setWorking }) {
    const [filePath, setFilePath] = useState('');
    const [quality, setQuality] = useState('high');

    const handleConvert = async () => {
        if (!filePath) return;
        setWorking(true);
        addLog("Converter", `Starting conversion: ${filePath} (${quality})`);

        try {
            await fetch(`http://localhost:8000/convert`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ file_path: filePath, quality })
            });
        } catch (e) {
            setWorking(false);
            addLog("Error", `Conversion request failed: ${e.message}`);
        }
    };

    return (
        <div className="max-w-4xl mx-auto">
            <div className="mb-8">
                <h1 className="text-3xl font-bold mb-2">Format Converter</h1>
                <p className="text-gray-400">Convert MKV, AVI, and other formats to high-quality MP4.</p>
            </div>

            <div className="card">
                <label className="block text-sm font-medium text-gray-400 mb-2">Input File Path</label>
                <div className="input-group">
                    <input
                        type="text"
                        className="glass-input"
                        placeholder="C:\Users\Name\Videos\movie.mkv"
                        value={filePath}
                        onChange={(e) => setFilePath(e.target.value.replace(/"/g, ''))} // Remove quotes automatically
                    />
                    <FileVideo className="absolute right-4 top-4 text-gray-500" />
                </div>

                <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-400 mb-2">Quality Preset</label>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                        {['high', 'medium', 'fast', 'ultrafast'].map((q) => (
                            <div
                                key={q}
                                onClick={() => setQuality(q)}
                                className={`p-3 rounded-lg border cursor-pointer transition text-center capitalize ${quality === q ? 'bg-blue-600 border-blue-500 text-white' : 'bg-slate-800 border-slate-700 text-gray-400 hover:bg-slate-700'}`}
                            >
                                {q}
                            </div>
                        ))}
                    </div>
                </div>

                <button
                    className={`btn-primary ${working ? 'opacity-70' : ''}`}
                    onClick={handleConvert}
                    disabled={working}
                >
                    {working ? 'Converting...' : 'Start Conversion'}
                </button>
            </div>
        </div>
    );
}
