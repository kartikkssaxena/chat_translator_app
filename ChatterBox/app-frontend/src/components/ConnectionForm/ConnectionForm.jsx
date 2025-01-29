import React, { useState } from 'react';
import './ConnectionForm.css';

const LANGUAGES = ['English', 'Hindi', 'Mandarin', 'Spanish'];

const ConnectionForm = ({ onConnect }) => {
  const [name, setName] = useState('');
  const [language, setLanguage] = useState('English');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const ws = new WebSocket(`ws://localhost:8000/ws/connect`);
    
    ws.onopen = () => {
      console.log("WebSocket connection opened");
      ws.send(JSON.stringify({ name, language }));
    };
    
    ws.onmessage = (event) => {
      const response = JSON.parse(event.data);
      if (response.status === 200) {
        console.log("WebSocket connection established with server");
        onConnect({ name, language, ws });
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    ws.onclose = (event) => {
      console.log("WebSocket connection closed:", event);
    };
  };

  return (
    <div className="connection-form-container">
      <form onSubmit={handleSubmit} className="connection-form">
        <input
          type="text"
          placeholder="Enter your name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
        >
          {LANGUAGES.map(lang => (
            <option key={lang} value={lang}>{lang}</option>
          ))}
        </select>
        <button type="submit">Connect</button>
      </form>
    </div>
  );
};

export default ConnectionForm;