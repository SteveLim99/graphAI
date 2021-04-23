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

    handleSaveFromDB = async (e, id, file) => {
        e.preventDefault();
        var endpoint = '/db/dbGetFile?id=' + String(id);
        endpoint += '&file=' + String(file);
        endpoint += "&token=" + this.props.user_token
        axios({
            url: endpoint,
            method: 'GET',
            responseType: 'blob'
        }).then((response) => {
            if (response && response.data["status"]) {
                const msg = response.data["message"]
                alert(msg)
                this.props.handleUserToken(null)
            } else {
                let fileName = "undefined";
                if (file === 1) {
                    fileName = String(id) + "_entity.png";
                } else if (file === 0) {
                    fileName = String(id) + "_arrow.png";
                } else if (file === 2) {
                    fileName = String(id) + "_networkx_obj.gml"
                }
                const url = window.URL.createObjectURL(new Blob([response.data]));
                const link = document.createElement('a');
                link.href = url;
                link.setAttribute('download', fileName);
                document.body.appendChild(link);
                link.click();
            }
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
                            <h4>{this.props.prediction}</h4>
                            <ProgressBar>
                                <ProgressBar variant="success" now={this.props.prob_0} key={1} />
                                <ProgressBar variant="danger" now={this.props.prob_1} key={2} />
                            </ProgressBar>
                            <p>
                                {this.props.content}
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
                                        onClick={(e) => { this.handleSaveFromDB(e, this.props.rowID, 1) }}
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
                                        onClick={(e) => { this.handleSaveFromDB(e, this.props.rowID, 0) }}
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
                                        onClick={(e) => { this.handleSaveFromDB(e, this.props.rowID, 2) }}
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