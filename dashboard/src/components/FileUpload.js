import React, { Component } from 'react';
import { Form, Button } from "react-bootstrap";
import styled from "styled-components";
import axios from "axios";
import { LinearProgress } from '@material-ui/core';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Switch from '@material-ui/core/Switch';

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
      gcType: true,
      fileUploadLabel: "Attach a File",
      title: "Insert File to Get Started",
      gcTitle: "KSVM Image Classification"
    }
  }

  handleGcChoice = () => {
    if (this.state.gcType) {
      this.setState({
        gcType: false,
        gcTitle: "Graph Neural Networks Graph Classification"
      })
    } else {
      this.setState({
        gcType: true,
        gcTitle: "KSVM Image Classification"
      })
    }
  }

  handleChanges = e => {
    e.preventDefault();
    // File types are validated on upload 
    var accept_types = /(\.jpg|\.jpeg|\.png)$/i;
    var file = e.target.files[0];

    if (!accept_types.exec(file.name)) {
      this.setState({
        fileUploadLabel: "Invalid File Type. Please Try Again."
      })
    } else {
      this.setState({
        uploadedFile: file,
        fileUploadLabel: file.name
      });
    }
  };

  handleSubmit = async e => {
    e.preventDefault();
    const loader = document.getElementById("loading");
    const loader_upload = document.getElementById("loading-items");
    const loader_button = document.getElementById("loading-button");
    const loader_gc_choice = document.getElementById('loading-gc-choice');

    const token = "token=" + this.props.user_token;

    loader.style.display = "flex";
    loader_upload.style.display = 'none';
    loader_button.style.display = 'none';
    loader_gc_choice.style.display = 'none';

    this.setState({
      title: "Generating Prediction"
    })

    const form = document.querySelector("#form-group");
    const { uploadedFile, gcType, fileUploadLabel } = this.state;
    const formData = new FormData();
    formData.append("file", uploadedFile);

    var gcChoice = "";
    if (gcType === true) {
      gcChoice = "ksvm";
    } else {
      gcChoice = "gnn"
    }

    try {
      var res = await axios.post(
        "/ood/fileUpload?" + token,
        formData,
        {}
      );
      if (res.status === 200) {
        const status = res.data["status"];

        if (status === "success") {
          const arr = res.data["arrow_img"];
          const ent = res.data["entity_img"];
          const nx = res.data["networkx_img"];
          const fname_hash = res.data["file_name_hash"];
          this.props.handleImgChanges(arr, ent, nx)

          this.setState({
            title: "Running Graph Classification Model..."
          })

          var pred = ""
          var p0 = ""
          var p1 = ""

          const graph_method = "&gcType=" + gcChoice;
          const fname = "&fname_hash=" + fname_hash;
          var gnn_res = await axios.post(
            "/gnn/gmlUpload?" + token + graph_method + fname,
            {}
          );

          if (gnn_res.status === 200) {
            const gnn_status = gnn_res.data["status"];

            if (gnn_status === "success") {
              pred = gnn_res.data["prediction"];
              p0 = gnn_res.data["prob_0"];
              p1 = gnn_res.data["probs_1"];
              const content = gnn_res.data["content"];

              this.props.handlePredictionChanges(pred, p0, p1, content)

              const pred_endpoint = "?pred=" + pred;
              const bpnm_prob_endpoint = "&BPNM=" + p0;
              const swimlane_prob_endpoint = "&Swimlane=" + p1;
              const ori_file_name = "&inputName=" + fileUploadLabel;

              const endpoint = "/db/dbConnect" + pred_endpoint + bpnm_prob_endpoint + swimlane_prob_endpoint + "&" + token + fname + ori_file_name;
              var db_res = await axios.post(
                endpoint,
                {}
              )

              if (db_res.status === 200) {
                const db_status = db_res.data["status"];

                if (db_status === "success") {
                  console.log("DB Updated")
                  const graphID = db_res.data["graphID"]
                  this.props.handleRowID(graphID)
                  this.props.updateTable();
                  this.props.toggle();
                } else {
                  const db_message = db_res.data["message"];
                  if (db_message.startsWith("Token Error")) {
                    alert(db_message)
                    this.props.handleUserToken(null)
                    this.props.logOutReset();
                  } else {
                    alert("DB Error: " + db_message)
                  }
                }

              }
            } else {
              const gnn__message = gnn_res.data["message"];
              if (gnn__message.startsWith("Token Error")) {
                alert(gnn__message)
                this.props.handleUserToken(null)
                this.props.logOutReset();
              } else {
                alert("GNN Error: " + gnn__message)
              }
            }
          }

        } else {
          const message = res.data["message"];
          if (message.startsWith("Token Error")) {
            alert(message)
            this.props.handleUserToken(null)
            this.props.logOutReset();
          } else {
            alert("RCNN Error: " + message)
          }
        }
      }
    } catch (error) {
      alert("File submission error: Check console for error message");
      console.log(error)
    } finally {
      loader.style.display = "none";
      loader_upload.style.display = 'block';
      loader_button.style.display = 'block';
      loader_gc_choice.style.display = 'block';

      this.setState({
        fileUploadLabel: "Attach a File",
        title: "Insert File to Get Started"
      })
      if (!this.props.open) {
        form.reset();
      }
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
              <FormControlLabel
                control={<Switch name="gcType" onChange={this.handleGcChoice} />}
                label={this.state.gcTitle}
                id='loading-gc-choice'
              />
            </Form.Row>
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
