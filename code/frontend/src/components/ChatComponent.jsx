import React, { useState, useEffect } from 'react';
import { Send } from 'lucide-react';
import './ChatComponent.css';

const ChatComponent = () => {
    const [messages, setMessages] = useState([]);
    const [newMessage, setNewMessage] = useState('');
    const [socket, setSocket] = useState(null);
    const [language, setLanguage] = useState('English');
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);

    const LANGUAGES = process.env.REACT_APP_LANGUAGES.split(',');
    const DEVICE_ID = process.env.REACT_APP_DEVICE_ID;
    const TARGET_DEVICE = process.env.REACT_APP_TARGET_DEVICE;
    const WS_URL = `${process.env.REACT_APP_WS_URL}${DEVICE_ID}`;

    useEffect(() => {
        const ws = new WebSocket(`${WS_URL}?language=${language}`);

        ws.onopen = () => console.log('Connected to WebSocket');
        ws.onmessage = (event) => {
            const receivedMessage = JSON.parse(event.data);
            setMessages(prev => [...prev, {
                text: receivedMessage.message,
                sender: 'other',
                language: receivedMessage.language
            }]);
        };

        setSocket(ws);

        return () => ws.close();
    }, [language]);

    const sendMessage = () => {
        if (!newMessage.trim() || !socket) return;

        const messageData = {
            target_device: TARGET_DEVICE,
            message: newMessage,
            language: language
        };

        socket.send(JSON.stringify(messageData));

        setMessages(prev => [...prev, {
            text: newMessage,
            sender: 'me',
            language: language
        }]);
        setNewMessage('');
    };

    const toggleDropdown = () => setIsDropdownOpen(!isDropdownOpen);

    const handleLanguageChange = (selectedLanguage) => {
        setLanguage(selectedLanguage);
        setIsDropdownOpen(false);
    };

    return (
        <div className="chat-container">
            <div className="chat-header">
                <h1>{process.env.REACT_APP_NAME}</h1>
                <div className="language-dropdown">
                    <div 
                        className="dropdown-header" 
                        onClick={toggleDropdown}
                    >
                        {language}
                        <span className="dropdown-arrow">▼</span>
                    </div>
                    {isDropdownOpen && (
                        <ul className="dropdown-list">
                            {LANGUAGES.filter(l => l !== language).map(lang => (
                                <li 
                                    key={lang} 
                                    onClick={() => handleLanguageChange(lang)}
                                >
                                    {lang}
                                </li>
                            ))}
                        </ul>
                    )}
                </div>
            </div>

            <div className="chat-messages">
                {messages.map((msg, index) => (
                    <div
                        key={index}
                        className={`message ${msg.sender === 'me' ? 'message-sent' : 'message-received'}`}
                    >
                        <div className="message-text">
                            {msg.text}
                            {/* <span className="message-language">({msg.language})</span> */}
                        </div>
                    </div>
                ))}
            </div>

            <div className="chat-input">
                <input
                    type="text"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
                    placeholder="Type a message"
                />
                <button onClick={sendMessage}>
                    <Send />
                </button>
            </div>
        </div>
    );
};

export default ChatComponent;