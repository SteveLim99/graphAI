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

    handleShowModalButton = (e, arr, ent, nx, pred, probs, context, id) => {
        e.preventDefault();
        this.props.handleImgChanges(arr, ent, nx);
        this.props.handlePredictionChanges(pred, probs[0], probs[1], context)
        this.props.handleIsUpload(false);
        this.props.handleRowID(id);
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
                title: "Graph Type",
                dataIndex: "files_gtype",
                sorter: (a, b) => a.files_gtype.length - b.files_gtype.length,
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