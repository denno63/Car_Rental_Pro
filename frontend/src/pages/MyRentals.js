import React, { useEffect, useState } from 'react';
import { Container, Table, Badge, Button, Spinner, Card } from 'react-bootstrap';
import { rentalService } from '../services/api';
import { toast } from 'react-toastify';

const MyRentals = () => {
    const [rentals, setRentals] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadRentals();
    }, []);

    const loadRentals = async () => {
        try {
            const response = await rentalService.getAll();
            setRentals(response.data.rentals);
        } catch (error) {
            toast.error('Failed to load rentals');
        } finally {
            setLoading(false);
        }
    };

    const handleReturn = async (rentalId) => {
        try {
            await rentalService.returnCar(rentalId);
            toast.success('Car returned successfully!');
            loadRentals();
        } catch (error) {
            toast.error(error.response?.data?.error || 'Return failed');
        }
    };

    const handleCancel = async (rentalId) => {
        if (!window.confirm('Are you sure you want to cancel this rental?')) return;
        try {
            await rentalService.cancel(rentalId);
            toast.success('Rental cancelled successfully!');
            loadRentals();
        } catch (error) {
            toast.error(error.response?.data?.error || 'Cancellation failed');
        }
    };

    const getStatusBadge = (status) => {
        const variants = {
            'active': 'success',
            'completed': 'secondary',
            'cancelled': 'danger',
            'overdue': 'warning'
        };
        return <Badge bg={variants[status] || 'secondary'}>{status.toUpperCase()}</Badge>;
    };

    if (loading) {
        return <div className="text-center mt-5"><Spinner animation="border" /></div>;
    }

    return (
        <Container className="mt-4">
            <h1 className="mb-4">My Rentals</h1>
            {rentals.length === 0 ? (
                <Card>
                    <Card.Body className="text-center">
                        <p>You have no rentals yet.</p>
                        <Button href="/cars">Browse Cars</Button>
                    </Card.Body>
                </Card>
            ) : (
                <Table striped bordered hover responsive>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Car</th>
                            <th>Start Date</th>
                            <th>End Date</th>
                            <th>Total Cost</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rentals.map((rental) => (
                            <tr key={rental.id}>
                                <td>#{rental.id}</td>
                                <td>{rental.car?.make} {rental.car?.model}</td>
                                <td>{new Date(rental.start_date).toLocaleDateString()}</td>
                                <td>{new Date(rental.end_date).toLocaleDateString()}</td>
                                <td>${rental.total_cost?.toFixed(2) || '0.00'}</td>
                                <td>{getStatusBadge(rental.status)}</td>
                                <td>
                                    {rental.status === 'active' && (
                                        <>
                                            <Button
                                                variant="success"
                                                size="sm"
                                                className="me-2"
                                                onClick={() => handleReturn(rental.id)}
                                            >
                                                Return
                                            </Button>
                                            <Button
                                                variant="danger"
                                                size="sm"
                                                onClick={() => handleCancel(rental.id)}
                                            >
                                                Cancel
                                            </Button>
                                        </>
                                    )}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </Table>
            )}
        </Container>
    );
};

export default MyRentals;