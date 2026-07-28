import React, { useEffect, useState } from 'react';
import { Container, Row, Col, Card, Spinner, Table } from 'react-bootstrap';
import { rentalService } from '../../services/api';
import { toast } from 'react-toastify';

const AdminDashboard = () => {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadStats();
    }, []);

    const loadStats = async () => {
        try {
            const response = await rentalService.adminGetStats();
            setStats(response.data);
        } catch (error) {
            toast.error('Failed to load dashboard stats');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return <div className="text-center mt-5"><Spinner animation="border" /></div>;
    }

    return (
        <Container className="mt-4">
            <h1 className="mb-4">Admin Dashboard</h1>

            <Row className="mb-4">
                <Col md={3}>
                    <Card className="text-center bg-primary text-white">
                        <Card.Body>
                            <h2>{stats?.total_rentals || 0}</h2>
                            <p>Total Rentals</p>
                        </Card.Body>
                    </Card>
                </Col>
                <Col md={3}>
                    <Card className="text-center bg-success text-white">
                        <Card.Body>
                            <h2>{stats?.active_rentals || 0}</h2>
                            <p>Active Rentals</p>
                        </Card.Body>
                    </Card>
                </Col>
                <Col md={3}>
                    <Card className="text-center bg-info text-white">
                        <Card.Body>
                            <h2>${stats?.total_revenue?.toFixed(2) || '0.00'}</h2>
                            <p>Total Revenue</p>
                        </Card.Body>
                    </Card>
                </Col>
                <Col md={3}>
                    <Card className="text-center bg-warning text-white">
                        <Card.Body>
                            <h2>${stats?.monthly_revenue?.toFixed(2) || '0.00'}</h2>
                            <p>Monthly Revenue</p>
                        </Card.Body>
                    </Card>
                </Col>
            </Row>

            <Row>
                <Col md={6}>
                    <Card>
                        <Card.Header>
                            <h5 className="mb-0">Popular Cars</h5>
                        </Card.Header>
                        <Card.Body>
                            <Table striped>
                                <thead>
                                    <tr>
                                        <th>#</th>
                                        <th>Car</th>
                                        <th>Rentals</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {stats?.popular_cars?.map((car, index) => (
                                        <tr key={index}>
                                            <td>{index + 1}</td>
                                            <td>{car.make} {car.model}</td>
                                            <td>{car.rental_count}</td>
                                        </tr>
                                    ))}
                                    {(!stats?.popular_cars || stats.popular_cars.length === 0) && (
                                        <tr>
                                            <td colSpan="3" className="text-center">No data yet</td>
                                        </tr>
                                    )}
                                </tbody>
                            </Table>
                        </Card.Body>
                    </Card>
                </Col>
                <Col md={6}>
                    <Card>
                        <Card.Header>
                            <h5 className="mb-0">Rental Status</h5>
                        </Card.Header>
                        <Card.Body>
                            <Table striped>
                                <thead>
                                    <tr>
                                        <th>Status</th>
                                        <th>Count</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>Active</td>
                                        <td>{stats?.active_rentals || 0}</td>
                                    </tr>
                                    <tr>
                                        <td>Completed</td>
                                        <td>{stats?.completed_rentals || 0}</td>
                                    </tr>
                                    <tr>
                                        <td>Cancelled</td>
                                        <td>{stats?.cancelled_rentals || 0}</td>
                                    </tr>
                                </tbody>
                            </Table>
                        </Card.Body>
                    </Card>
                </Col>
            </Row>
        </Container>
    );
};

export default AdminDashboard;