import { useEffect, useRef, useState } from 'react';
import { Button } from "@/components/ui/button";


import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

import { useLocalState } from '@/utils/usingLocalStorage';
import { UserNav } from './comp/user-nav';


import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { AgGridReact } from 'ag-grid-react';
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-quartz.css";

import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTrigger,
} from "@/components/ui/dialog"

import AdminMainNav from '@/components/ui/Admin-main-nav';
import { DialogClose } from '@radix-ui/react-dialog';
import Select from 'react-select';
import GenericTable from './comp/GenericTable';
import GenericChart from './comp/GenericChart';

function AdminTransactions() {
    const [customers, setCustomers] = useState([]);
    const [customerdata, setCustomerdata] = useState([]);
    const [stocks, setStocks] = useState([]);
    const [AgentData, setAgentData] = useState([]);
    const [transaction, setTransaction] = useState([]);
    const [jwt] = useLocalState("", "jwt");
    const gridRef = useRef(null);
    const [selectedStock, setSelectedStock] = useState(null);
    const [selectedCustomer, setSelectedCustomer] = useState(null);
    const [selectedAgent, setSelectedAgent] = useState(null);
    const [selectedAction, setSelectedAction] = useState(null);
    const [transactionId, setTransactionId] = useState("");  
    const [volume, setVolume] = useState("");
    const [colDefs] = useState([
        { field: 'transaction_id', checkboxSelection: true, headerCheckboxSelection: true },
        // { field: 'customer_id' },
        { field: "customer_name", filter: true, floatingFilter: true
        },
        {     field: "agent_name" , filter: true, floatingFilter: true
        },
        { field: "ticket" , filter: true, floatingFilter: true },
        { field: "volume", editable: true },
        { field: "each_cost" },
        { field: "action",  
        cellEditor: 'agSelectCellEditor',
        cellEditorParams: {
            values: ['buy', 'sell'],
        },editable: true , filter: true, floatingFilter: true },
        { field: "date", editable: true , filter: true, floatingFilter: true }
    ])
    console.log(customers);
    const fetchAgents = async () => {
        const data = await fetch('http://localhost:8000/api/agents/', {
            headers: { "Authorization": `Bearer ${jwt}` }
        }).then(res => res.json());
        setAgentData(data.map(agent => ({ label: agent.name, value: agent.agent_id })));
    };
    const fetchStocks = async () => {
        // Fetch stocks logic
        const data = await fetch('http://localhost:8000/api/stocks', {
            "Content-Type": "application/json",
            headers: { "Authorization": `Bearer ${jwt}` }
        }).then(res => res.json());
        setStocks(data.map(stock => ({ label: stock.Company_ticker, value: stock.stock_id, cp:stock.Closed_price })));
    };
    const fetchCustomer = async () => {
        // Fetch stocks logic
        const data = await fetch('http://localhost:8000/api/customers/admin', {
            "Content-Type": "application/json",
            headers: { "Authorization": `Bearer ${jwt}` }
        }).then(res => res.json());
        setCustomerdata(data.map(customer => ({ label: customer.username, value: customer.customer_id })));
    };

    const fetchtransationData = async () => {
        try {
            const requestOptions = {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: "Bearer " + jwt,
                },
            };

            const response = await fetch('http://localhost:8000/api/transactions/adminpro/', requestOptions);
            const data = await response.json();
            setTransaction(data);
        } catch (error) {
            console.error('Error fetching setTransaction data:', error);
        }
    };
    const fetchCustomerData = async () => {
        try {
            const requestOptions = {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: "Bearer " + jwt,
                },
            };

            const response = await fetch('http://localhost:8000/api/customers/admin', requestOptions);
            const data = await response.json();
            setCustomers(data);
            const usernames = data.map(customer => customer.username);
            setCustomerUsernames(usernames);

        } catch (error) {
            console.error('Error fetching setTransaction data:', error);
        }
    };
    useEffect(() => {
        fetchAgents();
        fetchStocks();
        fetchtransationData();
        fetchCustomerData();
        fetchCustomer();
        

    }, [jwt]);


    const closeDialog = () => {
        setSelectedStock("");
        setSelectedAction("");
        setSelectedCustomer("");
        setSelectedAgent("");
        setVolume("");
        
    };
    const action =[
        {label: 'sell', value: 0},
        
        {label: 'buy', value: 1}
    ]
    async function updateTransactionData(transaction) {
        const updateData = {
            stock_id: transaction.stock_id,
            agent_id: transaction.agent_id,
            ticket: transaction.ticket,
            volume: transaction.volume,
            each_cost: transaction.each_cost,
            action: transaction.action,
            customer_id:transaction.customer_id
        };
        try {
            const response = await fetch(`http://localhost:8000/api/transactions/admin/${transaction.transaction_id}`, {
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
            const updatedTransactionData = await response.json();
            setTransaction(prevTransaction =>
                prevTransaction.map(t => t.transaction_id === transaction.transaction_id ? { ...t, ...updatedTransactionData } : t)
            );

        } catch (error) {
            console.error('Error updating transaction:', error);
        }
    }
    const onCellValueChanged = params => {
        const { field, data } = params;
        const updatedTransaction = {
            ...data,
            [field]: params.newValue,
        };
        updateTransactionData(updatedTransaction);
    }; 
    console.log(selectedCustomer);
    const deleteSelectedtransactions = async () => {
        const selectedNodes = gridRef.current.api.getSelectedNodes();
        const selectedIDs = selectedNodes.map(node => node.data.transaction_id);
        const response = await fetch(`http://localhost:8000/api/transactions/admin`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${jwt}`,
            },
            body: JSON.stringify({ transaction_ids: selectedIDs })
        });
        if (response.ok) {
            const deleteResponse = await response.json();
            console.log(deleteResponse.message);
            setTransaction(prevTransaction => prevTransaction.filter(t => !selectedIDs.includes(t.transaction_id)));
        } else {
            console.error('Failed to delete selected customers.');
        }
    };





    const handleSelectChangestock = selectedOption => {
        setSelectedStock(selectedOption);
    };
    const handleSelectChangecustomer = selectedOption => {
        setSelectedCustomer(selectedOption);
    };
    const handleSelectChangeagent = selectedOption => {
        setSelectedAgent(selectedOption);
    };
    const handleSelectAction = selectedOption => {
        setSelectedAction(selectedOption);
    };

    async function saveNewTransaction(transaction) {
        const CreateData = {
            stock_id: transaction.stock_id,
            agent_id: transaction.agent_id,
            ticket: transaction.ticket,
            volume: transaction.volume,
            each_cost: transaction.each_cost,
            action: transaction.action,
            customer_id: transaction.customer_id
        };
        try {
            const response = await fetch('http://localhost:8000/api/transactions/admin', {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${jwt}`,
                },
                body: JSON.stringify(CreateData)
            });
    
            if (!response.ok) {
                const errorData = await response.json(); // Assuming the server sends back JSON with error details
                throw new Error(`Failed to create new transaction: ${JSON.stringify(errorData)}`);
            }
    
            const newTransactionData = await response.json();
            setTransaction(prevTransactions => [...prevTransactions, newTransactionData]);
        } catch (error) {
            console.error('Error creating new transaction:', error);
            // Optionally, you can update UI here to show error messages.
            // Example: setError(error.message);
        }
    }
    // useEffect(() => {
    //     const fetchTransactionData = async () => {
    //         try {
    //             const response = await fetch(`http://localhost:8000/api/transactions/admin/${transactionId}`, {
    //                 method: "GET",
    //                 headers: {
    //                     "Content-Type": "application/json",
    //                     Authorization: `Bearer ${jwt}`,
    //                 },
    //             });
    
    //             if (response.ok) {
    //                 const data = await response.json();
    //                 setSelectedStock(data.stock_id);
    //                 selectedCustomer(data.customer_id);
    //                 selectedAction(data.action);
    //                 selectedAgent(data.agent_id);
    //                 setVolume(data.volume)
    //                 // Set other fields as needed
    //             } else {
    //                 console.error('Failed to fetch customer details');
    //             }
    //         } catch (error) {
    //             console.error('Error fetching customer details:', error);
    //         }
    //     };
    
    //     if (transactionId) {
    //         fetchTransactionData();
    //     }
    // }, [transactionId, jwt]);



    const handleSubmit = async (e) => {
        e.preventDefault();
        if (transactionId) {
            updateTransactionData( {
                transaction_id:transactionId,
                stock_id: selectedStock.value,
                agent_id: selectedAgent.value,
                ticket: selectedStock.label,
                volume: volume,
                each_cost: selectedStock.cp,
                action: selectedAction.label,
                customer_id:selectedCustomer.value
            });
        } else {
            saveNewTransaction({
                stock_id: selectedStock.value,
                agent_id: selectedAgent.value,
                ticket: selectedStock.label,
                volume: volume,
                each_cost: selectedStock.cp,
                action: selectedAction.label,
                customer_id:selectedCustomer.value
            });
        }
    };
    const topAgentsChartOptions = {
        transformData: (data) => ({
          labels: data.map((agent) => agent.agent_name),
          datasets: [
            {
              label: 'Total Cost',
              data: data.map((agent) => agent.total_cost),
              backgroundColor: 'rgba(54, 162, 235, 0.5)',
              borderColor: 'rgba(54, 162, 235, 1)',
              borderWidth: 1,
            },
          ],
        }),
        options: {
          scales: {
            y: {
              beginAtZero: true,
            },
          },
        },
      };


    const topCustomersChartOptions = {
        transformData: (fetchedData) => ({
          labels: fetchedData.map((customer) => customer.username),
          datasets: [
            {
              label: 'Total Cost',
              data: fetchedData.map((customer) => customer.total_cost),
              backgroundColor: 'rgba(53, 162, 235, 0.5)',
              borderColor: 'rgba(53, 162, 235, 1)',
              borderWidth: 1,
            }
          ],
        }),
        options: {
          scales: {
            y: {
              beginAtZero: true,
            },
          },
          indexAxis: 'y', // Optional: if you want a horizontal bar chart
        },
      };



