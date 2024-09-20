import  { useEffect, useRef, useState } from 'react';
import { Button } from "@/components/ui/button";
import { AgGridReact } from 'ag-grid-react';
import AdminMainNav from '@/components/ui/Admin-main-nav';
import { UserNav } from './comp/user-nav';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { useLocalState } from '@/utils/usingLocalStorage';
import GenericTable from './comp/GenericTable';

function AdminStocks() {
    const [stocks, setStocks] = useState([]);
    const [jwt] = useLocalState("", "jwt");
    const gridRef = useRef(null);
    useEffect(() => {
        const fetchStockData = async () => {
            try {
                const requestOptions = {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: "Bearer " + jwt,
                    },
                };
                const response = await fetch('http://localhost:8000/api/stocks/', requestOptions);
                const data = await response.json();
                setStocks(data);
            } catch (error) {
                console.error('Error fetching stock data:', error);
            }
        };

        fetchStockData();
    }, [jwt]);

    const addNewStock = () => {
        const newStock = {
            tempId: new Date().getTime(), // temporary ID for the frontend
            Company_name: "",
            Company_ticker: "",
            Closed_price: "",
            Company_PE: "",
            Company_cash_flow: "",
            Company_dividend: "",
            Company_info:'',

        };
        setStocks([...stocks, newStock]);
    };

    const onCellValueChanged = async (params) => {
        const { data } = params;
        const updateData = { ...data, [params.column.colId]: params.newValue };

        if (data.stock_id) {
            // Existing stock
            try {
                const response = await fetch(`http://localhost:8000/api/stocks/${data.stock_id}`, {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${jwt}`,
                    },
                    body: JSON.stringify(updateData)
                });
                if (!response.ok) {
                const errorData = await response.json(); // Assuming the server sends back JSON with error details
                throw new Error(`Failed to create new transaction: ${JSON.stringify(errorData)}`);
            }
                const updatedData = await response.json();
                setStocks(currentStocks =>
                    currentStocks.map(stock => stock.stock_id === data.stock_id ? { ...stock, ...updatedData } : stock)
                );
            } catch (error) {
                console.error('Error updating stock:', error);
            }
        } else {
            // New stock
            console.log("Saving new stock:", updateData);
            try {
                const response = await fetch(`http://localhost:8000/api/stocks/`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${jwt}`,
                    },
                    body: JSON.stringify(updateData)
                });
                if (!response.ok) {
                    const errorData = await response.json(); // Assuming the server sends back JSON with error details
                    throw new Error(`Failed to create new transaction: ${JSON.stringify(errorData)}`);
                }
                const newStockData = await response.json();
                
                setStocks(currentStocks =>
                    currentStocks.map(stock => stock.tempId === data.tempId ? { ...stock, ...newStockData } : stock)
                );
            } catch (error) {
                console.error('Error saving new stock:', error);
            }
        }
    };
    const deleteSelectedstocks = async () => {
        const selectedNodes = gridRef.current.api.getSelectedNodes();
        const selectedIDs = selectedNodes.map(node => node.data.stock_id);
        const response = await fetch(`http://localhost:8000/api/stocks/admin`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${jwt}`,
            },
            body: JSON.stringify({ stocks_ids: selectedIDs })
        });
        if (!response.ok) {
            const errorData = await response.json(); // Assuming the server sends back JSON with error details
            throw new Error(`Failed to create new transaction: ${JSON.stringify(errorData)}`);
        }
        
            const deleteResponse = await response.json();
            console.log(deleteResponse.message);
            setStocks(prevTransaction => prevTransaction.filter(t => !selectedIDs.includes(t.stock_id)));
    };

    return (
        <>
            <div className="flex flex-col bg-gray-100 shadow-md  dark:bg-gray-900 ">
            <nav className=" navbar   bg-gray-200 shadow-md dark:bg-gray-950 flex justify-between items-center p-4 border-b">
                    <AdminMainNav  className="ml-12 dark:text-white" />
                    <UserNav className="mr-14-12 dark:text-white" />
                </nav>
                <main className="content" >
                <div className='flex flex-wrap'>           <Card className="justify-center m-16 w-[1352px]">
                    <CardHeader>
                        <div className='flex flex-row'>
                            <Button className='flex flex-col mx-7 m-2' onClick={addNewStock}>Add New Stock</Button>
                            <Button className='flex flex-col mx-7 m-2 bg-red-500' onClick={deleteSelectedstocks}>Delete Selected</Button>
                        </div>
                    </CardHeader>
                    <CardContent>
                        <div className="ag-theme-quartz" style={{ height: 540, width: 1260 }}>
                            <AgGridReact
                                rowData={stocks}
                                columnDefs={[
                                    { field: "stock_id", checkboxSelection: true, headerCheckboxSelection: true },
                                    { field: "Company_name", editable: true },
                                    { field: "Company_ticker", editable: true },
                                    { field: "Closed_price", editable: true },
                                    { field: "Company_PE", editable: true },
                                    { field: "Company_cash_flow", editable: true },
                                    { field: "Company_dividend", editable: true }
                                ]}
                                ref={gridRef}
                                autoSizeStrategy={{ type: 'fitCellContents' }}
                                pagination={true}
                                paginationPageSize={10}
                                rowSelection="multiple"
                                paginationPageSizeSelector={[10, 20, 50, 100]}
                                onCellValueChanged={onCellValueChanged}
                            />
                        </div>
                    </CardContent>
                </Card>
          
                <GenericTable
                                url='http://localhost:8000/api/queries/customers/most-stock-transactions'
                                title="TOP CUSTOMERS"
                                columnDefs={[
                                    { field: "username" },
                                    { field: "email" },
                                    { field: "total_transactions" },
                                    { field: "agent_name" },

                                    { field: "agent_level" },

                                ]}
                                height={490}
                                width={800}
                                pagination={true}
                            />
                </div>
 
                </main>
            </div>
        </>
    );
}

export default AdminStocks;
