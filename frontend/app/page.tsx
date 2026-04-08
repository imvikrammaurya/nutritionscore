'use client';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const [image, setImage] = useState<File | null>(null);
  const [preview, setPreview] = useState('');
  const [category, setCategory] = useState('chips');
  const [loading, setLoading] = useState(false);
  const [agentLog, setAgentLog] = useState<string[]>([]);
  const [error, setError] = useState('');
  const router = useRouter();

  const onFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) {
      console.log("File detected:", f.name); // Debug log
      setImage(f);
      const objectUrl = URL.createObjectURL(f);
      setPreview(objectUrl);
    }
  };

  // Cleanup memory when preview changes
  useEffect(() => {
    return () => { if (preview) URL.revokeObjectURL(preview); };
  }, [preview]);

  const submit = async () => {
    if (!image) return;
    setLoading(true); setError(''); setAgentLog([]);
    const fakeLogs = [
      'Coordinator: uploading image to GCS temp bucket...',
      'Coordinator: calling VisionAnalyzer sub-agent (Vertex AI)...',
      'VisionAnalyzer: reading label with Gemini Vision...',
      'VisionAnalyzer: extraction complete!',
      'Coordinator: calling HealthScorer sub-agent (Vertex AI)...',
      'HealthScorer: analyzing nutrition data...',
      'Coordinator: calling MCP Server — AlloyDB similarity search...',
    ];
    let i = 0;
    const iv = setInterval(() => {
      if (i < fakeLogs.length) setAgentLog(p => [...p, fakeLogs[i++]]);
      else clearInterval(iv);
    }, 700);
    try {
      const fd = new FormData();
      fd.append('file', image);
      fd.append('category', category);
      const res = await fetch(
        "https://nutritionscore-backend-400760560700.asia-south1.run.app/analyze",
        { method: 'POST', body: fd }
      );
      clearInterval(iv);
      if (!res.ok) throw new Error('failed');
      const data = await res.json();
      setAgentLog(data.agent_log || []);
      setTimeout(() => {
        localStorage.setItem('ns_result', JSON.stringify(data));
        router.push('/result');
      }, 1500);
    } catch {
      clearInterval(iv);
      setError('Analysis failed. Is the backend URL correct?');
    }
    setLoading(false);
  };

  return (
    <main className="min-h-screen bg-indigo-50 flex flex-col items-center justify-center p-6">
      <h1 className="text-4xl font-bold text-indigo-900 mb-1">NutritionScore</h1>
      <p className="text-gray-500 mb-6 text-center text-sm">
        Multi-Agent AI &middot; Vertex AI &middot; AlloyDB &middot; MCP
      </p>

      <div className="bg-white rounded-2xl shadow-md p-7 w-full max-w-md">
        <select value={category} onChange={e => setCategory(e.target.value)}
          className="w-full border rounded-xl p-3 mb-4 text-gray-700 text-sm outline-none">
          <option value="chips">Chips / Snacks</option>
          <option value="biscuits">Biscuits / Cookies</option>
          <option value="drinks">Drinks / Juices</option>
          <option value="dairy">Dairy Products</option>
          <option value="cereals">Cereals / Oats</option>
          <option value="noodles">Noodles / Instant Food</option>
        </select>

        {/* Display Area */}
        <div className="w-full h-52 border-2 border-dashed border-indigo-200 rounded-xl bg-indigo-50 mb-4 overflow-hidden flex flex-col items-center justify-center relative">
          {preview ? (
            <>
              <img src={preview} className="h-full w-full object-contain" alt="preview" />
              <button
                onClick={() => { setImage(null); setPreview(''); }}
                className="absolute top-2 right-2 bg-red-600 text-white w-6 h-6 rounded-full flex items-center justify-center text-xs shadow-lg"
              >
                ✕
              </button>
            </>
          ) : (
            <div className="grid grid-cols-2 gap-4 w-full px-4">
              {/* CAMERA LABEL */}
              <label htmlFor="camera-input" className="flex flex-col items-center justify-center p-4 bg-white border border-indigo-200 rounded-xl cursor-pointer hover:bg-indigo-100 transition shadow-sm">
                <span className="text-3xl mb-1">📷</span>
                <span className="text-xs font-bold text-indigo-700 uppercase">Camera</span>
              </label>

              {/* GALLERY LABEL */}
              <label htmlFor="gallery-input" className="flex flex-col items-center justify-center p-4 bg-white border border-indigo-200 rounded-xl cursor-pointer hover:bg-indigo-100 transition shadow-sm">
                <span className="text-3xl mb-1">🖼️</span>
                <span className="text-xs font-bold text-indigo-700 uppercase">Gallery</span>
              </label>
            </div>
          )}
        </div>

        {/* ACTUAL HIDDEN INPUTS (Always rendered at the bottom) */}
        <input id="camera-input" type="file" accept="image/*" capture="environment" onChange={onFile} className="hidden" />
        <input id="gallery-input" type="file" accept="image/*" onChange={onFile} className="hidden" />

        {agentLog.length > 0 && (
          <div className="bg-gray-900 rounded-xl p-3 mb-4 max-h-32 overflow-y-auto">
            {agentLog.map((l, i) => (
              <p key={i} className="text-green-400 text-xs font-mono leading-5">&#9658; {l}</p>
            ))}
          </div>
        )}

        {error && <p className="text-red-500 text-sm mb-3 text-center">{error}</p>}

        <button onClick={submit} disabled={!image || loading}
          className="w-full bg-indigo-700 text-white py-4 rounded-xl font-bold hover:bg-indigo-800 disabled:opacity-40 text-sm shadow-lg transition-transform active:scale-95">
          {loading ? 'Agents Analyzing...' : 'Analyze with NutritionScore AI'}
        </button>
      </div>
    </main>
  );
}