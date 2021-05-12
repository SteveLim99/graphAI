import React, { Component } from "react";
import { Table } from 'antd';
import "antd/dist/antd.css";
import styled from "styled-components";
import axios from "axios";
import Button from '@material-ui/core/Button';
import { SearchBar } from './SearchBar';
import IconButton from '@material-ui/core/IconButton';
import DeleteForeverRoundedIcon from '@material-ui/icons/DeleteForeverRounded';
import { AlertDialog } from "./AlertDialog"

const Styles = styled.div`

  .table-container {
      top: 30vh;
      background-color: #FAFAFA;
      padding: 0.25%;
  }
`;

export class DBTable extends Component {
    constructor(props) {
        super(props);
        this.state = {
            e: null,
            id: null,
            dialog_open: false,
            dialog: "Are you sure that you want to detele this prediction?"
        }
    }

    handleClose = () => {
        this.setState({
            dialog_open: false,
            e: null,
            id: null
        })
    }

    handleAccept = async () => {
        const { e, id } = this.state
        e.preventDefault();
        this.setState({
            dialog_open: false,
            e: null,
            id: null
        })
        try {
            var endpoint = "db/dbDeleteFile?id=" + id
            endpoint += "&token=" + this.props.user_token
            var res = await axios.post(
                endpoint,
                {}
            )

            if (res.status === 200) {
                const deletedFile = res.data["status"]
                const deletedFileMsg = res.data["message"]

                if (deletedFile === "success") {
                    this.props.resetTable();
                } else {
                    alert(deletedFileMsg);
                    this.props.handleUserToken(null);
                    this.props.logOutReset();
                }

            }
        } catch (error) {
            console.log(error)
            alert("File delete error, check console for error message")
        }
    }

    handleDelete = (e, id) => {
        this.setState({
            dialog_open: true,
            e: e,
            id: id
        })
    }

    handleShowModalButton = (e, arr, ent, nx, pred, probs, context, id) => {
        e.preventDefault();
        this.props.handleImgChanges(arr, ent, nx);
        this.props.handlePredictionChanges(pred, probs[0], probs[1], context)
        this.props.handleRowID(id);
        this.props.toggle();
    }

    // handleDeleteFileButton = async (e, id) => {
    //     e.preventDefault();
    //     try {
    //         var endpoint = "db/dbDeleteFile?id=" + id
    //         endpoint += "&token=" + this.props.user_token
    //         var res = await axios.post(
    //             endpoint,
    //             {}
    //         )

    //         if (res.status === 200) {
    //             const deletedFile = res.data["status"]
    //             const deletedFileMsg = res.data["message"]

    //             if (deletedFile === "success") {
    //                 this.props.resetTable();
    //             } else {
    //                 alert(deletedFileMsg);
    //                 this.props.handleUserToken(null);
    //                 this.props.logOutReset();
    //             }

    //         }
    //     } catch (error) {
    //         console.log(error)
    //         alert("File delete error, check console for error message")
    //     }
    // }

    render() {
        const columns = [
            {
                title: "File ID",
                dataIndex: "files_id",
                sorter: (a, b) => a.files_id - b.files_id,
                ellipsis: true,
                sortDirections: ["descend", "ascend"]
            },
            {
                title: "File Name",
                dataIndex: "files_name",
                sorter: (a, b) => a.files_name.length - b.files_name.length,
                ellipsis: true,
                sortDirections: ["descend", "ascend"]
            },
            {
                title: "Graph Type",
                dataIndex: "files_gtype",
                sorter: (a, b) => a.files_gtype.length - b.files_gtype.length,
                ellipsis: true,
                sortDirections: ["descend", "ascend"]
            },
            {
                title: "Upload Date",
                dataIndex: "files_date",
                sorter: (a, b) => new Date(a.files_date) - new Date(b.files_date),
                ellipsis: true,
                sortDirections: ["descend", "ascend"]
            },
            {
                title: "Toggle Modal",
                key: 'action',
                render: (text, record) => (
                    <Button
                        variant="outlined"
                        color="default"
                        size="small"
                        onClick={(e) => {
                            this.handleShowModalButton(e,
                                record.files_arr,
                                record.files_ent,
                                record.files_nx,
                                record.files_gtype,
                                record.files_probs,
                                record.files_context,
                                record.files_id)
                        }}
                    >
                        Load Modal
                    </Button>

                ),
            },
            {
                title: "Delete Prediction",
                key: 'action',
                render: (record) => (
                    <IconButton
                        className="collapse-icon"
                        color="inherit"
                        onClick={(e) => {
                            this.handleDelete(e, record.files_id)
                        }}
                    >
                        <DeleteForeverRoundedIcon fontSize='default' color='error' />
                    </IconButton>
                )
            }
        ];
        return (
            <Styles>
                <AlertDialog
                    open={this.state.dialog_open}
                    dialog={this.state.dialog}
                    handleClose={this.handleClose}
                    handleAccept={this.handleAccept}>
                </AlertDialog>
                <SearchBar
                    handleSearchKeyword={this.props.handleSearchKeyword}
                    handleSearchSelect={this.props.handleSearchSelect}
                    handleSearchDates={this.props.handleSearchDates}
                    searchTable={this.props.searchTable}
                    resetTable={this.props.resetTable}>
                </SearchBar>
                <Table
                    columns={columns}
                    pagination={{ showSizeChanger: true }}
                    dataSource={this.props.docs}
                    rowKey="files_id"
                    className="table-container"
                />
            </Styles>
        );
    }
}