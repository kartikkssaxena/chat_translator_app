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
                                sender: receivedMessage?.sender || '',
                                language: receivedMessage?.language || '',
                                message: receivedMessage?.message || '',
                                timeStamp: receivedMessage?.timeStamp || new Date().toISOString()
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
        let timeStamp = new Date().toISOString();
        let messageObj = {
            sender: deviceId,
            language: language,
            message: newMessage,
            timeStamp: timeStamp
        }
        // update chat history
        if (deviceId !== currentUser.device_id) {
            setChatHistory(prev => ({
                ...prev,
                [currentUser.device_id]: [
                    ...(prev[currentUser.device_id] || []),
                    messageObj
                ]
            }));
        }
        
        // Created a local copy of updated history to send to server. This is because state updates are async.
        let updatedHistory = {...chatHistory};
        updatedHistory[deviceId] = [...(updatedHistory[deviceId] || []), messageObj];
        // create message data
        const messageData = {
            type: 'message',
            target_device: currentUser.device_id,
            target_device_language: currentUser.language,
            message: newMessage,
            language: language,
            chatHistory: updatedHistory,
            timeStamp: timeStamp
        };
        // send message to server
        socket.send(JSON.stringify(messageData));
        // clear input field
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
    console.log("chatHistory", chatHistory);
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
                                    {msg.message}
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