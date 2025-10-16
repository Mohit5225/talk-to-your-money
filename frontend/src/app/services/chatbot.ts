// services/chatbot.ts
export interface ChatMessage {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

export async function sendMessage(message: string, token?: string): Promise<ChatMessage> {
  try {
    // build headers, including Clerk JWT if provided
    const headers: Record<string,string> = {
      'Content-Type': 'application/json'
    };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const res = await fetch('http://localhost:8000/chat', {
      method: 'POST',
      headers,
      credentials: 'include',
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