import  { useEffect, useRef, useState } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { useLocalState } from '@/utils/usingLocalStorage';
import AdminMainNav from '@/components/ui/Admin-main-nav';
import { UserNav } from './comp/user-nav';
import { AgGridReact } from 'ag-grid-react';
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-quartz.css";
import GenericTable from './comp/GenericTable';



function AdminCrypto() {
    const [cryptos, setCryptos] = useState([]);
    const [jwt] = useLocalState("", "jwt");
    const gridRef = useRef(null);

    useEffect(() => {
        const fetchCryptoData = async () => {
            try {
                const requestOptions = {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: "Bearer " + jwt,
                    },
                };
                const response = await fetch('http://localhost:8000/api/cryptocurrencies/', requestOptions);
                const data = await response.json();
                setCryptos(data);
            } catch (error) {
                console.error('Error fetching crypto data:', error);
            }
        };

        fetchCryptoData();
    }, [jwt]);

    const addNewCrypto = () => {
        const newCrypto = {
            tempId: new Date().getTime(), // temporary ID for the frontend
            Name: "",
            Symbol: "",
            Market_Cap: "",
            Volume_24h: "",
            Circulating_Supply: ""
        };
        setCryptos([...cryptos, newCrypto]);
    };

    const onCellValueChanged = async (params) => {
        const { data } = params;
        const updateData = { ...data, [params.column.colId]: params.newValue };

        if (data.crypto_id) {
            try {
                const response = await fetch(`http://localhost:8000/api/cryptocurrencies/${data.crypto_id}`, {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${jwt}`,
                    },
                    body: JSON.stringify(updateData)
                });
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(`Failed to update cryptocurrency: ${JSON.stringify(errorData)}`);
                }
                const updatedData = await response.json();
                setCryptos(currentCryptos =>
                    currentCryptos.map(crypto => crypto.crypto_id === data.crypto_id ? { ...crypto, ...updatedData } : crypto)
                );
            } catch (error) {
                console.error('Error updating cryptocurrency:', error);
            }
        } else {
            console.log("Saving new cryptocurrency:", updateData);
            try {
                const response = await fetch(`http://localhost:8000/api/cryptocurrencies/`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${jwt}`,
                    },
                    body: JSON.stringify(updateData)
                });
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(`Failed to save new cryptocurrency: ${JSON.stringify(errorData)}`);
                }
                const newCryptoData = await response.json();
                
                setCryptos(currentCryptos =>
                    currentCryptos.map(crypto => crypto.tempId === data.tempId ? { ...crypto, ...newCryptoData} : crypto)
                );
            } catch (error) {
                console.error('Error saving new cryptocurrency:', error);
            }
        }
    };
    const deleteSelectedcrypto = async () => {
        const selectedNodes = gridRef.current.api.getSelectedNodes();
        const selectedIDs = selectedNodes.map(node => node.data.crypto_id);
        const response = await fetch(`http://localhost:8000/api/cryptocurrencies/admin`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${jwt}`,
            },
            body: JSON.stringify({ crypto_ids: selectedIDs })
        });
        if (!response.ok) {
            const errorData = await response.json(); // Assuming the server sends back JSON with error details
            throw new Error(`Failed to create new transaction: ${JSON.stringify(errorData)}`);
        }
        
            const deleteResponse = await response.json();
            console.log(deleteResponse.message);
            setCryptos(prevTransaction => prevTransaction.filter(t => !selectedIDs.includes(t.crypto_id)));
    };

    return (
        <>
        <div className="flex flex-col bg-gray-100 shadow-md  dark:bg-gray-900 ">
        <nav className=" navbar   bg-gray-200 shadow-md dark:bg-gray-950 flex justify-between items-center p-4 border-b">
                <AdminMainNav className="ml-12 dark:text-white" />
                <UserNav className="mr-12" />
            </nav>
            <main className="content" >
            <Card className="justify-center m-24 w-[1032px]">
                <CardHeader>
                <div className='flex flex-row'>
                    <Button   className='flex flex-col mx-7 m-2' onClick={addNewCrypto}>Add New Crypto</Button>
                    <Button className='flex flex-col mx-7 m-2 bg-red-500 ' onClick={deleteSelectedcrypto} >Delete Selected</Button>
                    </div>
                </CardHeader>
                <CardContent>
                    <div className="ag-theme-quartz" style={{ height: 540, width: 984 }}>
                        <AgGridReact
                            rowData={cryptos}
                            ref={gridRef}
                            columnDefs={[
                                { field: "crypto_id", checkboxSelection: true, headerCheckboxSelection: true  },
                                { field: "Name", editable: true },
                                { field: "Symbol", editable: true },
                                { field: "Last_Close", editable: true },
                                { field: "Market_Cap", editable: true },
                                { field: "Volume_24h", editable: true },
                                { field: "Circulating_Supply", editable: true }
                            ]}
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
                                url='http://localhost:8000/api/queries/customers/most-crypto-transactions'
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
            </main>
        </div>
        </>
    );
}

export default AdminCrypto;
