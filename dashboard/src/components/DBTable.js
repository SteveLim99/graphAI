import React, { Component } from "react";
import { Table, Space } from 'antd';
import "antd/dist/antd.css";
import Button from '@material-ui/core/Button';

export class DBTable extends Component {
    render() {
        const columns = [
            {
                title: "File ID",
                dataIndex: "files_id",
                sorter: (a, b) => a.fileName.length - b.fileName.length,
                ellipsis: true,
                sortDirections: ["descend", "ascend"]
            },
            {
                title: "File Name",
                dataIndex: "files_name",
                sorter: (a, b) => a.fileVersion - b.fileVersion,
                ellipsis: true,
                sortDirections: ["descend", "ascend"]
            },
            {
                title: "Toggle Modal",
                key: 'action',
                render: (text) => (
                    <Space size="middle">
                        <Button
                            variant="outlined"
                            color="default"
                            size="small"
                        >
                            Save
                        </Button>
                    </Space>
                ),
            }
        ];
        return (
            <Table
                columns={columns}
                pagination={{ showSizeChanger: true }}
                dataSource={this.props.docs}
                rowKey="fileName"
            />
        );
    }
}