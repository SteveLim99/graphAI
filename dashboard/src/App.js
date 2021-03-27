import './App.css';
import React, { Component } from "react";
import { FileUpload } from "./components/FileUpload";
import { PopUp } from "./components/PopUp";
import 'bootstrap/dist/css/bootstrap.min.css';
import { NavBar } from "./components/Navbar"
import background from "./images/background.png";
import { Button } from 'react-bootstrap';

class App extends Component {
  constructor() {
    super();
    this.state = {
      open: false,
      images: [],
    }
  }

  toggleOpen = () => {
    this.setState({
      open: !this.state.open
    });
  };

  render() {
    return (
      <div>
        <div className="App">
          <header className="App-header" style={{ backgroundImage: `url(${background})` }}>
            <NavBar></NavBar>
            <FileUpload toggle={this.toggleOpen} open={this.state.open}></FileUpload>
            <Button onClick={this.toggleOpen}>open modal</Button>
            <PopUp show={this.state.open} onHide={this.toggleOpen}></PopUp>

          </header>
        </div>
      </div>
    );
  }
}

export default App;
