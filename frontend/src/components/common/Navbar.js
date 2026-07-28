import React from 'react';
import { Navbar, Nav, Container, Button } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const Navigation = () => {
    const { user, isAuthenticated, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <Navbar bg="dark" variant="dark" expand="lg" className="mb-4">
            <Container>
                <Navbar.Brand as={Link} to="/">
                    🚗 RentWheel
                </Navbar.Brand>
                <Navbar.Toggle aria-controls="basic-navbar-nav" />
                <Navbar.Collapse id="basic-navbar-nav">
                    <Nav className="me-auto">
                        <Nav.Link as={Link} to="/">Home</Nav.Link>
                        <Nav.Link as={Link} to="/cars">Browse Cars</Nav.Link>
                        {isAuthenticated && (
                            <Nav.Link as={Link} to="/my-rentals">My Rentals</Nav.Link>
                        )}
                        {isAuthenticated && user?.role === 'admin' && (
                            <>
                                <Nav.Link as={Link} to="/admin/dashboard">Dashboard</Nav.Link>
                                <Nav.Link as={Link} to="/admin/cars">Manage Cars</Nav.Link>
                            </>
                        )}
                    </Nav>
                    <Nav>
                        {isAuthenticated ? (
                            <>
                                <Nav.Link as={Link} to="/profile">
                                    👤 {user?.first_name || user?.username}
                                </Nav.Link>
                                <Button variant="outline-light" size="sm" onClick={handleLogout}>
                                    Logout
                                </Button>
                            </>
                        ) : (
                            <>
                                <Nav.Link as={Link} to="/login">Login</Nav.Link>
                                <Nav.Link as={Link} to="/register">Register</Nav.Link>
                            </>
                        )}
                    </Nav>
                </Navbar.Collapse>
            </Container>
        </Navbar>
    );
};

export default Navigation;