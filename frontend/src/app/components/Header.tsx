'use client';

import { SignInButton, SignUpButton, SignedIn, SignedOut, UserButton } from '@clerk/nextjs';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { MessageCircle } from 'lucide-react';

export default function Header() {
  const pathname = usePathname();
  
  return (
    <header className="bg-gradient-to-r from-blue-950 via-indigo-900 to-purple-900 shadow-lg border-b border-indigo-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16 text-sky-100">
          <div className="flex items-center">
            <Link href="/" className="font-bold text-xl text-amber-300 drop-shadow">
              Talk To Your Money
            </Link>
            <nav className="ml-10 flex space-x-8">
              <SignedIn>
                <Link 
                  href="/dashboard" 
                  className={`${
                    pathname?.startsWith('/dashboard') && !pathname?.startsWith('/dashboard/chatbot')
                      ? 'text-amber-300 border-b-2 border-amber-300'
                      : 'text-cyan-200/80 hover:text-cyan-100'
                  } px-1 pt-1 text-sm font-semibold transition-colors`}
                >
                  Dashboard
                </Link>
                <Link 
                  href="/profile" 
                  className={`${
                    pathname?.startsWith('/profile')
                      ? 'text-amber-300 border-b-2 border-amber-300'
                      : 'text-cyan-200/80 hover:text-cyan-100'
                  } px-1 pt-1 text-sm font-semibold transition-colors`}
                >
                  Profile
                </Link>
                <Link 
                  href="/dashboard/chatbot" 
                  className={`${
                    pathname?.startsWith('/dashboard/chatbot')
                      ? 'text-amber-300 border-b-2 border-amber-300'
                      : 'text-cyan-200/80 hover:text-cyan-100'
                  } px-1 pt-1 text-sm font-semibold flex items-center gap-1 transition-colors`}
                >
                  <MessageCircle size={16} />
                  Chatbot
                </Link>
              </SignedIn>
            </nav>
          </div>

          <div className="flex items-center gap-4">
            <SignedOut>
              <SignInButton mode="modal">
                <button className="text-cyan-100 hover:text-amber-200 transition-colors font-semibold">
                  Sign In
                </button>
              </SignInButton>
              <SignUpButton mode="modal">
                <button className="bg-amber-400 text-blue-950 rounded-full font-semibold text-sm h-10 px-4 hover:bg-amber-300 transition-colors">
                  Sign Up
                </button>
              </SignUpButton>
            </SignedOut>
            <SignedIn>
              <Link href="/dashboard/chatbot">
                <button className="p-2 rounded-full bg-cyan-500/20 text-cyan-100 hover:bg-cyan-500/30 transition-colors" aria-label="Open Chatbot">
                  <MessageCircle size={20} />
                </button>
              </Link>
              <UserButton afterSignOutUrl="/" appearance={{ elements: { avatarBox: 'ring-2 ring-amber-300' } }} />
            </SignedIn>
          </div>
        </div>
      </div>
    </header>
  );
}