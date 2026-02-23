import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [loading, setLoading] = useState(true);

    const logout = useCallback(() => {
        localStorage.removeItem('token');
        setToken(null);
        setUser(null);
    }, []);

    useEffect(() => {
        const verifyToken = async () => {
            if (token) {
                try {
                    const response = await api.get('/auth/me');
                    setUser(response.data);
                } catch (error) {
                    console.error('Token verification failed:', error);
                    logout();
                }
            }
            setLoading(false);
        };

        verifyToken();
    }, [token, logout]);

    const login = async (email, password) => {
        const response = await api.post('/auth/login', { email, password });
        const { access_token, user: userData } = response.data;
        
        localStorage.setItem('token', access_token);
        setToken(access_token);
        setUser(userData);
        
        return userData;
    };

    const register = async (name, email, password) => {
        const response = await api.post('/auth/register', { name, email, password });
        const { access_token, user: userData } = response.data;
        
        localStorage.setItem('token', access_token);
        setToken(access_token);
        setUser(userData);
        
        return userData;
    };

    const refreshUser = async () => {
        if (token) {
            try {
                const response = await api.get('/auth/me');
                setUser(response.data);
            } catch (error) {
                console.error('Failed to refresh user:', error);
            }
        }
    };

    const isAdmin = user?.role === 'admin';

    const value = {
        user,
        token,
        loading,
        login,
        register,
        logout,
        isAdmin,
        refreshUser
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};

export default AuthContext;
