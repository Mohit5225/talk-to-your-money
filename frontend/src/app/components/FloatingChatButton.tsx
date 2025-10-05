'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { MessageCircle } from 'lucide-react';
import { usePathname } from 'next/navigation';

export default function FloatingChatButton() {
  const [isVisible, setIsVisible] = useState(true);
  const pathname = usePathname();
  
  // Hide button when on the chatbot page
  useEffect(() => {
    if (pathname?.startsWith('/dashboard/chatbot')) {
      setIsVisible(false);
    } else {
      setIsVisible(true);
    }
  }, [pathname]);
  
  if (!isVisible) return null;
  
  return (
    <div className="fixed bottom-6 right-6 z-50">
      <Link href="/dashboard/chatbot">
        <button 
          className="bg-[var(--accent)] text-[#1a0515] p-4 rounded-full shadow-[0_0_22px_rgba(255,63,125,0.32)] hover:bg-[#ff568c] transition-transform hover:scale-105 flex items-center gap-2"
          aria-label="Open chatbot"
        >
          <MessageCircle size={24} />
          <span className="font-medium">Chat with AI</span>
        </button>
      </Link>
    </div>
  );
}