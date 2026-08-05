import React, { useEffect, useState } from 'react';
import { Container, Table, Button, Modal, Form, Spinner, Row, Col } from 'react-bootstrap';
import { carService } from '../../services/api';
import { toast } from 'react-toastify';

const AdminCars = () => {
    const [cars, setCars] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [editingCar, setEditingCar] = useState(null);
    const [formData, setFormData] = useState({
        make: '',
        model: '',
        year: '',
        license_plate: '',
        color: '',
        daily_rate: '',
        car_type: '',
        seats: 5,
        transmission: '',
        fuel_type: '',
        description: ''
    });
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        loadCars();
    }, []);

    const loadCars = async () => {
        try {
            const response = await carService.getAll({ per_page: 100 });
            setCars(response.data.cars);
        } catch (error) {
            toast.error('Failed to load cars');
        } finally {
            setLoading(false);
        }
    };

    const handleOpenModal = (car = null) => {
        if (car) {
            setEditingCar(car);
            setFormData(car);
        } else {
            setEditingCar(null);
            setFormData({
                make: '',
                model: '',
                year: '',
                license_plate: '',
                color: '',
                daily_rate: '',
                car_type: '',
                seats: 5,
                transmission: '',
                fuel_type: '',
                description: ''
            });
        }
        setShowModal(true);
    };

    const handleCloseModal = () => {
        setShowModal(false);
        setEditingCar(null);
    };

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSubmitting(true);
        try {
            if (editingCar) {
                await carService.update(editingCar.id, formData);
                toast.success('Car updated successfully!');
            } else {
                await carService.create(formData);
                toast.success('Car added successfully!');
            }
            handleCloseModal();
            loadCars();
        } catch (error) {
            toast.error(error.response?.data?.error || 'Operation failed');
        } finally {
            setSubmitting(false);
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm('Are you sure you want to delete this car?')) return;
        try {
            await carService.delete(id);
            toast.success('Car deleted successfully!');
            loadCars();
        } catch (error) {
            toast.error(error.response?.data?.error || 'Delete failed');
        }
    };

    if (loading) {
        return <div className="text-center mt-5"><Spinner animation="border" /></div>;
    }

    return (
        <Container className="mt-4">
            <div className="d-flex justify-content-between align-items-center mb-4">
                <h1>Manage Cars</h1>
                <Button variant="primary" onClick={() => handleOpenModal()}>
                    Add Car
                </Button>
            </div>

            <Table striped bordered hover responsive>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Make</th>
                        <th>Model</th>
                        <th>Year</th>
                        <th>Plate</th>
                        <th>Rate</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {cars.map((car) => (
                        <tr key={car.id}>
                            <td>{car.id}</td>
                            <td>{car.make}</td>
                            <td>{car.model}</td>
                            <td>{car.year}</td>
                            <td>{car.license_plate}</td>
                            <td>${car.daily_rate}</td>
                            <td>
                                <span className={car.is_available ? 'text-success' : 'text-danger'}>
                                    {car.is_available ? 'Available' : 'Booked'}
                                </span>
                            </td>
                            <td>
                                <Button
                                    variant="warning"
                                    size="sm"
                                    className="me-2"
                                    onClick={() => handleOpenModal(car)}
                                >
                                    Edit
                                </Button>
                                <Button
                                    variant="danger"
                                    size="sm"
                                    onClick={() => handleDelete(car.id)}
                                >
                                    Delete
                                </Button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </Table>

            <Modal show={showModal} onHide={handleCloseModal} size="lg">
                <Modal.Header closeButton>
                    <Modal.Title>{editingCar ? 'Edit Car' : 'Add New Car'}</Modal.Title>
                </Modal.Header>
                <Form onSubmit={handleSubmit}>
                    <Modal.Body>
                        <Row>
                            <Col md={6}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Make *</Form.Label>
                                    <Form.Control
                                        type="text"
                                        name="make"
                                        value={formData.make}
                                        onChange={handleChange}
                                        required
                                    />
                                </Form.Group>
                            </Col>
                            <Col md={6}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Model *</Form.Label>
                                    <Form.Control
                                        type="text"
                                        name="model"
                                        value={formData.model}
                                        onChange={handleChange}
                                        required
                                    />
                                </Form.Group>
                            </Col>
                        </Row>
                        <Row>
                            <Col md={4}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Year *</Form.Label>
                                    <Form.Control
                                        type="number"
                                        name="year"
                                        value={formData.year}
                                        onChange={handleChange}
                                        required
                                    />
                                </Form.Group>
                            </Col>
                            <Col md={4}>
                                <Form.Group className="mb-3">
                                    <Form.Label>License Plate *</Form.Label>
                                    <Form.Control
                                        type="text"
                                        name="license_plate"
                                        value={formData.license_plate}
                                        onChange={handleChange}
                                        required
                                    />
                                </Form.Group>
                            </Col>
                            <Col md={4}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Daily Rate *</Form.Label>
                                    <Form.Control
                                        type="number"
                                        name="daily_rate"
                                        value={formData.daily_rate}
                                        onChange={handleChange}
                                        step="0.01"
                                        required
                                    />
                                </Form.Group>
                            </Col>
                        </Row>
                        <Row>
                            <Col md={4}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Color</Form.Label>
                                    <Form.Control
                                        type="text"
                                        name="color"
                                        value={formData.color}
                                        onChange={handleChange}
                                    />
                                </Form.Group>
                            </Col>
                            <Col md={4}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Car Type</Form.Label>
                                    <Form.Control
                                        type="text"
                                        name="car_type"
                                        value={formData.car_type}
                                        onChange={handleChange}
                                    />
                                </Form.Group>
                            </Col>
                            <Col md={4}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Seats</Form.Label>
                                    <Form.Control
                                        type="number"
                                        name="seats"
                                        value={formData.seats}
                                        onChange={handleChange}
                                    />
                                </Form.Group>
                            </Col>
                        </Row>
                        <Row>
                            <Col md={6}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Transmission</Form.Label>
                                    <Form.Select
                                        name="transmission"
                                        value={formData.transmission}
                                        onChange={handleChange}
                                    >
                                        <option value="">Select...</option>
                                        <option value="Automatic">Automatic</option>
                                        <option value="Manual">Manual</option>
                                        <option value="CVT">CVT</option>
                                    </Form.Select>
                                </Form.Group>
                            </Col>
                            <Col md={6}>
                                <Form.Group className="mb-3">
                                    <Form.Label>Fuel Type</Form.Label>
                                    <Form.Select
                                        name="fuel_type"
                                        value={formData.fuel_type}
                                        onChange={handleChange}
                                    >
                                        <option value="">Select...</option>
                                        <option value="Gasoline">Gasoline</option>
                                        <option value="Diesel">Diesel</option>
                                        <option value="Electric">Electric</option>
                                        <option value="Hybrid">Hybrid</option>
                                    </Form.Select>
                                </Form.Group>
                            </Col>
                        </Row>
                        <Form.Group className="mb-3">
                            <Form.Label>Description</Form.Label>
                            <Form.Control
                                as="textarea"
                                rows={3}
                                name="description"
                                value={formData.description}
                                onChange={handleChange}
                            />
                        </Form.Group>
                    </Modal.Body>
                    <Modal.Footer>
                        <Button variant="secondary" onClick={handleCloseModal}>
                            Cancel
                        </Button>
                        <Button type="submit" variant="primary" disabled={submitting}>
                            {submitting ? 'Saving...' : 'Save'}
                        </Button>
                    </Modal.Footer>
                </Form>
            </Modal>
        </Container>
    );
};

export default AdminCars;