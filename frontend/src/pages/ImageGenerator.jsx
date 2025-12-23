import { useState } from "react";
import { axiosInstance } from "../service/axiosInstance";



export default function ImageGenerator() {
  const [prompt, setPrompt] = useState("");
  const [resolution, setResolution] = useState("512x512");
  const [photorealistic, setPhotorealistic] = useState(false);
  const [loading, setLoading] = useState(false);
  const [imageUrl, setImageUrl] = useState(null);
  const [error, setError] = useState('')


const pollJobStatus = (jobId) => {
  const interval = setInterval(async () => {
    try {
      const res = await axiosInstance.get(`/status/${jobId}`);
      const data = res.data;

      if (data.status === "completed") {
        clearInterval(interval);
        setImageUrl(data.image_url);
        setLoading(false);
      } else if (data.status === "failed") {
        clearInterval(interval);
        setLoading(false);
        setError("Image generation failed");
      }
    } catch (err) {
      clearInterval(interval);
      setLoading(false);
      setError("Polling error");
    }
  }, 2000);
};



 const handleGenerate = async (e) => {
  e.preventDefault();
  setLoading(true);
  setImageUrl(null);
  setError('');

  try {
    // 1️⃣ Generate request
    const res = await axiosInstance.post('/generate', {prompt, resolution, photorealistic})



    // 2️⃣ Start polling
    pollJobStatus(res.data.job_id);
  } catch (err) {
    setLoading(false);
    setError("Failed to start image generation");
  }
};

  return (
    <div className="min-h-screen bg-gray-950 text-white flex items-center justify-center px-4">
      <div className="w-full max-w-2xl bg-gray-900 rounded-2xl shadow-xl p-6 space-y-6">
        <h1 className="text-2xl font-semibold text-center">
          AI Image Generator
        </h1>

        {/* Form */}
        <form onSubmit={handleGenerate} className="space-y-4">
          {/* Prompt */}
          <div>
            <label className="block text-sm mb-1">Prompt</label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe your image..."
              className="w-full rounded-lg bg-gray-800 border border-gray-700 p-3 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              rows={3}
              required
            />
          </div>

          {/* Resolution */}
          <div>
            <label className="block text-sm mb-1">Resolution</label>
            <select
              value={resolution}
              onChange={(e) => setResolution(e.target.value)}
              className="w-full rounded-lg bg-gray-800 border border-gray-700 p-3"
            >
              <option value={'512x512'}>512x512</option>
              <option value={'768x768'}>768x768</option>
              <option value={'1080x1080'}>1024x1024</option>
            </select>
          </div>

          {/* Photorealistic */}
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={photorealistic}
              onChange={(e) => setPhotorealistic(e.target.checked)}
              className="accent-indigo-500"
            />
            <label className="text-sm">Photorealistic</label>
          </div>

          {/* Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 hover:bg-indigo-700 transition rounded-lg py-3 font-medium disabled:opacity-50"
          >
            Generate Image
          </button>
        </form>

        {/* Result Section */}
        <div className="mt-6">
          {loading && (
            <div className="h-64 flex items-center justify-center border border-dashed border-gray-700 rounded-lg text-gray-400 animate-pulse">
              Image generation in process...
            </div>
          )}

          {!loading && imageUrl && (
            <div className="rounded-lg overflow-hidden border border-gray-700">
              <img
                src={imageUrl}
                alt="Generated"
                className="w-full object-cover"
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
