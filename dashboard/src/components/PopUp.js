import React, { Component } from "react";
import styled from "styled-components";
import { Modal, ProgressBar } from 'react-bootstrap'
import alternative from "../images/alternative.png";
import Button from '@material-ui/core/Button';
import SaveIcon from '@material-ui/icons/Save';
import axios from "axios";

const Styles = styled.div`
    .section{
        padding-top: 2px;
        padding-bottom: 2px;
    }
`;

export class PopUp extends Component {

    handleSave = async (e, id) => {
        e.preventDefault();
        const endpoint = '/fileDownload?id=' + String(id);
        axios({
            url: endpoint,
            method: 'POST',
            responseType: 'blob'
        }).then((response) => {
            let fileName = "undefined";
            if (id === 0) {
                fileName = "entity.png";
            } else if (id === 1) {
                fileName = "arrow.png";
            } else if (id === 2) {
                fileName = "networkx_obj.gml"
            }
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', fileName);
            document.body.appendChild(link);
            link.click();
        });
    }

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
                            <div className="row">
                                <div className="col-md-8">
                                    <h4>Entity Predictions</h4>
                                </div>
                                <div className="col-md-4">
                                    <Button
                                        variant="outlined"
                                        color="default"
                                        size="small"
                                        startIcon={<SaveIcon />}
                                        style={{ float: "right" }}
                                        onClick={(e) => { this.handleSave(e, 0) }}
                                    >
                                        Save
                                    </Button>
                                </div>
                            </div>
                            <img src={this.props.entity_img} alt={alternative} className="img-fluid" />
                        </div>

                        <div className="section">
                            <div className="row">
                                <div className="col-md-8">
                                    <h4>Arrow Predictions</h4>
                                </div>
                                <div className="col-md-4">
                                    <Button
                                        variant="outlined"
                                        color="default"
                                        size="small"
                                        startIcon={<SaveIcon />}
                                        style={{ float: "right" }}
                                        onClick={(e) => { this.handleSave(e, 1) }}
                                    >
                                        Save
                                    </Button>
                                </div>
                            </div>
                            <img src={this.props.arrow_img} alt={alternative} className="img-fluid" />
                        </div>
                        <div className="section">
                            <div className="row">
                                <div className="col-md-8">
                                    <h4>Networkx Conversion</h4>
                                </div>
                                <div className="col-md-4">
                                    <Button
                                        variant="outlined"
                                        color="default"
                                        size="small"
                                        startIcon={<SaveIcon />}
                                        style={{ float: "right" }}
                                        onClick={(e) => { this.handleSave(e, 2) }}
                                    >
                                        Save
                                    </Button>
                                </div>
                            </div>
                            <img src={this.props.networkx_img} alt={alternative} className="img-fluid" />
                        </div>
                    </Modal.Body>
                    <Modal.Footer>
                        <Button onClick={this.props.onHide}>Close</Button>
                    </Modal.Footer>
                </Modal>
            </Styles >
        );
    }
}