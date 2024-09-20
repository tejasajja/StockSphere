import React, { useState, useEffect } from 'react';
import { useLocalState } from './usingLocalStorage';
import { Navigate } from 'react-router-dom';

const PrivateRoute = ({ children, roleRequired }) => {
    const [jwt] = useLocalState("", "jwt");
    const [user, setUser] = useLocalState({}, "user"); // Assuming user is an object
    const [isLoading, setLoading] = useState(true);
    const [isValid, setIsValid] = useState(false);

    useEffect(() => {
        const validateUser = async () => {
            if (!jwt) {
                setIsValid(false);
                setLoading(false);
                return;
            }
    
            try {
                const response = await fetch('http://localhost:8000/api/auth/test-token', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${jwt}`,
                    },
                });
                const data = await response.json();
                if (response.ok) {
                    console.log("API Response:", data); // Debugging: Check what you receive
                    setUser(data);
                    setIsValid(data.role && (!roleRequired || data.role === roleRequired));
                } else {
                    throw new Error(`API responded with status ${response.status}`);
                }
            } catch (error) {
                console.error('Error during user validation', error);
                setIsValid(false);
            } finally {
                setLoading(false);
            }
        };
    
        validateUser();
    }, [jwt]);
    
    if (isLoading) {
        return <div>Loading...</div>;
    }

    if (!isValid) {
        return <Navigate to="/login" replace />;
    }

    return children;
};

export default PrivateRoute;
