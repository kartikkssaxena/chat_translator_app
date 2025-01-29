import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar/Navbar';
import ConnectionForm from './components/ConnectionForm/ConnectionForm';
import ChatWindow from './components/ChatWindow/ChatWindow';
import './App.css';

function App() {
  const [isConnected, setIsConnected] = React.useState(false);
  const [userProfile, setUserProfile] = React.useState(null);

  return (
    <Router>
      <div className="app">
        <Navbar />
        <Routes>
          <Route path="/" element={
            isConnected ? 
            <ChatWindow userProfile={userProfile} /> : 
            <ConnectionForm 
              onConnect={(profile) => {
                setUserProfile(profile);
                setIsConnected(true);
              }} 
            />
          } />
        </Routes>
      </div>
    </Router>
  );
}

export default App;