import React, { useState, useEffect } from 'react';
import { Send } from 'lucide-react';
import './ChatComponent.css';
import { socketClosureInstance } from '../utils';

const ChatComponent = ({ deviceId, language, socket }) => {
    const [messages, setMessages] = useState([]);
    const [newMessage, setNewMessage] = useState('');

    useEffect(() => {
        if (socket) {
            socket.onmessage = (event) => {
                const receivedMessage = JSON.parse(event.data);
                setMessages(prev => [...prev, {
                    text: receivedMessage.message,
                    sender: 'other',
                    language: receivedMessage.language
                }]);
            };

            socketClosureInstance(socket, deviceId, language);
        }
    }, [socket, deviceId, language]);

    const sendMessage = () => {
        if (!newMessage.trim() || !socket) return;

        const messageData = {
            target_device: process.env.REACT_APP_TARGET_DEVICE,
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

    return (
        <div className="chat-container">
            <div className="chat-header">
                <h1>{deviceId}</h1>
                <div className="language-dropdown">
                    <div className="dropdown-header">
                        {language}
                    </div>
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