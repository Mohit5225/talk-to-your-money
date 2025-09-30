import { type Metadata } from 'next'
import {
  ClerkProvider,
  SignedIn,
} from '@clerk/nextjs'
import { Geist, Geist_Mono } from 'next/font/google'
import './globals.css'
import Header from './components/Header'
import FloatingChatButton from './components/FloatingChatButton'

const geistSans = Geist({
  variable: '--font-geist-sans',
  subsets: ['latin'],
})

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin'],
})

export const metadata: Metadata = {
  title: 'Talk To Your Money',
  description: 'AI-powered financial insights and stock predictions',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
          {/* Use your custom Header component */}
          <Header />

          {/* Optional: keep SignIn/SignUp/UserButton if needed inside Header or separate */}
          <main className="min-h-screen bg-gradient-to-br from-blue-950 via-indigo-950 to-purple-900 text-sky-50">
            {children}
          </main>
          
          {/* Floating Chat Button */}
          <SignedIn>
            <FloatingChatButton />
          </SignedIn>
        </body>
      </html>
    </ClerkProvider>
  )
}
