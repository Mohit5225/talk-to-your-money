'use client'

import Link from 'next/link'
import { SignedIn, SignedOut, SignInButton, SignUpButton } from '@clerk/nextjs'

export default function Home() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#04040d] via-[#0b0c20] to-[#151236] p-6">
      <div className="max-w-lg w-full text-center bg-[#0a0920]/85 backdrop-blur-xl shadow-[0_0_45px_rgba(123,91,255,0.22)] rounded-2xl p-10 border border-[#1f1740]">
        <h1 className="text-5xl font-extrabold bg-gradient-to-r from-[#fefbff] via-[#cdbfff] to-[var(--accent)] bg-clip-text text-transparent mb-4 drop-shadow-[0_0_18px_rgba(123,91,255,0.35)]">
          Talk To Your Money
        </h1>
        <p className="text-lg text-[#c7cbff] mb-10">
          AI-powered financial insights and stock predictions, designed for clarity and confidence.
        </p>

        <div className="flex flex-col sm:flex-row justify-center gap-4">
          <SignedOut>
            <SignInButton mode="modal">
              <button className="px-6 py-3 bg-[var(--accent)] text-[#1d0618] rounded-xl shadow-[0_0_26px_rgba(255,63,125,0.26)] hover:bg-[#ff568c] transition">
                Sign In
              </button>
            </SignInButton>
            <SignUpButton mode="modal">
              <button className="px-6 py-3 bg-[var(--accent-secondary)] text-[#1a0a2d] rounded-xl shadow-[0_0_26px_rgba(123,91,255,0.28)] hover:bg-[#8c71ff] transition">
                Sign Up
              </button>
            </SignUpButton>
          </SignedOut>

          <SignedIn>
            <Link href="/dashboard">
              <button className="px-6 py-3 bg-[#4037ff] text-white rounded-xl shadow-[0_0_26px_rgba(64,55,255,0.32)] hover:bg-[#5a52ff] transition">
                Go to Dashboard
              </button>
            </Link>
          </SignedIn>
        </div>
      </div>
    </div>
  )
}
