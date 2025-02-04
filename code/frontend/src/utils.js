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
                language: language
            };
            console.log("Sending message to the server", messageData);
            socket.send(JSON.stringify(messageData));
        }
    }
}

export const socketClosureInstance = socketClosure();