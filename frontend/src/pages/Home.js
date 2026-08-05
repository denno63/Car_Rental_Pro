import React, { useEffect, useState } from 'react';
import { Container, Row, Col, Card, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { carService } from '../services/api';

const Home = () => {
    const [cars, setCars] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadCars();
    }, []);

    const loadCars = async () => {
        try {
            const response = await carService.getAvailable();
            setCars(response.data?.cars?.slice(0, 4));
        } catch (error) {
            console.error('Error loading cars:', error);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return <div className="text-center mt-5">Loading...</div>;
    }

    return (
        <Container className="mt-4">
            <div className="text-center mb-5">
                <h1>🚗 Welcome to RentWheel</h1>
                <p className="lead">Your trusted car rental service</p>
            </div>

            <h2 className="mb-4">Featured Cars</h2>
            <Row>
                {cars.map((car) => (
                    <Col key={car.id} md={3} className="mb-4">
                        <Card>
                            <Card.Body>
                                <Card.Title>{car.make} {car.model}</Card.Title>
                                <Card.Subtitle className="mb-2 text-muted">{car.year}</Card.Subtitle>
                                <Card.Text>
                                    <div><strong>Type:</strong> {car.car_type || 'N/A'}</div>
                                    <div><strong>Seats:</strong> {car.seats}</div>
                                    <div><strong>Price:</strong> ${car.daily_rate}/day</div>
                                    <div className={car.is_available ? 'text-success' : 'text-danger'}>
                                        {car.is_available ? '✅ Available' : '❌ Not Available'}
                                    </div>
                                </Card.Text>
                                <Button
                                    as={Link}
                                    to={car.is_available ? `/cars/${car.id}` : '#'}
                                    variant={car.is_available ? 'primary' : 'secondary'}
                                    disabled={!car.is_available}
                                    className="w-100"
                                >
                                    {car.is_available ? 'View Details' : 'Unavailable'}
                                </Button>
                            </Card.Body>
                        </Card>
                    </Col>
                ))}
            </Row>
            <div className="text-center">
                <Button as={Link} to="/cars" variant="outline-primary">
                    View All Cars
                </Button>
            </div>
        </Container>
    );
};

export default Home;