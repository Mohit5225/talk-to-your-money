'use client'

import { useState, useRef, useEffect } from 'react'
import { useRouter } from 'next/navigation'
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
    <div className="flex flex-col h-[calc(100vh-64px)] bg-gradient-to-br from-blue-950 via-indigo-950 to-purple-900 text-sky-100">
      <div className="bg-gradient-to-r from-indigo-800 via-blue-700 to-cyan-600 p-4 shadow-lg border-b border-cyan-400/60">
        <h1 className="text-xl font-semibold text-white drop-shadow">Talk to Your Money Assistant</h1>
        <p className="text-cyan-100 text-sm">Ask questions about finances, investments, or get stock predictions</p>
      </div>
      
      <div className={`flex-grow overflow-y-auto p-4 ${styles.chatContainer}`}>
        <div className="max-w-3xl mx-auto">
          {messages.map((message) => (
            <div 
              key={message.id} 
              className={`mb-4 ${message.sender === 'user' ? 'flex justify-end' : 'flex justify-start'} ${styles.messageIn}`}
            >
              {message.sender === 'bot' && (
                <div className="flex-shrink-0 h-8 w-8 rounded-full bg-cyan-500/30 flex items-center justify-center mr-2 border border-cyan-300/60">
                  <Bot size={18} className="text-cyan-100" />
                </div>
              )}
              
              <div 
                className={`p-3 rounded-lg max-w-[80%] ${styles.messageIn} ${
                  message.sender === 'user' 
                    ? 'bg-amber-400 text-blue-950 rounded-br-none' 
                    : 'bg-indigo-900/80 text-sky-100 shadow-xl border border-indigo-600/60 rounded-bl-none'
                }`}
              >
                <p className="whitespace-pre-wrap">{message.text}</p>
                <div 
                  className={`text-xs mt-1 flex items-center ${
                    message.sender === 'user' ? 'text-blue-900/80' : 'text-cyan-200'
                  }`}
                >
                  {message.timestamp.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                </div>
              </div>
              
              {message.sender === 'user' && (
                <div className="flex-shrink-0 h-8 w-8 rounded-full bg-amber-400 flex items-center justify-center ml-2 border border-amber-200/80">
                  <User size={18} className="text-blue-950" />
                </div>
              )}
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start mb-4">
              <div className="flex-shrink-0 h-8 w-8 rounded-full bg-cyan-500/30 flex items-center justify-center mr-2 border border-cyan-300/60">
                <Bot size={18} className="text-cyan-100" />
              </div>
              <div className="bg-indigo-900/80 border border-indigo-600/60 p-3 rounded-lg shadow-xl rounded-bl-none">
                <div className="flex space-x-2">
                  <div className={`h-2 w-2 bg-blue-400 rounded-full ${styles.typingDot}`}></div>
                  <div className={`h-2 w-2 bg-blue-400 rounded-full ${styles.typingDot}`}></div>
                  <div className={`h-2 w-2 bg-blue-400 rounded-full ${styles.typingDot}`}></div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>
      
      <div className="p-4 border-t border-indigo-700 bg-indigo-950/90">
        <form onSubmit={handleSendMessage} className="max-w-3xl mx-auto">
          <div className="flex items-center gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question about your finances..."
              className="flex-grow border border-cyan-500/60 rounded-full px-4 py-3 bg-indigo-900/60 text-sky-100 placeholder-sky-300 focus:outline-none focus:ring-2 focus:ring-amber-400 shadow-lg"
              disabled={isLoading}
              onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSendMessage(e)}
              autoFocus
            />
            <button 
              type="submit" 
              className="bg-amber-400 text-blue-950 p-3 rounded-full hover:bg-amber-300 focus:outline-none focus:ring-2 focus:ring-amber-200 disabled:bg-amber-200 shadow-lg transition-colors font-semibold"
              disabled={isLoading || !input.trim()}
              aria-label="Send message"
            >
              <Send size={20} />
            </button>
          </div>
          <p className="text-xs text-cyan-200 mt-2 text-center">Ask about finances, investments, or get stock predictions</p>
        </form>
      </div>
    </div>
  )
}