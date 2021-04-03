import './App.css';
import React, { Component } from "react";
import { FileUpload } from "./components/FileUpload";
import { PopUp } from "./components/PopUp";
import 'bootstrap/dist/css/bootstrap.min.css';
import { NavBar } from "./components/Navbar"
import { DBTable } from "./components/DBTable";
import background from "./images/background.png";
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
      files: []
    }
  }

  getDBFiles = () => {
    axios.get("/db/dbConnect")
      .then(res => {
        const db_files_id = res.data["files_id"]
        const db_files_name = res.data["files_name"]
        const db_files_arr = res.data["files_arr"]
        const db_files_ent = res.data["files_ent"]
        const db_files_nx = res.data["files_nx"]
        var db_files = []

        for (var i = 0; i < db_files_id.length(); i++) {
          var file = {
            "files_id": db_files_id[i],
            "files_name": db_files_name[i],
            "files_arr": db_files_arr[i],
            "files_ent": db_files_ent[i],
            "files_nx": db_files_nx[i]
          }
          db_files.push(file)
        }
        return db_files
      })
      .catch(error => {
        console.log(error)
        alert("Error occured when fetching files from DB, check console for error message")
      })
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

  componentDidMount = async () => {
    this.setState({
      files: this.getDBFiles()
    });
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
              handlePredictionChanges={this.handlePredictionChanges}>
            </FileUpload>
            <DBTable
              docs={this.state.files}>
            </DBTable>
            <PopUp
              show={this.state.open}
              onHide={this.toggleOpen}
              arrow_img={this.state.arrow_img}
              entity_img={this.state.entity_img}
              networkx_img={this.state.networkx_img}
              prediction={this.state.prediction}
              prob_0={this.state.prob_0}
              prob_1={this.state.prob_1}
              content={this.state.content}>
            </PopUp>
          </header>
        </div>
      </div >
    );
  }
}

export default App;
