'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User } from 'lucide-react'
import styles from './chatbot.module.css'
import { sendMessage, ChatMessage } from '@/app/services/chatbot'

// Using ChatMessage type from our service

export default function ChatbotPage() {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      text: 'Hi there! How can I help you with your finances today?',
      sender: 'bot',
      timestamp: new Date()
    }
  ])
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to the bottom of chat when messages change
  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }
  
  const formatTime = (timestamp: Date) => {
    return new Date(timestamp).toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit'
    });
  }

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!input.trim()) return
    
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      text: input,
      sender: 'user',
      timestamp: new Date()
    }
    
    // Add user message to chat
    setMessages(prev => [...prev, userMessage])
    const userInput = input.trim()
    setInput('')
    setIsLoading(true)
    
    // Send request to backend
    try {
      // Call our service function
      const botResponse = await sendMessage(userInput)
      setMessages(prev => [...prev, botResponse])
    } catch (error) {
      console.error('Error sending message:', error)
      
      // Add error message
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        text: 'Sorry, I encountered an error. Please try again later.',
        sender: 'bot',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-64px)] bg-gradient-to-br from-[#04040d] via-[#0b0c20] to-[#151237] text-[var(--foreground)]">
      <div className="bg-gradient-to-r from-[#090b1d] via-[#12153a] to-[#1c1e4f] p-4 shadow-lg border-b border-[var(--accent-secondary)]/30">
        <h1 className="text-xl font-semibold text-[#f6f5ff] drop-shadow-[0_0_16px_rgba(123,91,255,0.28)]">Talk to Your Money Assistant</h1>
        <p className="text-[#c8cdfd] text-sm">Ask questions about finances, investments, or get stock predictions</p>
      </div>
      
      <div className={`flex-grow overflow-y-auto p-4 ${styles.chatContainer}`}>
        <div className="max-w-3xl mx-auto">
          {messages.map((message) => (
            <div 
              key={message.id} 
              className={`mb-4 ${message.sender === 'user' ? 'flex justify-end' : 'flex justify-start'} ${styles.messageIn}`}
            >
              {message.sender === 'bot' && (
                <div className="flex-shrink-0 h-8 w-8 rounded-full bg-[var(--accent-secondary)]/20 flex items-center justify-center mr-2 border border-[var(--accent-secondary)]/35">
                  <Bot size={18} className="text-[var(--accent-secondary)]" />
                </div>
              )}
              
              <div 
                className={`p-3 rounded-lg max-w-[80%] ${styles.messageIn} ${
                  message.sender === 'user' 
                    ? 'bg-[var(--accent)] text-[#1c0619] rounded-br-none' 
                    : 'bg-[#101432]/80 text-[var(--foreground)] shadow-xl border border-[var(--accent-secondary)]/25 rounded-bl-none'
                }`}
              >
                <p className="whitespace-pre-wrap">{message.text}</p>
                <div 
                  className={`text-xs mt-1 flex items-center ${
                    message.sender === 'user' ? 'text-[#37122c]' : 'text-[var(--accent-secondary)]'
                  }`}
                >
                   {formatTime(message.timestamp)}
                </div>
              </div>
              
              {message.sender === 'user' && (
                <div className="flex-shrink-0 h-8 w-8 rounded-full bg-[var(--accent)] flex items-center justify-center ml-2 border border-[#ff5c8f]/60">
                  <User size={18} className="text-[#190612]" />
                </div>
              )}
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start mb-4">
              <div className="flex-shrink-0 h-8 w-8 rounded-full bg-[var(--accent-secondary)]/20 flex items-center justify-center mr-2 border border-[var(--accent-secondary)]/35">
                <Bot size={18} className="text-[var(--accent-secondary)]" />
              </div>
              <div className="bg-[#101432]/80 border border-[var(--accent-secondary)]/25 p-3 rounded-lg shadow-xl rounded-bl-none">
                <div className="flex space-x-2">
                  <div className={`h-2 w-2 bg-[var(--accent)] rounded-full ${styles.typingDot}`}></div>
                  <div className={`h-2 w-2 bg-[var(--accent)] rounded-full ${styles.typingDot}`}></div>
                  <div className={`h-2 w-2 bg-[var(--accent)] rounded-full ${styles.typingDot}`}></div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>
      
      <div className="p-4 border-t border-[#232046] bg-[#090b20]/90">
        <form onSubmit={handleSendMessage} className="max-w-3xl mx-auto">
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question about your finances..."
              className="flex-grow border border-[var(--accent-secondary)]/35 rounded-full px-4 py-3 bg-[#111533]/70 text-[var(--foreground)] placeholder-[#c8cdfd]/80 focus:outline-none focus:ring-2 focus:ring-[var(--accent-secondary)] shadow-[0_0_22px_rgba(64,55,255,0.24)]"
              disabled={isLoading}
              onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSendMessage(e)}
              autoFocus
            />
            <button 
              type="submit" 
              className="bg-[var(--accent)] text-[#1d0618] p-3 rounded-full hover:bg-[#ff568c] focus:outline-none focus:ring-2 focus:ring-[var(--accent-secondary)]/70 disabled:bg-[var(--accent)]/50 shadow-[0_0_24px_rgba(255,63,125,0.28)] transition-colors font-semibold"
              disabled={isLoading || !input.trim()}
              aria-label="Send message"
            >
              <Send size={20} />
            </button>
          </div>
          <p className="text-xs text-[#c8cdfd] mt-2 text-center">Ask about finances, investments, or get stock predictions</p>
        </form>
      </div>
    </div>
  )
}