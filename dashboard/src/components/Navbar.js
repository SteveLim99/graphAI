import React, { Component } from 'react';
import { Navbar } from 'react-bootstrap';
import styled from "styled-components";

const Styles = styled.div`
    .navbar{
        background-color: rgba(108,117,125,0.15);
        width: 100vw;
        border-bottom: 0.5px solid #6C757D
    }

    .navbar-text{
        padding-left: 60px;
        color: white;
    }
`

export class NavBar extends Component {
    render() {
        return (
            <Styles>
                <Navbar className="navbar" >
                    <Navbar.Brand className="navbar-text">Graph AI</Navbar.Brand>
                </Navbar>
            </Styles>
        )
    }
}