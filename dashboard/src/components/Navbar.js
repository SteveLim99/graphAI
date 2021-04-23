import React, { Component } from 'react';
import { Navbar } from 'react-bootstrap';
import styled from "styled-components";
import MeetingRoomIcon from '@material-ui/icons/MeetingRoom';
import IconButton from '@material-ui/core/IconButton';
import axios from "axios";

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
    handleLogOut = async (e) => {
        e.preventDefault();
        const endpoint = "/user/logout?token=" + this.props.user_token

        try {
            await axios.post(endpoint, {})
        } finally {
            this.props.handleUserToken(null);
            this.props.logOutReset();
        }
    }

    render() {
        return (
            <Styles>
                <Navbar className="navbar" >
                    <Navbar.Brand className="navbar-text">Graph AI</Navbar.Brand>
                    <Navbar.Collapse className="justify-content-end">
                        {this.props.user_token === null ?
                            null
                            :
                            <IconButton
                                className="collapse-icon"
                                color="inherit"
                                onClick={(e) => { this.handleLogOut(e) }}
                            >
                                <MeetingRoomIcon fontSize='default' color='secondary' />
                            </IconButton>}
                    </Navbar.Collapse>
                </Navbar>
            </Styles>
        )
    }
}