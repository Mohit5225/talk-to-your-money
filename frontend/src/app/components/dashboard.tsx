import { auth } from '@clerk/nextjs/server';
import { redirect } from 'next/navigation';
import Link from 'next/link';

export default async function Dashboard() {
  const { userId } = await auth();
  
  if (!userId) {
    redirect('/auth/sign-in');
  }
  
  return (
    <div className="p-8 text-[var(--foreground)]">
      <h1 className="text-3xl font-bold mb-6 text-[#f2eeff] drop-shadow-[0_0_16px_rgba(123,91,255,0.28)]">Your Financial Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-gradient-to-br from-[#0d0b1f]/80 to-[#141033]/80 border border-[#211b44] p-6 rounded-xl shadow-[0_0_24px_rgba(64,55,255,0.2)] backdrop-blur">
          <h2 className="text-xl font-semibold mb-2 text-[var(--accent-secondary)]">Stock Predictions</h2>
          <p className="text-[#c8cdfd] mb-4">Get AI-powered stock price predictions</p>
          <Link href="/dashboard/predictions" className="text-[var(--accent)] font-semibold hover:text-[#ff5c8f] transition-colors">
            View predictions →
          </Link>
        </div>
        
        <div className="bg-gradient-to-br from-[#0d0b1f]/80 to-[#141033]/80 border border-[#211b44] p-6 rounded-xl shadow-[0_0_24px_rgba(64,55,255,0.2)] backdrop-blur">
          <h2 className="text-xl font-semibold mb-2 text-[var(--accent-secondary)]">Portfolio Analysis</h2>
          <p className="text-[#c8cdfd] mb-4">Analyze your investment portfolio</p>
          <Link href="/dashboard/portfolio" className="text-[var(--accent)] font-semibold hover:text-[#ff5c8f] transition-colors">
            View analysis →
          </Link>
        </div>
        
        <div className="bg-gradient-to-br from-[#0d0b1f]/80 to-[#141033]/80 border border-[#211b44] p-6 rounded-xl shadow-[0_0_24px_rgba(64,55,255,0.2)] backdrop-blur">
          <h2 className="text-xl font-semibold mb-2 text-[var(--accent-secondary)]">Profile</h2>
          <p className="text-[#c8cdfd] mb-4">Manage your account settings</p>
          <Link href="/profile" className="text-[var(--accent)] font-semibold hover:text-[#ff5c8f] transition-colors">
            View profile →
          </Link>
        </div>
      </div>
    </div>
  );
}

