import  { useEffect, useRef, useState } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useLocalState } from '@/utils/usingLocalStorage';
import { UserNav } from './comp/user-nav';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';

 "@/components/ui/dropdown-menu"

import { AgGridReact } from 'ag-grid-react'; // AG Grid Component
import "ag-grid-community/styles/ag-grid.css"; // Mandatory CSS required by the grid

import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTrigger,
} from "@/components/ui/dialog"
import AdminMainNav from '@/components/ui/Admin-main-nav';

import { DialogClose } from '@radix-ui/react-dialog';
import GenericTable from './comp/GenericTable';
import GenericChart from './comp/GenericChart';

function AdminCustomers() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [customerId, setCustomerId] = useState("");  
    const [username, setUsername] = useState("");
    const [balance, setBalance] = useState("");
    const [customer, setcustomer] = useState([]);
    const [jwt] = useLocalState("", "jwt");
    const gridRef = useRef(null);
    useEffect(() => {
        const fetchtransationData = async () => {
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
                setcustomer(data);
            } catch (error) {
                console.error('Error fetching setTransaction data:', error);
            }
        };
        


        fetchtransationData();
    }, [jwt]);
    const closeDialog = () => {
        setUsername("");
        setEmail("");
        setPassword("");
        setBalance("");
        setCustomerId("");
        
    };
    useEffect(() => {
        const fetchCustomerData = async () => {
            try {
                const response = await fetch(`http://localhost:8000/api/customers/admin/${customerId}`, {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${jwt}`,
                    },
                });
    
                if (response.ok) {
                    const data = await response.json();
                    setUsername(data.username);
                    setEmail(data.email);
                    setPassword(data.hashed_password);
                    setBalance(data.balance);
                    // Set other fields as needed
                } else {
                    console.error('Failed to fetch customer details');
                }
            } catch (error) {
                console.error('Error fetching customer details:', error);
            }
        };
    
        if (customerId) {
            fetchCustomerData();
        }
    }, [customerId, jwt]);

    async function saveNewCustomer(customer) {
        const createData = {
            username: customer.username,
            email: customer.email,
            hashed_password: customer.hashed_password,
            balance: customer.balance,
            role: customer.role,
            net_stock: customer.net_stock,
        };
        try {
            const response = await fetch('http://localhost:8000/api/auth/register', {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(createData)
            });
            if (!response.ok) throw new Error('Failed to create new customer');
    
            const newCustomerData = await response.json();
            setcustomer(prevCustomers => [...prevCustomers, newCustomerData]);
        } catch (error) {
            console.error('Error creating new customer:', error);
        }
    }
    

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (customerId) {
            updateCustomerData({
                customer_id: customerId,
                username,
                email,
                hashed_password: password,
                balance,
                net_stock: 0,
                role: "customer",
            });
        } else {
            saveNewCustomer({
                username,
                email,
                hashed_password: password,
                balance,
                role: "customer",
                net_stock: 0,
            });
        }
    };


    // console.log(customer);

    function onCellValueChanged(params) {
        const { field, data } = params;
        const updatedRecord = { ...data, [field]: params.newValue };
        if (!updatedRecord.customer_id) {

            saveNewCustomer(updatedRecord);
        } else {
            updateCustomerData(updatedRecord);
        }
    }


    async function updateCustomerData(customer) {
        const updateData = {
            username: customer.username,
            email: customer.email,
            hashed_password: customer.hashed_password, // Ensure this value is managed securely
            balance: customer.balance,
            net_stock: customer.net_stock,
            role: customer.role // Assuming role is not editable but must be sent
        };
        try {
            const response = await fetch(`http://localhost:8000/api/customers/admin/${customer.customer_id}`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${jwt}`,
                },
                body: JSON.stringify(updateData)
            });
            if (!response.ok) throw new Error('Failed to update customer');

            const updatedCustomerData = await response.json();
            setcustomer(prevCustomers =>
                prevCustomers.map(c => c.customer_id === customer.customer_id ? { ...c, ...updatedCustomerData } : c)
            );
        } catch (error) {
            console.error('Error updating customer:', error);
        }
    }
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



    const deleteSelectedCustomers = async () => {
        const selectedNodes = gridRef.current.api.getSelectedNodes();
        const selectedIDs = selectedNodes.map(node => node.data.customer_id);
        const response = await fetch(`http://localhost:8000/api/customers/admin`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${jwt}`,
            },
            body: JSON.stringify({ customer_ids: selectedIDs })
        });
        if (response.ok) {
            const deleteResponse = await response.json();
            console.log(deleteResponse.message);
            setcustomer(prevCustomers => prevCustomers.filter(c => !selectedIDs.includes(c.customer_id)));
        } else {
            console.error('Failed to delete selected customers.');
        }
    };
    return (
        <>
            <div className="flex flex-col bg-gray-100 shadow-md  dark:bg-gray-900 ">
                <nav className=" navbar   bg-gray-200 shadow-md dark:bg-gray-950 flex justify-between items-center p-4 border-b">
                    <AdminMainNav className="ml-12 dark:text-white" />
                    <UserNav className="mr-14-12 dark:text-white" />
                </nav>
                <main className="content" >
                <div className='flex flex-wrap'>  
                    <Card className="justify-center m-24  w-[765px] dark:text-white" >
                        <CardHeader> <div className='flex flex-row '><Button className=' flex flex col mx-7 m-2 bg-red-500' onClick={deleteSelectedCustomers}>Delete Selected</Button>
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

                                        <CardContent as="form" onSubmit={handleSubmit} className="grid gap-4">
                                        <div className="grid gap-2">
    <Label htmlFor="id">ID</Label>
    <Input id="id" name="id" type="text" placeholder="Leave empty to add new" value={customerId}
        onChange={(e) => setCustomerId(e.target.value)} />
</div>
                                            <div className="grid gap-2">
                                                <Label htmlFor="username">Username</Label>
                                                <Input id="username" name="username" type="text" placeholder="someone" required value={username}
                                                    onChange={(e) => setUsername(e.target.value)} />
                                            </div>
                                            <div className="grid gap-2">
                                                <Label htmlFor="email">Email</Label>
                                                <Input id="email" name="email" type="email" placeholder="example@gmail.com" required value={email}
                                                    onChange={(e) => setEmail(e.target.value)} />
                                            </div>
                                            <div className="grid gap-2">
                                                <Label htmlFor="password">Password</Label>
                                                <Input id="password" type="password" placeholder="keep it secret" value={password}
                                                    onChange={(e) => setPassword(e.target.value)} />
                                            </div>
                                            <div className="grid gap-2">
                                                <Label htmlFor="balance">balance</Label>
                                                <Input id="balance" name="balance" type="number" placeholder="no limit" required value={balance}
                                                    onChange={(e) => setBalance(e.target.value)} />
                                            </div>
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
                        
          
                            </Dialog></div>  </CardHeader>
                        <CardContent>
                            {/* <Button className=' flex flex col mx-72 m-2' onClick={deleteSelectedCustomers}>Delete Selected</Button>  */}
                            <div className="ag-theme-quartz dark:ag-theme-quartz-dark"
                                style={{ height: 530, width: 700 }}
                            >
                                <AgGridReact
                                    rowData={customer}
                                    ref={gridRef}
                                    columnDefs={[
                                        { field: 'customer_id', checkboxSelection: true, headerCheckboxSelection: true },
                                        { field: "username", editable: true },
                                        { field: "email", editable: true },
                                        { field: "balance", editable: true },
                                        { field: "net_stock", editable: true },

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
                                width={480}
                                pagination={true}
                            />
 <GenericChart
      url='http://localhost:8000/api/queries/customers/top-stock-transactions'
      chartOptions={topCustomersChartOptions}
      title="Top Customers"
    />
    </div>
                            </div>
                </main>
            </div>
        </>
    );
}
export default AdminCustomers;


