import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './RegistrationComponent.css';

const RegistrationComponent = ({ setDeviceId, setLanguage, setSocket }) => {
    const [name, setName] = useState('');
    const [selectedLanguage, setSelectedLanguage] = useState('');
    const navigate = useNavigate();

    const LANGUAGES = process.env.REACT_APP_LANGUAGES.split(',');

    const handleConnect = async () => {
        if (!name || !selectedLanguage) return;

        const DEVICE_ID = name; // Assuming name is used as DEVICE_ID
        const WS_URL = `${process.env.REACT_APP_WS_URL}${DEVICE_ID}`;

        const ws = new WebSocket(`${WS_URL}?language=${selectedLanguage}`);
        ws.onopen = () => {
            console.log('Connected to WebSocket');
            setSocket(ws);
            setDeviceId(DEVICE_ID);
            setLanguage(selectedLanguage);
            navigate('/chat');
        };
    };

    return (
        <div className="registration-container">
            <form onSubmit={(e) => { e.preventDefault(); handleConnect(); }}>
                <h1>Triple OG Register</h1>
                <div className="form-group">
                    <label htmlFor="name">Name</label>
                    <input
                        type="text"
                        id="name"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        required
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="language">Language</label>
                    <select
                        id="language"
                        value={selectedLanguage}
                        onChange={(e) => setSelectedLanguage(e.target.value)}
                        required
                    >
                        <option value="" disabled>Select a language</option>
                        {LANGUAGES.map(lang => (
                            <option key={lang} value={lang}>{lang}</option>
                        ))}
                    </select>
                </div>
                <button className="connect_button" type="submit">Connect</button>
            </form>
        </div>
    );
};

export default RegistrationComponent;