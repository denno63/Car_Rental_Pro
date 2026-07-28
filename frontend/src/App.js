import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { AuthProvider } from './context/AuthContext';
import PrivateRoute from './components/common/PrivateRoute';
import Navigation from './components/common/Navbar';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import CarList from './pages/CarList';
import './styles/App.css';

function App() {
    return (
        <Router>
            <AuthProvider>
                <Navigation />
                <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Register />} />
                    <Route path="/cars" element={<CarList />} />
                    <Route path="/cars/:id" element={
                        <PrivateRoute>
                            <div>Car Detail Page - Coming Soon</div>
                        </PrivateRoute>
                    } />
                    <Route path="/my-rentals" element={
                        <PrivateRoute>
                            <div>My Rentals Page - Coming Soon</div>
                        </PrivateRoute>
                    } />
                    <Route path="/profile" element={
                        <PrivateRoute>
                            <div>Profile Page - Coming Soon</div>
                        </PrivateRoute>
                    } />
                    <Route path="/admin/dashboard" element={
                        <PrivateRoute adminOnly>
                            <div>Admin Dashboard - Coming Soon</div>
                        </PrivateRoute>
                    } />
                </Routes>
                <ToastContainer position="bottom-right" />
            </AuthProvider>
        </Router>
    );
}

export default App;