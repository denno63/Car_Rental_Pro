import React, { useEffect, useState, useCallback } from 'react';
import { Container, Row, Col, Card, Button, Form, Spinner } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { carService } from '../services/api';

const CarList = () => {
    const [cars, setCars] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filters, setFilters] = useState({
        search: '',
        car_type: '',
        min_rate: '',
        max_rate: '',
        available: ''
    });
    const [carTypes, setCarTypes] = useState([]);
    const [pagination, setPagination] = useState({
        page: 1,
        total_pages: 1,
        total: 0
    });

    // Load car types - runs once on mount
    useEffect(() => {
        loadCarTypes();
    }, []);

    const loadCarTypes = async () => {
        try {
            const response = await carService.getTypes();
            setCarTypes(response.data.types);
        } catch (error) {
            console.error('Error loading car types:', error);
        }
    };

    const loadCars = useCallback(async () => {
        try {
            setLoading(true);
            const params = { ...filters, page: pagination.page };
            Object.keys(params).forEach(key => {
                if (params[key] === '' || params[key] === null || params[key] === undefined) {
                    delete params[key];
                }
            });
            const response = await carService.getAll(params);
            setCars(response.data.cars);
            setPagination({
                page: response.data.page,
                total_pages: response.data.total_pages,
                total: response.data.total
            });
        } catch (error) {
            console.error('Error loading cars:', error);
        } finally {
            setLoading(false);
        }
    }, [filters, pagination.page]);

    useEffect(() => {
        loadCars();
    }, [loadCars]);

    const handleFilterChange = (e) => {
        const { name, value } = e.target;
        setFilters({ ...filters, [name]: value });
        setPagination({ ...pagination, page: 1 });
    };

    const handlePageChange = (newPage) => {
        setPagination({ ...pagination, page: newPage });
        window.scrollTo(0, 0);
    };

    if (loading) {
        return <div className="text-center mt-5"><Spinner animation="border" /></div>;
    }

    return (
        <Container className="mt-4">
            <h1 className="mb-4">Browse Cars</h1>

            <Card className="mb-4">
                <Card.Body>
                    <Form>
                        <Row>
                            <Col md={4}>
                                <Form.Group>
                                    <Form.Label>Search</Form.Label>
                                    <Form.Control
                                        type="text"
                                        name="search"
                                        placeholder="Search by make or model"
                                        value={filters.search}
                                        onChange={handleFilterChange}
                                    />
                                </Form.Group>
                            </Col>
                            <Col md={2}>
                                <Form.Group>
                                    <Form.Label>Type</Form.Label>
                                    <Form.Select
                                        name="car_type"
                                        value={filters.car_type}
                                        onChange={handleFilterChange}
                                    >
                                        <option value="">All Types</option>
                                        {carTypes.map((type) => (
                                            <option key={type.type} value={type.type}>
                                                {type.type} ({type.available} available)
                                            </option>
                                        ))}
                                    </Form.Select>
                                </Form.Group>
                            </Col>
                            <Col md={2}>
                                <Form.Group>
                                    <Form.Label>Min Price</Form.Label>
                                    <Form.Control
                                        type="number"
                                        name="min_rate"
                                        placeholder="Min"
                                        value={filters.min_rate}
                                        onChange={handleFilterChange}
                                    />
                                </Form.Group>
                            </Col>
                            <Col md={2}>
                                <Form.Group>
                                    <Form.Label>Max Price</Form.Label>
                                    <Form.Control
                                        type="number"
                                        name="max_rate"
                                        placeholder="Max"
                                        value={filters.max_rate}
                                        onChange={handleFilterChange}
                                    />
                                </Form.Group>
                            </Col>
                            <Col md={2}>
                                <Form.Group>
                                    <Form.Label>Availability</Form.Label>
                                    <Form.Select
                                        name="available"
                                        value={filters.available}
                                        onChange={handleFilterChange}
                                    >
                                        <option value="">All</option>
                                        <option value="true">Available</option>
                                        <option value="false">Not Available</option>
                                    </Form.Select>
                                </Form.Group>
                            </Col>
                        </Row>
                    </Form>
                </Card.Body>
            </Card>

            <Row>
                {cars.map((car) => (
                    <Col key={car.id} md={4} lg={3} className="mb-4">
                        <Card>
                            <Card.Body>
                                <Card.Title>{car.make} {car.model}</Card.Title>
                                <Card.Subtitle className="mb-2 text-muted">{car.year}</Card.Subtitle>
                                <Card.Text>
                                    <div><strong>Type:</strong> {car.car_type || 'N/A'}</div>
                                    <div><strong>Seats:</strong> {car.seats}</div>
                                    <div><strong>Transmission:</strong> {car.transmission || 'N/A'}</div>
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

            {pagination.total_pages > 1 && (
                <div className="d-flex justify-content-between align-items-center mt-4">
                    <div>
                        Showing {cars.length} of {pagination.total} cars
                    </div>
                    <div>
                        <Button
                            variant="outline-primary"
                            disabled={pagination.page <= 1}
                            onClick={() => handlePageChange(pagination.page - 1)}
                        >
                            Previous
                        </Button>
                        <span className="mx-3">Page {pagination.page} of {pagination.total_pages}</span>
                        <Button
                            variant="outline-primary"
                            disabled={pagination.page >= pagination.total_pages}
                            onClick={() => handlePageChange(pagination.page + 1)}
                        >
                            Next
                        </Button>
                    </div>
                </div>
            )}
        </Container>
    );
};

export default CarList;