import './App.css';
import React, { Component } from "react";
import { FileUpload } from "./components/FileUpload";
import { PopUp } from "./components/PopUp";
import 'bootstrap/dist/css/bootstrap.min.css';
import { NavBar } from "./components/Navbar"
import { DBTable } from "./components/DBTable";
import background from "./images/background.png";
import ArrowDropDownCircleOutlinedIcon from '@material-ui/icons/ArrowDropDownCircleOutlined';
import IconButton from '@material-ui/core/IconButton';
import EjectOutlinedIcon from '@material-ui/icons/EjectOutlined';
import axios from "axios";

class App extends Component {
  constructor() {
    super();
    this.state = {
      open: false,
      arrow_img: "",
      entity_img: "",
      networkx_img: "",
      prediction: "",
      prob_0: "",
      prob_1: "",
      content: "",
      isUpload: true,
      files: [],
      viewPast: false
    }
  }

  getDBFiles = async () => {
    var db_files = []

    try {
      var res = await axios.get("/db/dbConnect");

      if (res.status === 200) {
        const db_files_id = res.data["files_id"]
        const db_files_name = res.data["files_name"]
        const db_files_arr = res.data["files_arr"]
        const db_files_ent = res.data["files_ent"]
        const db_files_nx = res.data["files_nx"]
        const db_files_gtype = res.data["files_gtype"]
        const db_files_probs = res.data["files_probs"]
        const db_files_context = res.data["files_context"]

        for (var i = 0; i < db_files_id.length; i++) {
          var file = {
            "files_id": db_files_id[i],
            "files_name": db_files_name[i],
            "files_arr": db_files_arr[i],
            "files_ent": db_files_ent[i],
            "files_nx": db_files_nx[i],
            "files_context": db_files_context[i],
            "files_gtype": db_files_gtype[i],
            "files_probs": db_files_probs[i]
          }
          db_files.push(file)
        }

      }
    } catch (error) {
      console.log(error)
      alert("DB Fetching error, check console for error message");
    } finally {
      return db_files;
    }
  };

  toggleOpen = () => {
    this.setState({
      open: !this.state.open
    });
  };

  handleImgChanges = (arr, ent, nx) => {
    this.setState({
      arrow_img: "data:image/png;base64," + arr,
      entity_img: "data:image/png;base64," + ent,
      networkx_img: "data:image/png;base64," + nx
    })
  };

  handlePredictionChanges = (pred, p0, p1, content) => {
    var float_p0 = parseFloat(p0);
    var float_p1 = parseFloat(p1);

    if (float_p0 >= 1) {
      float_p0 = 100
      float_p1 = 0
    } else if (float_p1 >= 1) {
      float_p1 = 100
      float_p0 = 0
    } else {
      float_p1 = Math.round(float_p1 * 100)
      float_p0 = Math.round(float_p0 * 100)
    }
    this.setState({
      prediction: pred,
      prob_0: float_p0,
      prob_1: float_p1,
      content: content
    })
  }

  handleIsUpload = (bool) => {
    this.setState({
      isUpload: bool
    })
  }

  updateTable = async () => {
    if (!this.state.viewPast) {
      this.setState({
        files: await this.getDBFiles(),
        viewPast: !this.state.viewPast
      });
    } else {
      this.setState({
        viewPast: !this.state.viewPast
      });
    }
  }

  render() {
    return (
      <div>
        <div className="App">
          <header className="App-header" style={{ backgroundImage: `url(${background})` }}>
            <NavBar></NavBar>
            <FileUpload
              toggle={this.toggleOpen}
              open={this.state.open}
              handleImgChanges={this.handleImgChanges}
              handlePredictionChanges={this.handlePredictionChanges}
              handleIsUpload={this.handleIsUpload}
              updateTable={this.updateTable}>
            </FileUpload>
            <IconButton
              onClick={this.updateTable}
              color="inherit"
            >
              {this.state.viewPast ?
                <EjectOutlinedIcon fontSize="large" />
                :
                <ArrowDropDownCircleOutlinedIcon fontSize="large" />
              }
            </IconButton>
            <PopUp
              show={this.state.open}
              onHide={this.toggleOpen}
              arrow_img={this.state.arrow_img}
              entity_img={this.state.entity_img}
              networkx_img={this.state.networkx_img}
              prediction={this.state.prediction}
              prob_0={this.state.prob_0}
              prob_1={this.state.prob_1}
              content={this.state.content}
              isUpload={this.state.isUpload}>
            </PopUp>
            {this.state.viewPast ?
              <DBTable
                toggle={this.toggleOpen}
                open={this.state.open}
                onHide={this.toggleOpen}
                handleImgChanges={this.handleImgChanges}
                docs={this.state.files}
                handlePredictionChanges={this.handlePredictionChanges}
                handleIsUpload={this.handleIsUpload}>
              </DBTable>
              :
              null
            }
          </header>
        </div>
      </div >
    );
  }
}

export default App;
