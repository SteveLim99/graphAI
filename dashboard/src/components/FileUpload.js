import React, { Component } from 'react';
import { Form, Button } from "react-bootstrap";
import styled from "styled-components";
import axios from "axios";

const Styles = styled.div`

  .form-container {
    padding: 2%;
    border-radius: 3px;
    vertical-align: middle;
    width: 100vw;
    height: 100vh;
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

  .loader {
    display: none;
    border: 3px solid whitesmoke;
    border-top: 3px solid #007bff;
    border-radius: 50%;
    width: 33px;
    height: 33px;
    margin-left:20px;
    animation: spin 0.35s linear infinite;
  }

  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
`;

export class FileUpload extends Component {
  constructor(props) {
    super(props);
    this.state = {
      uploadedFile: null,
      fileUploadLabel: "Attach a File"
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
    const form = document.querySelector("#form-group");
    e.preventDefault();
    loader.style.display = "flex";
    const { uploadedFile } = this.state;
    const formData = new FormData();
    formData.append("file", uploadedFile);
    try {
      var res = await axios.post(
        "/fileUpload",
        formData,
        {}
      );
      if (res.status === 200) {
        const arr = res.data["arrow_img"];
        const ent = res.data["entity_img"];
        const nx = res.data["networkx_img"];
        this.props.handleImgChanges(arr, ent, nx)
        this.props.toggle();
      }
    } catch (error) {
      alert("File submission error, check console for error message");
      loader.style.display = "none";
    }
    this.setState({
      fileUploadLabel: "Attach a File"
    })
    loader.style.display = "none";
    if (!this.props.open) {
      form.reset();
    }
  }

  render() {
    return (
      <Styles>
        <Form className="form-container" id="form-group">
          <div id="child">
            <h3 className="form-title">Insert File to Get Started</h3>
            <Form.Group
              required
              type="file"
              onChange={this.handleChanges}
              controlId="form-file"
            >
              <Form.File required type="file" label={this.state.fileUploadLabel} custom />
              <Form.Text id="passwordHelpInline" muted>
                Uploaded file must be of type .jpeg or .png
              </Form.Text>
            </Form.Group>
            <Form.Row>
              <Button variant="outline-light" type="submit" onClick={this.handleSubmit}>
                Start Prediction
              </Button>
              <div className="loader" id="loading"></div>
            </Form.Row>
          </div>
        </Form>
      </Styles>
    )
  }
};
