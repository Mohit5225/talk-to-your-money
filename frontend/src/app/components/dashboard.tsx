import { auth } from '@clerk/nextjs/server';
import { redirect } from 'next/navigation';
import Link from 'next/link';

export default async function Dashboard() {
  const { userId } = await auth();
  
  if (!userId) {
    redirect('/auth/sign-in');
  }
  
  return (
    <div className="p-8 text-sky-100">
      <h1 className="text-3xl font-bold mb-6 text-amber-200 drop-shadow">Your Financial Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-indigo-900/70 border border-indigo-700 p-6 rounded-xl shadow-lg backdrop-blur">
          <h2 className="text-xl font-semibold mb-2 text-amber-200">Stock Predictions</h2>
          <p className="text-sky-100 mb-4">Get AI-powered stock price predictions</p>
          <Link href="/dashboard/predictions" className="text-cyan-300 font-semibold hover:text-amber-200 transition-colors">
            View predictions →
          </Link>
        </div>
        
        <div className="bg-indigo-900/70 border border-indigo-700 p-6 rounded-xl shadow-lg backdrop-blur">
          <h2 className="text-xl font-semibold mb-2 text-amber-200">Portfolio Analysis</h2>
          <p className="text-sky-100 mb-4">Analyze your investment portfolio</p>
          <Link href="/dashboard/portfolio" className="text-cyan-300 font-semibold hover:text-amber-200 transition-colors">
            View analysis →
          </Link>
        </div>
        
        <div className="bg-indigo-900/70 border border-indigo-700 p-6 rounded-xl shadow-lg backdrop-blur">
          <h2 className="text-xl font-semibold mb-2 text-amber-200">Profile</h2>
          <p className="text-sky-100 mb-4">Manage your account settings</p>
          <Link href="/profile" className="text-cyan-300 font-semibold hover:text-amber-200 transition-colors">
            View profile →
          </Link>
        </div>
      </div>
    </div>
  );
}

