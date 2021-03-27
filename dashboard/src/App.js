import './App.css';
import React, { Component } from "react";
import { FileUpload } from "./components/FileUpload";
import PopUp from "./components/PopUp";
import 'bootstrap/dist/css/bootstrap.min.css';
import { NavBar } from "./components/Navbar"
import background from "./images/background.png";

class App extends Component {
  state = {
    open: false,
    images: []
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
            <FileUpload toggle={this.toggleOpen}></FileUpload>
            <PopUp toggle={this.togglePop} />
            {this.state.open ? <PopUp toggle={this.togglePop} /> : null}
          </header>
        </div>
      </div>
    );
  }
}

export default App;
