import { useState } from 'react';
import { sendMessageToBot } from './api/chatService';
import ChatWindow from './components/ChatWindow';
import InputBar from './components/InputBar';
import './App.css';

const formatTime = (date) => {
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  const seconds = String(date.getSeconds()).padStart(2, '0');
  return `${hours}:${minutes}:${seconds}`;
};


function App() {
  const [messages, setMessages] = useState([
    { sender: 'bot', 
      text: 'Bienvenido al chat con el libro "An Introduction to Statistical Learning with Applications in Python". En que puedo ayudarte hoy?',
      timestamp: formatTime(new Date()) }
  ]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async (inputText) => {
    if (!inputText.trim()) return;

    const userMessage = { 
      sender: 'user',
      text: inputText,
      timestamp: formatTime(new Date()) 
     };

    setMessages(prevMessages => [...prevMessages, userMessage]);
    setIsLoading(true);
    const botReply = await sendMessageToBot(inputText, messages); 
    
    const botMessage = { 
      sender: 'bot',
      text: botReply,
      timestamp: formatTime(new Date())  };

    setMessages(prevMessages => [...prevMessages, botMessage]);
    setIsLoading(false);
};


  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Conversando con</h1>
        <h2> An Introduction to Statistical Learning with Applications in Python</h2>
      </header>
      <div className="chat-container">
        <ChatWindow messages={messages} />
        {isLoading && <div className="loading-indicator">El bot está pensando...</div>}
        <InputBar onSendMessage={handleSendMessage} disabled={isLoading} />
      </div>
    </div>
  );
}

export default App;