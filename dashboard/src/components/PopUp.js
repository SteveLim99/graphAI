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
        const endpoint = '/ood/fileDownload?id=' + String(id);
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
                                {this.props.isUpload ?
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
                                    :
                                    null
                                }
                            </div>
                            <img src={this.props.entity_img} alt={alternative} className="img-fluid" />
                        </div>

                        <div className="section">
                            <div className="row">
                                <div className="col-md-8">
                                    <h4>Arrow Predictions</h4>
                                </div>
                                {this.props.isUpload ?
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
                                    :
                                    null
                                }
                            </div>
                            <img src={this.props.arrow_img} alt={alternative} className="img-fluid" />
                        </div>
                        <div className="section">
                            <div className="row">
                                <div className="col-md-8">
                                    <h4>Networkx Conversion</h4>
                                </div>
                                {this.props.isUpload ?
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
                                    :
                                    null
                                }

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