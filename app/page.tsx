import { ShieldCheck, FileText, Lock, Users, CheckCircle } from 'lucide-react';

export default function Home() {
  return (
    <main className='flex flex-col'>
      <section className='bg-brand text-white py-20 text-center'>
        <h1 className='text-4xl md:text-6xl font-extrabold'>Verify your autographs with confidence</h1>
        <p className='mt-6 text-xl'>Professional, trusted authentication for memorabilia collectors and dealers</p>
        <div className='mt-8 space-x-4'>
          <a href='/upload' className='inline-block bg-white text-brand py-3 px-6 rounded-md font-semibold shadow hover:bg-gray-200 transition'>
            Get Started
          </a>
          <a href='/verify' className='inline-block border border-white text-white py-3 px-6 rounded-md font-semibold hover:bg-white hover:text-brand transition'>
            Verify Report
          </a>
        </div>
      </section>
      <section className='py-12 bg-brand-light grid grid-cols-2 md:grid-cols-4 gap-6 text-center'>
        <div>
          <ShieldCheck className='w-8 h-8 text-brand mx-auto' />
          <p className='mt-2 font-medium'>Industry Experts</p>
        </div>
        <div>
          <Lock className='w-8 h-8 text-brand mx-auto' />
          <p className='mt-2 font-medium'>Secure Storage</p>
        </div>
        <div>
          <FileText className='w-8 h-8 text-brand mx-auto' />
          <p className='mt-2 font-medium'>Detailed Reports</p>
        </div>
        <div>
          <Users className='w-8 h-8 text-brand mx-auto' />
          <p className='mt-2 font-medium'>Trusted by Collectors</p>
        </div>
      </section>
      <section className='py-16 text-center'>
        <h2 className='text-3xl font-bold mb-6'>How It Works</h2>
        <div className='grid md:grid-cols-3 gap-8'>
          <div>
            <CheckCircle className='w-12 h-12 text-brand mx-auto mb-4' />
            <h3 className='text-xl font-semibold mb-2'>Submit</h3>
            <p className='text-slate-600'>Upload high‑quality scans or photos via our secure portal.</p>
          </div>
          <div>
            <ShieldCheck className='w-12 h-12 text-brand mx-auto mb-4' />
            <h3 className='text-xl font-semibold mb-2'>Analyze</h3>
            <p className='text-slate-600'>Our specialists evaluate ink, paper, and provenance with forensic tools.</p>
          </div>
          <div>
            <FileText className='w-12 h-12 text-brand mx-auto mb-4' />
            <h3 className='text-xl font-semibold mb-2'>Receive</h3>
            <p className='text-slate-600'>Get a digitally signed PDF certificate and verification code.</p>
          </div>
        </div>
      </section>
      <section className='bg-brand text-white py-16 text-center'>
        <h2 className='text-3xl font-bold mb-4'>Ready to authenticate your autograph?</h2>
        <p className='mb-6'>Join thousands of collectors and dealers who trust Autograph Verify.</p>
        <a href='/upload' className='inline-block bg-white text-brand py-3 px-8 rounded-md font-semibold shadow hover:bg-gray-200 transition'>
          Start Now
        </a>
      </section>
    </main>
  );
}
