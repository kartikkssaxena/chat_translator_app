import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import './App.css';
import ChatComponent from './components/ChatComponent';
import RegistrationComponent from './components/RegistrationComponent';

function App() {
  const [deviceId, setDeviceId] = useState('');
  const [language, setLanguage] = useState('');
  const [socket, setSocket] = useState(null);

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/chat" element={<ChatComponent deviceId={deviceId} language={language} socket={socket} />} />
          <Route path="/" element={<RegistrationComponent setDeviceId={setDeviceId} setLanguage={setLanguage} setSocket={setSocket} />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;