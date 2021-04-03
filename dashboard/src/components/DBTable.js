import React, { Component } from "react";
import { Table } from 'antd';
import "antd/dist/antd.css";
import styled from "styled-components";
import Button from '@material-ui/core/Button';

const Styles = styled.div`

  .table-container {
      top: 30vh;
      background-color: #FAFAFA;
      padding: 0.25%;
  }
`;

export class DBTable extends Component {

    handleShowModalButton = (e, arr, ent, nx) => {
        e.preventDefault();
        this.props.handleImgChanges(arr, ent, nx);
        this.props.handlePredictionChanges("test", 0, 1, "test")
        this.props.toggle();
    }

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
                title: "Toggle Modal",
                key: 'action',
                render: (text, record) => (
                    <Button
                        variant="outlined"
                        color="default"
                        size="small"
                        onClick={(e) => { this.handleShowModalButton(e, record.files_arr, record.files_ent, record.files_nx) }}
                    >
                        Load Modal
                    </Button>
                ),
            }
        ];
        return (
            <Styles>
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