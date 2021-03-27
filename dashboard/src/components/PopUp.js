import React, { Component } from "react";
import styled from "styled-components";
import { Modal, Button, ProgressBar } from 'react-bootstrap'
import alternative from "../images/alternative.jpg";

const Styles = styled.div`
    .section{
        padding-top: 2px;
        padding-bottom: 2px;
    }
`;

export class PopUp extends Component {
    render() {
        return (
            <Styles>
                <Modal
                    {...this.props}
                    size="lg"
                    aria-labelledby="contained-modal-title-vcenter"
                    centered
                >
                    <Modal.Header closeButton>
                        <Modal.Title id="contained-modal-title-vcenter">
                            Predictions
                        </Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        <div className="section">
                            <h4>BPNM</h4>
                            <ProgressBar>
                                <ProgressBar variant="success" now={50} key={1} />
                                <ProgressBar variant="danger" now={50} key={2} />
                            </ProgressBar>
                            <p>
                                Business Process Model and Notation is a graphical
                                representation for specifying business processes in a business process model.
                                Originally developed by the Business Process Management Initiative,
                                BPMN has been maintained by the Object Management Group since the
                                two organizations merged in 2005.
                            </p>
                        </div>
                        <div className="section">
                            <h4>Entity Predictions</h4>
                            <img src={this.props.entity_img} alt={alternative} className="img-fluid" />
                        </div>
                        <div className="section">
                            <h4>Arrow Predictions</h4>
                            <img src={this.props.arrow_img} alt={alternative} className="img-fluid" />
                        </div>
                        <h4>Networkx Conversion</h4>
                        <img src={this.props.networkx_img} alt={alternative} className="img-fluid" />
                    </Modal.Body>
                    <Modal.Footer>
                        <Button onClick={this.props.onHide}>Close</Button>
                    </Modal.Footer>
                </Modal>
            </Styles >
        );
    }
}