import React, { Component } from "react";
import styled from "styled-components";

const Styles = styled.div`
.modal_content {
    background-color: white;
    position: absolute;
    border-radius: 25px;
    position: relative;
    margin: 0 auto;
  }

  .modal {
    width: 100%;
    height: 100%;
    top: 0;
    position: absolute;
    background-color: rgba(22,22,22,0.5);
  }
`;

export default class PopUp extends Component {
    handleClick = () => {
        this.props.toggle();
    };
    render() {
        return (
            <Styles>
                <div className="modal">
                    <div className="modal_content">
                        <span className="close" onClick={this.handleClick}>&times;    </span>
                        <p>I'm A Pop Up!!!</p>
                    </div>
                </div>
            </Styles>
        );
    }
}