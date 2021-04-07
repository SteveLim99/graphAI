import React, { Component } from 'react';
import { Form, Button } from "react-bootstrap";
import styled from "styled-components";
import axios from "axios";
import { LinearProgress } from '@material-ui/core';

const Styles = styled.div`

  .form-container {
    padding: 2%;
    border-radius: 3px;
    vertical-align: middle;
    width: 100vw;
    height: 87vh;
    position: relative;
  }

  .form-title{
    font-family: Sans-serif;
    font-size: 3vw;
    color: #FFFFFF;
    padding-bottom: 6px;
    float: left
  }

  #child{
    position: absolute;
    top: 30vh;
  }

  .progress-bar{
    display: none;
    width: 29vw;
  }
`;

export class FileUpload extends Component {
  constructor(props) {
    super(props);
    this.state = {
      uploadedFile: null,
      fileUploadLabel: "Attach a File",
      title: "Insert File to Get Started"
    }
  }

  handleChanges = e => {
    e.preventDefault();
    this.setState({
      uploadedFile: e.target.files[0],
      fileUploadLabel: e.target.files[0].name
    });
  };

  handleSubmit = async e => {
    const loader = document.getElementById("loading");
    const loader_upload = document.getElementById("loading-items");
    const loader_button = document.getElementById("loading-button");

    loader.style.display = "flex";
    loader_upload.style.display = 'none';
    loader_button.style.display = 'none';

    this.setState({
      title: "Generating Prediction"
    })

    e.preventDefault();
    const form = document.querySelector("#form-group");
    const { uploadedFile } = this.state;
    const formData = new FormData();
    formData.append("file", uploadedFile);

    try {
      var res = await axios.post(
        "/ood/fileUpload",
        formData,
        {}
      );
      if (res.status === 200) {
        const arr = res.data["arrow_img"];
        const ent = res.data["entity_img"];
        const nx = res.data["networkx_img"];
        this.props.handleImgChanges(arr, ent, nx)
      }
    } catch (error) {
      alert("File submission error, check console for error message");
      loader.style.display = "none";
    }

    this.setState({
      title: "Running GNN Model..."
    })

    var pred = ""
    var p0 = ""
    var p1 = ""
    try {
      var gnn_res = await axios.post(
        "/gnn/gmlUpload",
        {}
      );

      if (gnn_res.status === 200) {
        pred = gnn_res.data["prediction"];
        p0 = gnn_res.data["prob_0"];
        p1 = gnn_res.data["probs_1"];
        const content = gnn_res.data["content"];
        this.props.handlePredictionChanges(pred, p0, p1, content)
      }
    } catch (error) {
      alert("File submission error, check console for error message");
    }

    try {
      const pred_endpoint = "?pred=" + pred;
      const bpnm_prob_endpoint = "&BPNM=" + p0;
      const swimlane_prob_endpoint = "&Swimlane=" + p1;
      const endpoint = "/db/dbConnect" + pred_endpoint + bpnm_prob_endpoint + swimlane_prob_endpoint;
      var db_res = await axios.post(
        endpoint,
        {}
      )

      if (db_res.status === 200) {
        console.log("DB Updated")
        const graphID = db_res.data["graphID"]
        this.props.handleRowID(graphID)
      }
      this.props.updateTable();
      this.props.toggle();
    } catch (error) {
      console.log(error)
      alert("File submission error, check console for error message");
      loader.style.display = "none";
    }

    this.setState({
      fileUploadLabel: "Attach a File",
      title: "Insert File to Get Started"
    })

    loader.style.display = "none";
    loader_upload.style.display = 'block';
    loader_button.style.display = 'block';
    if (!this.props.open) {
      form.reset();
    }
  }

  render() {
    return (
      <Styles>
        <Form className="form-container" id="form-group">
          <div id="child">
            <h3 className="form-title">{this.state.title}</h3>
            <Form.Group
              required
              type="file"
              onChange={this.handleChanges}
              controlId="form-file"
            >
              <LinearProgress
                color='primary'
                className='progress-bar'
                id='loading'>
              </LinearProgress>
              <div id="loading-items">
                <Form.File
                  required type="file"
                  label={this.state.fileUploadLabel}
                  custom />
                <Form.Text
                  id="passwordHelpInline"
                  muted>
                  Uploaded file must be of type .jpeg or .png
              </Form.Text>
              </div>
            </Form.Group>
            <Form.Row>
              <Button
                variant="outline-light"
                type="submit"
                onClick={this.handleSubmit}
                id='loading-button'>
                Start Prediction
              </Button>
            </Form.Row>
          </div>
        </Form>
      </Styles>
    )
  }
};
