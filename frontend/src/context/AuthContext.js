import React, { createContext, useState, useContext, useEffect } from 'react';
import { authService } from '../services/api';
import { toast } from 'react-toastify';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    useEffect(() => {
        const token = localStorage.getItem('access_token');
        if (token) {
            loadUser();
        } else {
            setLoading(false);
        }
    }, []);

    const loadUser = async () => {
        try {
            const response = await authService.getProfile();
            setUser(response.data);
            setIsAuthenticated(true);
        } catch (error) {
            localStorage.clear();
            setUser(null);
            setIsAuthenticated(false);
        } finally {
            setLoading(false);
        }
    };

    const login = async (email, password) => {
        try {
            const response = await authService.login({ email, password });
            const { access_token, refresh_token, user } = response.data;
            localStorage.setItem('access_token', access_token);
            localStorage.setItem('refresh_token', refresh_token);
            setUser(user);
            setIsAuthenticated(true);
            toast.success('Login successful!');
            return { success: true };
        } catch (error) {
            toast.error(error.response?.data?.error || 'Login failed');
            return { success: false, error: error.response?.data?.error };
        }
    };

    const register = async (userData) => {
        try {
            await authService.register(userData);
            toast.success('Registration successful! Please login.');
            return { success: true };
        } catch (error) {
            toast.error(error.response?.data?.error || 'Registration failed');
            return { success: false, error: error.response?.data?.error };
        }
    };

    const logout = () => {
        authService.logout();
        setUser(null);
        setIsAuthenticated(false);
        toast.info('Logged out successfully');
    };

    const updateProfile = async (data) => {
        try {
            const response = await authService.updateProfile(data);
            setUser(response.data.user);
            toast.success('Profile updated successfully!');
            return { success: true };
        } catch (error) {
            toast.error(error.response?.data?.error || 'Update failed');
            return { success: false };
        }
    };

    const value = {
        user,
        loading,
        isAuthenticated,
        login,
        register,
        logout,
        updateProfile,
        loadUser,
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};