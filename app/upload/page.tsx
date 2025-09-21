'use client';
import { useState } from 'react';

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<string>('');

  const handleUpload = async () => {
    if (!file) return;
    setStatus('Generating upload URL…');
    try {
      // Request a pre‑signed upload URL from the API
      const res = await fetch('/api/upload', {
        method: 'POST',
      });
      if (!res.ok) throw new Error('Failed to get upload URL');
      const { uploadUrl, key } = await res.json();
      setStatus('Uploading to secure storage…');
      // Upload directly to S3 using the pre‑signed URL
      const uploadRes = await fetch(uploadUrl, {
        method: 'PUT',
        body: file,
        headers: {
          'Content-Type': file.type || 'application/octet-stream',
        },
      });
      if (!uploadRes.ok) throw new Error('Upload failed');
      setStatus('Upload complete! Your file key is ' + key);
    } catch (err: any) {
      setStatus('Error: ' + (err?.message ?? 'unknown'));
    }
  };

  return (
    <main className='container mx-auto px-6 py-16'>
      <h1 className='text-3xl font-bold mb-6'>Submit Your Autograph</h1>
      <p className='mb-4 text-slate-700'>Upload a high‑resolution scan or photo of your autograph. We will generate a secure pre‑signed URL to encrypt and store your file in S3.</p>
      <div className='border-2 border-dashed border-gray-300 rounded-lg p-6 flex flex-col items-center'>
        <input
          type='file'
          accept='image/*,application/pdf'
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          className='mb-4'
        />
        <button
          onClick={handleUpload}
          disabled={!file}
          className='bg-brand text-white py-2 px-4 rounded disabled:opacity-50'
        >
          Upload File
        </button>
      </div>
      {status && <p className='mt-4 text-slate-700'>{status}</p>}
      <div className='mt-8'>
        <a href='/api/report' className='text-brand underline'>Download a sample report</a>
      </div>
    </main>
  );
}
