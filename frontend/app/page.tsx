'use client';
import { useState } from 'react';
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
    if (f) { setImage(f); setPreview(URL.createObjectURL(f)); }
  };

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
      setError('Analysis failed. Is the backend URL correct in your environment?');
    }
    setLoading(false);
  };

  return (
    <main className="min-h-screen bg-indigo-50 flex flex-col items-center justify-center p-6">
      <h1 className="text-4xl font-bold text-indigo-900 mb-1">NutritionScore</h1>
      <p className="text-gray-500 mb-6 text-center text-sm">
        Multi-Agent AI &middot; Vertex AI + ADK &middot; AlloyDB + pg_trgm &middot; MCP
      </p>
      <div className="bg-white rounded-2xl shadow-md p-7 w-full max-w-md">
        <select value={category} onChange={e => setCategory(e.target.value)}
          className="w-full border rounded-xl p-3 mb-4 text-gray-700 text-sm">
          <option value="chips">Chips / Snacks</option>
          <option value="biscuits">Biscuits / Cookies</option>
          <option value="drinks">Drinks / Juices</option>
          <option value="dairy">Dairy Products</option>
          <option value="cereals">Cereals / Oats</option>
          <option value="noodles">Noodles / Instant Food</option>
        </select>
        <label className="flex flex-col items-center justify-center w-full h-36 border-2 border-dashed border-indigo-300 rounded-xl cursor-pointer hover:border-indigo-500 bg-indigo-50 mb-4 overflow-hidden">
          {preview
            ? <img src={preview} className="h-full w-full object-contain" alt="preview" />
            : <div className="text-center">
              <div className="text-3xl mb-1">&#128247;</div>
              <p className="text-sm text-gray-400">Tap to upload nutrition label</p>
            </div>}
          <input type="file" accept="image/*" onChange={onFile} className="hidden" />
        </label>
        {agentLog.length > 0 && (
          <div className="bg-gray-900 rounded-xl p-3 mb-4 max-h-32 overflow-y-auto">
            {agentLog.map((l, i) => (
              <p key={i} className="text-green-400 text-xs font-mono leading-5">&#9658; {l}</p>
            ))}
          </div>
        )}
        {error && <p className="text-red-500 text-sm mb-3">{error}</p>}
        <button onClick={submit} disabled={!image || loading}
          className="w-full bg-indigo-700 text-white py-3 rounded-xl font-semibold hover:bg-indigo-800 disabled:opacity-40 text-sm">
          {loading ? 'Agents working...' : 'Analyze with NutritionScore AI'}
        </button>
      </div>
    </main>
  );
}