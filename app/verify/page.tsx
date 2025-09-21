'use client';
import { useState } from 'react';

export default function VerifyPage() {
  const [code, setCode] = useState('');
  const [result, setResult] = useState('');

  const verify = async () => {
    if (!code) return;
    setResult('Checking…');
    try {
      const res = await fetch(`/api/verify?code=${encodeURIComponent(code)}`);
      if (!res.ok) throw new Error('Network error');
      const data = await res.json();
      if (data.valid) {
        setResult(`Valid report issued on ${data.issuedAt}`);
      } else {
        setResult('Invalid or unknown report code');
      }
    } catch (err: any) {
      setResult('Error: ' + (err?.message ?? 'unknown'));
    }
  };

  return (
    <main className='container mx-auto px-6 py-16'>
      <h1 className='text-3xl font-bold mb-6'>Verify a Report</h1>
      <p className='mb-4 text-slate-700'>Enter the verification code found on your certificate to confirm its authenticity.</p>
      <div className='flex flex-col sm:flex-row items-start sm:items-center space-y-4 sm:space-y-0 sm:space-x-4'>
        <input
          type='text'
          value={code}
          onChange={(e) => setCode(e.target.value)}
          placeholder='Verification code'
          className='border p-2 rounded flex-grow'
        />
        <button onClick={verify} className='bg-brand text-white px-4 py-2 rounded'>
          Verify
        </button>
      </div>
      {result && <p className='mt-4 text-slate-700'>{result}</p>}
    </main>
  );
}
