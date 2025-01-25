import React, { useState, useEffect, useRef } from 'react';
import { Send } from 'lucide-react';
import './ChatComponent.css'; // Import the CSS file

const ChatComponent = () => {
    const [messages, setMessages] = useState([]);
    const [newMessage, setNewMessage] = useState('');
    const [socket, setSocket] = useState(null);
    const messagesEndRef = useRef(null);

    const DEVICE_ID = 'device1';
    const TARGET_DEVICE = 'device2';
    const WS_URL = `ws://192.168.1.178:8765/ws/${DEVICE_ID}`;

    useEffect(() => {
        const ws = new WebSocket(WS_URL);

        ws.onopen = () => {
            console.log('Connected to WebSocket');
        };

        ws.onmessage = (event) => {
            const receivedMessage = JSON.parse(event.data);
            setMessages(prev => [...prev, {
                text: receivedMessage.message,
                sender: 'other'
            }]);
        };

        setSocket(ws);

        return () => ws.close();
    }, []);

    const sendMessage = () => {
        if (!newMessage.trim() || !socket) return;

        const messageData = {
            target_device: TARGET_DEVICE,
            message: newMessage
        };

        socket.send(JSON.stringify(messageData));

        setMessages(prev => [...prev, {
            text: newMessage,
            sender: 'me'
        }]);
        setNewMessage('');
    };

    return (
        <div className="chat-container">
            <div className="chat-header">
                <h1>{DEVICE_ID}</h1>
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
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
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