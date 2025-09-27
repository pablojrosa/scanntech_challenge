import React from 'react';
import './Message.css';

const Message = ({ sender, text, timestamp }) => {
  const messageClass = sender === 'user' ? 'user-message' : 'bot-message';

  return (
    <div className={`message-container ${messageClass}`}>
      <div className="message-bubble">
        <p className="message-text">{text}</p>
        <span className="message-timestamp">{timestamp}</span>
      </div>
    </div>
  );
};


export default Message;