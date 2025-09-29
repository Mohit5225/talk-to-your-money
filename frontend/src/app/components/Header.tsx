'use client';

import { SignInButton, SignUpButton, SignedIn, SignedOut, UserButton } from '@clerk/nextjs';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Header() {
  const pathname = usePathname();
  
  return (
    <header className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex">
            <Link href="/" className="font-bold text-xl text-blue-600">
              Talk To Your Money
            </Link>
            <nav className="ml-10 flex space-x-8">
              <SignedIn>
                <Link 
                  href="/dashboard" 
                  className={`${
                    pathname?.startsWith('/dashboard') ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500'
                  } px-1 pt-1 text-sm font-medium`}
                >
                  Dashboard
                </Link>
                <Link 
                  href="/profile" 
                  className={`${
                    pathname?.startsWith('/profile') ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500'
                  } px-1 pt-1 text-sm font-medium`}
                >
                  Profile
                </Link>
              </SignedIn>
            </nav>
          </div>
          
          <div className="flex items-center gap-4">
            <SignedOut>
              <SignInButton mode="modal">
                <button className="text-gray-600 hover:text-gray-900">
                  Sign In
                </button>
              </SignInButton>
              <SignUpButton mode="modal">
                <button className="bg-blue-600 text-white rounded-full font-medium text-sm h-10 px-4 cursor-pointer">
                  Sign Up
                </button>
              </SignUpButton>
            </SignedOut>
            <SignedIn>
              <UserButton afterSignOutUrl="/" />
            </SignedIn>
          </div>
        </div>
      </div>
    </header>
  );
}