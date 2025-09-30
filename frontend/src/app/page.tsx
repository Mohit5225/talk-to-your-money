'use client'

import Link from 'next/link'
import { SignedIn, SignedOut, SignInButton, SignUpButton } from '@clerk/nextjs'

export default function Home() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-950 via-indigo-900 to-purple-900 p-6">
      <div className="max-w-lg w-full text-center bg-indigo-900/80 backdrop-blur-md shadow-2xl rounded-2xl p-10 border border-indigo-700">
        <h1 className="text-5xl font-extrabold bg-gradient-to-r from-amber-300 via-rose-300 to-cyan-200 bg-clip-text text-transparent mb-4">
          Talk To Your Money
        </h1>
        <p className="text-lg text-sky-100 mb-10">
          AI-powered financial insights and stock predictions, designed for clarity and confidence.
        </p>

        <div className="flex flex-col sm:flex-row justify-center gap-4">
          <SignedOut>
            <SignInButton mode="modal">
              <button className="px-6 py-3 bg-blue-600 text-white rounded-xl shadow-md hover:shadow-lg hover:bg-blue-700 transition">
                Sign In
              </button>
            </SignInButton>
            <SignUpButton mode="modal">
              <button className="px-6 py-3 bg-green-600 text-white rounded-xl shadow-md hover:shadow-lg hover:bg-green-700 transition">
                Sign Up
              </button>
            </SignUpButton>
          </SignedOut>

          <SignedIn>
            <Link href="/dashboard">
              <button className="px-6 py-3 bg-indigo-600 text-white rounded-xl shadow-md hover:shadow-lg hover:bg-indigo-700 transition">
                Go to Dashboard
              </button>
            </Link>
          </SignedIn>
        </div>
      </div>
    </div>
  )
}
