import './App.css';
import React, { Component } from "react";
import { FileUpload } from "./components/FileUpload";
import { PopUp } from "./components/PopUp";
import 'bootstrap/dist/css/bootstrap.min.css';
import { NavBar } from "./components/Navbar"
import background from "./images/background.png";

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
      prob_1: ""
    }
  }

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

  handlePredictionChanges = (pred, p0, p1) => {
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
      prob_1: float_p1
    })
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
            <PopUp
              show={this.state.open}
              onHide={this.toggleOpen}
              arrow_img={this.state.arrow_img}
              entity_img={this.state.entity_img}
              networkx_img={this.state.networkx_img}
              prediction={this.state.prediction}
              prob_0={this.state.prob_0}
              prob_1={this.state.prob_1}>
            </PopUp>
          </header>
        </div>
      </div >
    );
  }
}

export default App;
