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
      networkx_img: ""
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

  render() {
    return (
      <div>
        <div className="App">
          <header className="App-header" style={{ backgroundImage: `url(${background})` }}>
            <NavBar></NavBar>
            <FileUpload
              toggle={this.toggleOpen}
              open={this.state.open}
              handleImgChanges={this.handleImgChanges}>
            </FileUpload>
            <PopUp
              show={this.state.open}
              onHide={this.toggleOpen}
              arrow_img={this.state.arrow_img}
              entity_img={this.state.entity_img}
              networkx_img={this.state.networkx_img}>
            </PopUp>
          </header>
        </div>
      </div >
    );
  }
}

export default App;
