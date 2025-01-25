import React, { useState, useEffect, useRef } from 'react';
import { Send } from 'lucide-react';

const ChatApp = () => {
    const [messages, setMessages] = useState([]);
    const [newMessage, setNewMessage] = useState('');
    const [socket, setSocket] = useState(null);
    const messagesEndRef = useRef(null);

    const DEVICE_ID = 'device1';
    const TARGET_DEVICE = 'device2';
    const WS_URL = `ws://192.168.1.178:8765/ws/${DEVICE_ID}`;
    // const WS_URL = 'ws://192.168.1.178:8765/ws/device1_device2'

    useEffect(() => {
        // Establish WebSocket connection
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
        <div className="h-screen flex flex-col bg-gray-100 p-4">
            <div className="flex-grow overflow-y-auto mb-4 space-y-2">
                <h1>{DEVICE_ID}</h1>
                {messages.map((msg, index) => (
                    <div
                        key={index}
                        className={`flex ${msg.sender === 'me' ? 'justify-end' : 'justify-start'}`}
                    >
                        <div
                            className={`p-2 rounded-lg max-w-[70%] ${
                                msg.sender === 'me'
                                    ? 'bg-blue-500 text-white'
                                    : 'bg-gray-200'
                            }`}
                        >
                            {msg.text}
                        </div>
                    </div>
                ))}
            </div>

            <div className="flex">
                <input
                    type="text"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                    className="flex-grow p-2 border rounded-l-lg"
                    placeholder="Type a message"
                />
                <button
                    onClick={sendMessage}
                    className="bg-blue-500 text-white p-2 rounded-r-lg"
                >
                    <Send />
                </button>
            </div>
        </div>
    );
};

export default ChatApp;