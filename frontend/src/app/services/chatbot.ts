// services/chatbot.ts
export interface ChatMessage {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

export async function sendMessage(message: string): Promise<ChatMessage> {
  try {
    // Call backend chat API. The backend router is exposed under /api/chat
    const res = await fetch('http://localhost:8000/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      // include credentials so Clerk session cookie is sent
      credentials: 'include',
      // send the user's message in a simple payload
      body: JSON.stringify({ message })
    });

    if (!res.ok) {
      const text = await res.text();
      console.error('Chat API error:', res.status, text);
      throw new Error('Chat API returned ' + res.status);
    }

    // Parse JSON safely
    let data: any = null;
    try {
      data = await res.json();
    } catch (e) {
      const text = await res.text();
      console.warn('Chat API returned non-JSON response:', text);
      data = { content: text };
    }

    // Expecting backend to return { type: 'text', content: '...' } or similar
    const botText = (data && data.content) ? data.content : (data.message || JSON.stringify(data));

    return {
      id: Date.now().toString(),
      text: botText,
      sender: 'bot',
      timestamp: new Date()
    };
  } catch (error) {
    console.error('Error in chat service:', error);
    throw new Error('Failed to send message');
  }
}