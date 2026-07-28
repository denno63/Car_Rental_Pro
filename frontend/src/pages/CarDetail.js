import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Container, Row, Col, Card, Button, Form, Spinner, Alert } from 'react-bootstrap';
import { useAuth } from '../context/AuthContext';
import { carService, rentalService } from '../services/api';
import { toast } from 'react-toastify';

const CarDetail = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const { isAuthenticated } = useAuth();
    const [car, setCar] = useState(null);
    const [loading, setLoading] = useState(true);
    const [booking, setBooking] = useState({
        start_date: '',
        end_date: '',
        notes: ''
    });
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        loadCar();
    }, [id]);

    const loadCar = async () => {
        try {
            const response = await carService.getById(id);
            setCar(response.data);
        } catch (error) {
            toast.error('Failed to load car details');
            navigate('/cars');
        } finally {
            setLoading(false);
        }
    };

    const handleBookingChange = (e) => {
        setBooking({ ...booking, [e.target.name]: e.target.value });
    };

    const handleBook = async (e) => {
        e.preventDefault();
        if (!isAuthenticated) {
            toast.info('Please login to book a car');
            navigate('/login');
            return;
        }

        setSubmitting(true);
        try {
            await rentalService.create({
                car_id: parseInt(id),
                ...booking
            });
            toast.success('Booking successful!');
            navigate('/my-rentals');
        } catch (error) {
            toast.error(error.response?.data?.error || 'Booking failed');
        } finally {
            setSubmitting(false);
        }
    };

    if (loading) {
        return (
            <Container className="text-center mt-5">
                <Spinner animation="border" />
            </Container>
        );
    }

    if (!car) {
        return (
            <Container className="text-center mt-5">
                <Alert variant="danger">Car not found</Alert>
            </Container>
        );
    }

    return (
        <Container className="mt-4">
            <Row>
                <Col md={8}>
                    <Card>
                        <Card.Body>
                            <h1>{car.make} {car.model}</h1>
                            <h5 className="text-muted">{car.year}</h5>
                            <hr />
                            <Row>
                                <Col md={6}>
                                    <p><strong>Type:</strong> {car.car_type || 'N/A'}</p>
                                    <p><strong>Color:</strong> {car.color || 'N/A'}</p>
                                    <p><strong>Seats:</strong> {car.seats}</p>
                                    <p><strong>Transmission:</strong> {car.transmission || 'N/A'}</p>
                                </Col>
                                <Col md={6}>
                                    <p><strong>Fuel Type:</strong> {car.fuel_type || 'N/A'}</p>
                                    <p><strong>Mileage:</strong> {car.mileage?.toLocaleString() || 'N/A'}</p>
                                    <p><strong>License Plate:</strong> {car.license_plate}</p>
                                    <p>
                                        <strong>Status:</strong>{' '}
                                        <span className={car.is_available ? 'text-success' : 'text-danger'}>
                                            {car.is_available ? 'Available' : 'Not Available'}
                                        </span>
                                    </p>
                                </Col>
                            </Row>
                            {car.description && (
                                <>
                                    <hr />
                                    <p><strong>Description:</strong></p>
                                    <p>{car.description}</p>
                                </>
                            )}
                            <hr />
                            <h3 className="text-primary">${car.daily_rate}/day</h3>
                        </Card.Body>
                    </Card>
                </Col>

                <Col md={4}>
                    <Card>
                        <Card.Body>
                            <h4>Book This Car</h4>
                            {car.is_available ? (
                                <Form onSubmit={handleBook}>
                                    <Form.Group className="mb-3">
                                        <Form.Label>Start Date</Form.Label>
                                        <Form.Control
                                            type="datetime-local"
                                            name="start_date"
                                            value={booking.start_date}
                                            onChange={handleBookingChange}
                                            required
                                        />
                                    </Form.Group>
                                    <Form.Group className="mb-3">
                                        <Form.Label>End Date</Form.Label>
                                        <Form.Control
                                            type="datetime-local"
                                            name="end_date"
                                            value={booking.end_date}
                                            onChange={handleBookingChange}
                                            required
                                        />
                                    </Form.Group>
                                    <Form.Group className="mb-3">
                                        <Form.Label>Notes</Form.Label>
                                        <Form.Control
                                            as="textarea"
                                            rows={3}
                                            name="notes"
                                            value={booking.notes}
                                            onChange={handleBookingChange}
                                            placeholder="Special requests..."
                                        />
                                    </Form.Group>
                                    <Button
                                        type="submit"
                                        variant="primary"
                                        className="w-100"
                                        disabled={submitting}
                                    >
                                        {submitting ? 'Booking...' : 'Book Now'}
                                    </Button>
                                    {!isAuthenticated && (
                                        <p className="text-muted mt-2 text-center">
                                            <small>Please login to book</small>
                                        </p>
                                    )}
                                </Form>
                            ) : (
                                <Alert variant="warning">
                                    This car is currently not available
                                </Alert>
                            )}
                        </Card.Body>
                    </Card>
                </Col>
            </Row>
        </Container>
    );
};

export default CarDetail;