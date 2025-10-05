'use client';

import { SignInButton, SignUpButton, SignedIn, SignedOut, UserButton } from '@clerk/nextjs';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { MessageCircle } from 'lucide-react';

export default function Header() {
  const pathname = usePathname();
  
  return (
    <header className="bg-gradient-to-r from-[#050510] via-[#0e0820] to-[#170c2c] shadow-lg border-b border-[#231544]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16 text-[var(--foreground)]">
          <div className="flex items-center">
            <Link href="/" className="font-bold text-xl text-[#f8f9ff] drop-shadow-[0_0_12px_rgba(123,91,255,0.35)]">
              Talk To Your Money
            </Link>
            <nav className="ml-10 flex space-x-8">
              <SignedIn>
                <Link 
                  href="/dashboard" 
                  className={`${
                    pathname?.startsWith('/dashboard') && !pathname?.startsWith('/dashboard/chatbot')
                      ? 'text-[var(--accent)] border-b-2 border-[var(--accent)]'
                      : 'text-[#b8beff]/70 hover:text-[#f5f6ff]'
                  } px-1 pt-1 text-sm font-semibold transition-colors`}
                >
                  Dashboard
                </Link>
                <Link 
                  href="/profile" 
                  className={`${
                    pathname?.startsWith('/profile')
                      ? 'text-[var(--accent)] border-b-2 border-[var(--accent)]'
                      : 'text-[#b8beff]/70 hover:text-[#f5f6ff]'
                  } px-1 pt-1 text-sm font-semibold transition-colors`}
                >
                  Profile
                </Link>
                <Link 
                  href="/dashboard/chatbot" 
                  className={`${
                    pathname?.startsWith('/dashboard/chatbot')
                      ? 'text-[var(--accent)] border-b-2 border-[var(--accent)]'
                      : 'text-[#b8beff]/70 hover:text-[#f5f6ff]'
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
                <button className="text-[#e7eaff] hover:text-[var(--accent)] transition-colors font-semibold">
                  Sign In
                </button>
              </SignInButton>
              <SignUpButton mode="modal">
                <button className="bg-[var(--accent)] text-[#140512] rounded-full font-semibold text-sm h-10 px-4 hover:bg-[#ff568c] transition-colors">
                  Sign Up
                </button>
              </SignUpButton>
            </SignedOut>
            <SignedIn>
              <Link href="/dashboard/chatbot">
                <button className="p-2 rounded-full bg-[var(--accent)]/20 text-[var(--accent)] hover:bg-[var(--accent)]/30 transition-colors" aria-label="Open Chatbot">
                  <MessageCircle size={20} />
                </button>
              </Link>
              <UserButton afterSignOutUrl="/" appearance={{ elements: { avatarBox: 'ring-2 ring-[var(--accent)]' } }} />
            </SignedIn>
          </div>
        </div>
      </div>
    </header>
  );
}