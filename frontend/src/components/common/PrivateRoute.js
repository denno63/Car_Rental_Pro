import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const PrivateRoute = ({ children, adminOnly = false }) => {
    const { isAuthenticated, user, loading } = useAuth();

    if (loading) {
        return <div className="text-center mt-5">Loading...</div>;
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" />;
    }

    if (adminOnly && user?.role !== 'admin') {
        return <Navigate to="/" />;
    }

    return children;
};

export default PrivateRoute;