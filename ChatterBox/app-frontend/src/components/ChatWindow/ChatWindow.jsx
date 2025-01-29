import React, { useState, useEffect, useRef } from 'react';
import { Send } from 'lucide-react';
import './ChatWindow.css';

const ChatWindow = ({ userProfile }) => {
    const [messages, setMessages] = useState([]);
    const [newMessage, setNewMessage] = useState('');
    const [activeUsers, setActiveUsers] = useState([]);
    const [selectedUser, setSelectedUser] = useState(null);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        if (userProfile?.ws) {
            userProfile.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.type === 'profiles') {
                    const users = Object.entries(data.profiles)
                        .map(([id, profile]) => ({
                            id,
                            name: profile.name,
                            language: profile.language
                        }))
                        .filter(user => user.name !== userProfile.name);
                    setActiveUsers(users);
                } else if (data.type === 'message') {
                    setMessages(prev => [...prev, {
                        text: data.content,
                        sender: 'other',
                        from: data.from
                    }]);
                    scrollToBottom();
                }
            };

            userProfile.ws.onerror = (error) => {
                console.error("WebSocket error:", error);
            };

            userProfile.ws.onclose = (event) => {
                console.log("WebSocket connection closed:", event);
            };
        }

        return () => {
            // if (userProfile?.ws) {
            //     userProfile.ws.close();
            // }
        };
    }, [userProfile]);

    useEffect(scrollToBottom, [messages]);

    const sendMessage = () => {
        if (!newMessage.trim() || !selectedUser) return;

        const messageData = {
            type: 'message',
            target: selectedUser.id,
            content: newMessage
        };

        userProfile.ws.send(JSON.stringify(messageData));

        setMessages(prev => [...prev, {
            text: newMessage,
            sender: 'me'
        }]);
        setNewMessage('');
    };

    const handleUserSelect = (user) => {
        setSelectedUser(user);
        setMessages([]); // Clear messages when switching users
    };

    return (
        <div className="chat-window">
            <div className="users-sidebar">
                <h2>Active Users</h2>
                <div className="users-list">
                    {activeUsers.map((user) => (
                        <div
                            key={user.id}
                            className={`user-item ${selectedUser?.id === user.id ? 'selected' : ''}`}
                            onClick={() => handleUserSelect(user)}
                        >
                            <div className="user-name">{user.name}</div>
                            <div className="user-language">{user.language}</div>
                        </div>
                    ))}
                </div>
            </div>

            <div className="chat-area">
                {selectedUser ? (
                    <>
                        <div className="chat-header">
                            <h3>Chat with {selectedUser.name}</h3>
                            <span className="user-language">{selectedUser.language}</span>
                        </div>
                        <div className="messages-container">
                            {messages.map((msg, index) => (
                                <div
                                    key={index}
                                    className={`message ${msg.sender === 'me' ? 'sent' : 'received'}`}
                                >
                                    <div className="message-content">{msg.text}</div>
                                </div>
                            ))}
                            <div ref={messagesEndRef} />
                        </div>
                        <div className="message-input">
                            <input
                                type="text"
                                value={newMessage}
                                onChange={(e) => setNewMessage(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
                                placeholder="Type a message..."
                            />
                            <button onClick={sendMessage}>
                                <Send size={20} />
                            </button>
                        </div>
                    </>
                ) : (
                    <div className="no-chat-selected">
                        <p>Select a user to start chatting</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ChatWindow;