import React, { useState, useEffect } from 'react';
import { Send } from 'lucide-react';
import './ChatComponent.css';
import { socketClosureInstance } from '../utils';

const ChatComponent = ({ deviceId, language, socket }) => {
    const [messages, setMessages] = useState([]);
    const [newMessage, setNewMessage] = useState('');
    const [activeUsers, setActiveUsers] = useState([]);
    const [currentUser, setCurrentUser] = useState({});

    useEffect(() => {
        if (socket) {
            socket.onmessage = (event) => {
                const receivedMessage = JSON.parse(event.data);
                console.log(receivedMessage);
                if (receivedMessage?.type === 'message') {
                    setMessages(prev => [...prev, {
                        text: receivedMessage.message,
                        sender: receivedMessage.sender,
                        language: receivedMessage.language
                    }]);
                } else if (receivedMessage?.type === 'active_users') {
                    console.log('receivedMessage', receivedMessage);
                    setActiveUsers(receivedMessage?.users);
                }
            };

            socketClosureInstance(socket, deviceId, language);
        }
    }, [socket, deviceId, language]);

    const sendMessage = () => {
        if (!newMessage.trim() || !socket) return;

        const messageData = {
            target_device: currentUser.device_id,
            message: newMessage,
            language: language
        };

        socket.send(JSON.stringify(messageData));

        setMessages(prev => [...prev, {
            text: newMessage,
            sender: deviceId,
            language: language
        }]);
        setNewMessage('');
    };
    console.log("messages", messages);
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
            <div className='chat-window-container'>
                <div className='active-users'>
                    <h2>Available Users</h2>
                    <ul>
                        {activeUsers.map((user) => (
                            <li
                                key={user.device_id}
                                onClick={() => setCurrentUser(user)}
                                className={currentUser.device_id === user.device_id ? 'selected-user' : ''}
                            >
                                {user.device_id} ({user.language})
                            </li>
                        ))}
                    </ul>
                </div>
                <div className='chat-window'>
                    <div className="chat-messages">
                        {messages.map((msg, index) => (
                            <div
                                key={index}
                                className={`message ${msg.sender === deviceId ? 'message-sent' : 'message-received'}`}
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
            </div>
        </div>
    );
};

export default ChatComponent;