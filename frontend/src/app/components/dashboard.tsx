import { auth } from '@clerk/nextjs/server';
import { redirect } from 'next/navigation';
import Link from 'next/link';

export default async function Dashboard() {
  const { userId } = await auth();
  
  if (!userId) {
    redirect('/auth/sign-in');
  }
  
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">Your Financial Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-2">Stock Predictions</h2>
          <p className="text-gray-600 mb-4">Get AI-powered stock price predictions</p>
          <Link href="/dashboard/predictions" className="text-blue-500 hover:underline">
            View predictions →
          </Link>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-2">Portfolio Analysis</h2>
          <p className="text-gray-600 mb-4">Analyze your investment portfolio</p>
          <Link href="/dashboard/portfolio" className="text-blue-500 hover:underline">
            View analysis →
          </Link>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-2">Profile</h2>
          <p className="text-gray-600 mb-4">Manage your account settings</p>
          <Link href="/profile" className="text-blue-500 hover:underline">
            View profile →
          </Link>
        </div>
      </div>
    </div>
  );
}

