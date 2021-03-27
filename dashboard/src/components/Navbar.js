import React, { Component } from 'react';
import { Navbar } from 'react-bootstrap';

export class NavBar extends Component {
    render() {
        return (
            <Navbar bg="dark" variant="dark">
                <Navbar.Brand href="#home">Graph AI</Navbar.Brand>
            </Navbar>
        )
    }
}