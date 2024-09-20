import { useState } from 'react';
import { useLocalState } from '@/utils/usingLocalStorage';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AgGridReact } from 'ag-grid-react';
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-quartz.css";
import PropTypes from 'prop-types'
import useFetchDataWithSetter from '@/hooks/datafetch';

function GenericTable(props) {
    const [data, setData] = useState([]);
    const [jwt] = useLocalState("", "jwt");

    useFetchDataWithSetter({
        url: props.url,
        method: 'GET',
        jwt,
        setData: setData 
    });

    return (
        <Card className={`justify-center m-16 h-[${props.height+2}] w-[${props.width+4}] dark:text-white`}>
            <CardHeader>
                <CardTitle className="text-3xl font-bold font-mono md:text-left transition-colors hover:text-primary">
                    {props.title}
                </CardTitle>
            </CardHeader>
            <CardContent>
                <div className={`ag-theme-quartz`} style={{ height: props.height, width: props.width }}>
                    <AgGridReact
                        rowData={data}
                        columnDefs={props.columnDefs}
                        autoSizeStrategy={{ type: 'fitCellContents' }}
                        pagination={props.pagination}
                        paginationPageSize={10}
                        rowSelection="multiple"
                        paginationPageSizeSelector={[10, 20, 50, 100]}
                    />
                </div>
            </CardContent>
        </Card>
    );
}
GenericTable.propTypes = {
    height: PropTypes.number.isRequired,
    width: PropTypes.number.isRequired,
    title: PropTypes.string.isRequired,
    columnDefs: PropTypes.array.isRequired,
    pagination:PropTypes.bool,
    url:PropTypes.string
}
export default GenericTable;