console.log(selectedStock)
    return (
        <>
             <div className="flex flex-col bg-gray-100 shadow-md  dark:bg-gray-900 ">
            <nav className=" navbar   bg-gray-200 shadow-md dark:bg-gray-950 flex justify-between items-center p-4 border-b">
                    <AdminMainNav className="ml-12 dark:text-white" />
                    <UserNav className="mr-14-12" />
                </nav>

                
                <main className="content" >
                <div className='flex flex-wrap'>
                    <Card className="justify-center m-24 w-[1162px]" >
                        <CardHeader><div className='flex'><Button className='  flex flex col mx-7 m-2 bg-red-500' onClick={deleteSelectedtransactions}>Delete Selected</Button>
                        <Dialog>
                                <DialogTrigger asChild>
                                    <Button variant="" className='mt-2'>Add or Edit Customer</Button>
                                </DialogTrigger>
                                <DialogContent>
                                    <DialogHeader>
                                    </DialogHeader>
                                    <Card className='w-[460px]  dark:text-white'>


                                        <CardHeader className="space-y-1">
                                            <CardTitle className="text-2xl">Create an account</CardTitle>
                                            <CardDescription>
                                                Enter your detials below to create your account
                                            </CardDescription>
                                        </CardHeader>

                                        <CardContent as="form"  onSubmit={handleSubmit} className="grid gap-4">
                                        <div className="grid gap-2">
    <Label htmlFor="id">ID</Label>
    <Input id="id" name="id" type="text" placeholder="Leave empty to add new" value={transactionId}
        onChange={(e) => setTransactionId(e.target.value)} />
</div>

                                            <Label htmlFor="stock">Stock</Label>
                            <Select
                                inputId="stock"
                                value={selectedStock}
                                onChange={handleSelectChangestock}
                                options={stocks}
                                isClearable={true}
                                isSearchable={true}
                                placeholder="Select or type to search"
                            />
                             <Label htmlFor="stock">Customer</Label>
                            <Select
                                inputId="customer"
                                value={selectedCustomer}
                                onChange={handleSelectChangecustomer}
                                options={customerdata}
                                isClearable={true}
                                isSearchable={true}
                                placeholder="Select or type to search"
                            />

                            <Label htmlFor="stock">Agent</Label>
                            <Select
                                inputId="Agent"
                                value={selectedAgent}
                                onChange={handleSelectChangeagent}
                                options={AgentData}
                                isClearable={true}
                                isSearchable={true}
                                placeholder="Select or type to search"
                            />                                       
                            <div className="grid gap-2">
    <Label htmlFor="id">Volume</Label>
    <Input id="vilume" name="volume" type="number" placeholder="" value={volume}
        onChange={(e) => setVolume(e.target.value)} />
</div>
<Label htmlFor="id">Action</Label>
<Select
                                inputId="customer"
                                value={selectedAction}
                                onChange={handleSelectAction}
                                options={action}
                                isClearable={true}
                                isSearchable={true}
                                placeholder="Select or type to search"
                            />         
                            
                            
                            
                             </CardContent>


                                        <CardFooter className="flex flex-row gap-4">
                                            <Button type="submit" onClick={handleSubmit} className="w-full">Add account</Button>
                                            <DialogClose asChild >
            <Button type="button" onClick={closeDialog} variant="secondary">
              Close
            </Button>
          </DialogClose>
                                        </CardFooter>
                                    </Card>
                                </DialogContent>
                        
          
                            </Dialog>
                        
                        </div></CardHeader>
                        <CardContent >
                        <div
                            className="ag-theme-quartz"
                            style={{ height: 590, width: 1100 }}
                        >      
                            <AgGridReact
                                rowData={transaction}
                                columnDefs={colDefs}
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
                    <div className='flex flex-row'>
                    <GenericTable
                                url='http://localhost:8000/api/queries/customers/top-stock-transactions'
                                title="TOP CUSTOMERS"
                                columnDefs={[
                                    { field: "username" },
                                    { field: "email" },
                                    { field: "total_cost" },
                                    { field: "agent_name" },

                                    { field: "agent_level" },

                                ]}
                                height={490}
                                width={600}
                                pagination={true}
                            />
 <GenericChart
      url='http://localhost:8000/api/queries/customers/top-stock-transactions'
      chartOptions={topCustomersChartOptions}
      title="Top Customers"
    />
    </div>
<GenericTable
                                url='http://localhost:8000/api/queries/agents/top-stock-transactions'
                                title="TOP AGENTs"
                                columnDefs={[
                                    { field: "agent_id" },
                                    { field: "agent_name" },
                                    { field: "agent_level" },
                                    { field: "total_cost" },

                                ]}
                                height={490}
                                width={600}
                                pagination={true}
                            />
                                            <GenericChart 
  url='http://localhost:8000/api/queries/agents/top-stock-transactions' 
  chartOptions={topAgentsChartOptions} 
  title="Top Agents" 
/>

<div className='flex flex-row'>
                    <GenericTable
                                url='http://localhost:8000/api/queries/customers/top-crypto-transactions'
                                title="TOP CUSTOMERS based on crypto"
                                columnDefs={[
                                    { field: "username" },
                                    { field: "email" },
                                    { field: "total_cost" },
                                    { field: "agent_name" },

                                    { field: "agent_level" },

                                ]}
                                height={490}
                                width={600}
                                pagination={true}
                            />
 <GenericChart
      url='http://localhost:8000/api/queries/customers/top-crypto-transactions'
      chartOptions={topCustomersChartOptions}
      title="Top Customers"
    />
    </div>
<GenericTable
                                url='http://localhost:8000/api/queries/agents/top-crypto-transactions'
                                title="TOP AGENTs based on crypto"
                                columnDefs={[
                                    { field: "agent_id" },
                                    { field: "agent_name" },
                                    { field: "agent_level" },
                                    { field: "total_cost" },

                                ]}
                                height={490}
                                width={600}
                                pagination={true}
                            />
                                            <GenericChart 
  url='http://localhost:8000/api/queries/agents/top-crypto-transactions' 
  chartOptions={topAgentsChartOptions} 
  title="Top Agents" 
/>

                          </div></main>
            </div>
            

        </>
    );
}
export default AdminTransactions;


