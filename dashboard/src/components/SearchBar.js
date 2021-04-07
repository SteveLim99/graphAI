import React, { Component } from 'react';
import { DatePicker, Select, Input, Button } from 'antd';
import { Form, Col } from "react-bootstrap";
import SearchIcon from '@material-ui/icons/Search';
import CloseIcon from '@material-ui/icons/Close';
import styled from "styled-components";
import IconButton from '@material-ui/core/IconButton';
const { RangePicker } = DatePicker;
const { Option } = Select;

const Styles = styled.div`
  .collapse-container{
    background-color: #fafafa;
    padding: 0.25px;
    width: 100%;
    height: 50px;
  }

  .collapse-icon{
    fontSize: 12;
    float: right;
    padding-right: 2%;
  }

  .form-container {
    background-color: #fafafa;
    width: 100%;
  }
`;


export class SearchBar extends Component {
    constructor() {
        super()
        this.state = {
            expand: false
        }
    }

    setExpand = () => {
        this.setState({
            expand: !this.state.expand
        });
    }
    render() {
        return (
            <Styles>
                <div className="collapse-container">
                    <IconButton
                        className="collapse-icon"
                        onClick={this.setExpand}
                        color="inherit"
                    >
                        {this.state.expand ?
                            <CloseIcon fontSize='default' color='error' />
                            :
                            <SearchIcon fontSize='default' color='primary' />
                        }
                    </IconButton>
                </div>

                {this.state.expand ?
                    <Form className="form-container">
                        <Form.Row>
                            <Form.Group as={Col} controlId="search-keyword">
                                <Input
                                    style={{ width: 250 }}
                                    placeholder="Enter File Name"
                                    onChange={(e) => { this.props.handleSearchKeyword(e) }}
                                />
                            </Form.Group>
                            <Form.Group as={Col} controlId="search-gType">
                                <Select
                                    placeholder="Select Graph Type"
                                    onSelect={(e) => { this.props.handleSearchSelect(e) }}
                                    allowClear
                                >
                                    <Option value="1">BPNM</Option>
                                    <Option value="2">Swimlane</Option>
                                </Select>
                            </Form.Group>
                            <Form.Group as={Col} controlId="search-date">
                                <RangePicker
                                    onChange={(_, dateString) => { this.props.handleSearchDates(dateString) }}
                                />
                            </Form.Group>
                            <Form.Group as={Col}>
                                <Button type="primary" htmlType="submit">
                                    Search
                                </Button>
                            </Form.Group>
                        </Form.Row>
                    </Form>
                    :
                    null
                }
            </Styles>
        );
    }
}