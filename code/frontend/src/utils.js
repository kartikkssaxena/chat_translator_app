const socketClosure = () => {
    let runOnce = false;
    return (socket, DEVICE_ID, language) => {
        console.log("Socket closure function called with", socket, DEVICE_ID, language);
        if (runOnce) return;
        if (socket.readyState === WebSocket.OPEN) {
            runOnce = true;
            console.log("Socket is open");
            const messageData = {
                target_device: "server",
                message: "Test Ping",
                sender: DEVICE_ID,
                language: language,
                timeStamp: new Date().toISOString()
            };
            console.log("Sending message to the server", messageData);
            socket.send(JSON.stringify(messageData));
        }
    }
}

export const socketClosureInstance = socketClosure();

export const chatHistoryClosure = () => {
    let runOnce = false;
    return (param, func)=>{
        if(runOnce) return;
        runOnce = true;
        func(param);
        console.log("Chat history closure function called with", param);
    }
}

export const chatHistoryClosureInstance = chatHistoryClosure();