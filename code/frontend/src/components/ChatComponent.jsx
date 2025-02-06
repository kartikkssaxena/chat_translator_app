import React, { useState, useEffect } from 'react';
import { Send } from 'lucide-react';
import './ChatComponent.css';
import { socketClosureInstance } from '../utils';

const ChatComponent = ({ deviceId, language, socket }) => {
    const [newMessage, setNewMessage] = useState('');
    const [activeUsers, setActiveUsers] = useState([]);
    const [currentUser, setCurrentUser] = useState({});
    const [chatHistory, setChatHistory] = useState({});

    useEffect(() => {
        if (socket) {
            socket.onmessage = (event) => {
                const receivedMessage = JSON.parse(event.data);
                if (receivedMessage?.type === 'message') {
                    console.log("receivedMessage", receivedMessage);
                    setChatHistory(prev => ({
                        ...prev,
                        [receivedMessage.sender]: [
                            ...(prev[receivedMessage.sender] || []),
                            {
                                text: receivedMessage.message,
                                sender: receivedMessage.sender,
                                language: receivedMessage.language
                            }
                        ]
                    }));

                } else if (receivedMessage?.type === 'active_users') {
                    console.log('active users list -', receivedMessage);
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

        if (deviceId !== currentUser.device_id) {
            setChatHistory(prev => ({
                ...prev,
                [currentUser.device_id]: [
                    ...(prev[currentUser.device_id] || []),
                    {
                        text: newMessage,
                        sender: deviceId,
                        language: language
                    }
                ]
            }));
        }

        setNewMessage('');
    };

    const getChatHistory = () => {

        if (!currentUser?.device_id) {
            return [];
        }
        if (!chatHistory[currentUser.device_id]) {
            return [];
        }
        if (chatHistory[currentUser.device_id].length === 0) {
            return [];
        }
        return chatHistory[currentUser.device_id];
    }

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
                        {getChatHistory().map((msg, index) => (
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