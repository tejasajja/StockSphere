import { useCallback, useState } from 'react';
import { Button } from "@/components/ui/button";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

import { useLocalState } from '@/utils/usingLocalStorage';
import { UserNav } from './comp/user-nav';
import { MainNav } from '@/components/ui/main-nav';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-quartz.css";
import Select from 'react-select';
import GenericTable from './comp/GenericTable';
import useFetchDataWithSetter from '@/hooks/datafetch';

function Dashboard() {
    const [AgentData, setAgentData] = useState([]);
    const [transaction, setTransaction] = useState([]);
    const [stocks, setStocks] = useState([]);
    const [selectedStock, setSelectedStock] = useState(null);
    const [selectedAgent, setSelectedAgent] = useState(null);
    const [selectedAction, setSelectedAction] = useState(null);
    const [volume, setVolume] = useState("");
    const [jwt] = useLocalState("", "jwt");



    const handleSetStockData = useCallback((data) => {
        const formattedstocks = data.map(stock => ({
            label: stock.Company_ticker,
            value: stock.stock_id,
            cp: stock.Closed_price
        }));
        setStocks(formattedstocks);
    }, []);
    useFetchDataWithSetter({
        url: 'http://localhost:8000/api/cryptocurrencies/',
        method: 'GET',
        jwt,
        setData: handleSetStockData
    });

    const handleSetAgentData = useCallback((data) => {
        const formattedAgents = data.map(agent => ({
            label: agent.name,
            value: agent.agent_id
        }));
        setAgentData(formattedAgents);
    }, []);
    useFetchDataWithSetter({
        url: 'http://localhost:8000/api/agents/',
        method: 'GET',
        jwt,
        setData: handleSetAgentData
    });

    const handleSelectChangestock = selectedOption => {
        setSelectedStock(selectedOption);
    };
    const handleSelectChangeagent = selectedOption => {
        setSelectedAgent(selectedOption);
    };
    const handleSelectAction = selectedOption => {
        setSelectedAction(selectedOption);
    };


    const action = [
        { label: 'sell', value: 0 },
        { label: 'buy', value: 1 }
    ]



    const handleBuy = async () => {
        const transactionData = {
            crypto_id: selectedStock.value, 
            stock_id: 0,
            agent_id: selectedAgent.value, 
            ticket: selectedStock.label,
            volume: volume, 
            each_cost: selectedStock.cp,
            action: selectedAction.label
        };

        try {
            const requestOptions = {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: "Bearer " + jwt,
                },
                body: JSON.stringify(transactionData),
            };

            const response = await fetch('http://localhost:8000/api/transactions/', requestOptions);

            if (!response.ok) {
                const errorData = await response.json(); // Assuming the server sends back JSON with error details
                throw new Error(`Failed to create new transaction: ${JSON.stringify(errorData)}`);
            }
            const data = await response.json();
            console.log('Transaction successful', data);

            setTransaction([...transaction, data]);
        } catch (error) {
            console.error('Failed to complete the transaction:', error);
            if (error.response && error.response.data && error.response.data.detail) {
                console.error('Transaction error details:', error.response.data.detail);
                if (Array.isArray(error.response.data.detail)) {
                    console.error('First validation error:', error.response.data.detail[0]);
                }
            }
        }
    };



    return (
        <>
            <div className="flex flex-col bg-gray-100 shadow-md  dark:bg-gray-900 ">
                <nav className=" bg-gray-200 shadow-md dark:bg-gray-950 flex justify-between items-center p-4 border-b">
                    <MainNav className="ml-12  dark:text-white" />
                    <UserNav className="mr-14-12" />
                </nav>

                <div className="flex flex-wrap">
                    <div className='flex flex-row'>

                        <GenericTable
                            url="http://localhost:8000/api/cryptocurrencies/"
                            title="Crypto"
                            columnDefs={[
                                { field: "Name" },
                                { field: "Symbol" },
                                { field: "Last_Close" },
                                { field: "Market_Cap" },
                                { field: "Volume_24h" },
                                { field: "Circulating_Supply" }

                            ]}
                            height={540}  
                            width={640}  
                            pagination='true'
                        />

                        <Card className="justify-center h-[550px] w-[320px] my-32 mx-16 dark:text-white" >


                            <CardHeader className="space-y-1">
                                <CardTitle className="text-2xl">Trade Crypto</CardTitle>
                                <CardDescription>
                                    Enter your detials to trade stocks
                                </CardDescription>
                            </CardHeader>

                            <CardContent as="form" className="grid gap-4">

                                <Label htmlFor="stock">Crypto</Label>
                                <Select 
                                    inputId="stock"
                                    value={selectedStock}
                                    onChange={handleSelectChangestock}
                                    options={stocks}
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
                                <div className="grid gap-2">
                                    <Label htmlFor="id">Volume</Label>
                                    <Input id="vilume" name="volume" type="number" placeholder="" value={volume}
                                        onChange={(e) => setVolume(e.target.value)} />
                                </div>


                            </CardContent>

                            <CardFooter className="">
                                <Button type="submit" onClick={handleBuy} className="w-full">Add account</Button>


                            </CardFooter>
                        </Card>
                    </div>
                    <div className="md:col-span-1  mt-10">
                    </div>
                    <div className='flex flex-row '>
                        <div className='my'>
                            <GenericTable
                                url='http://localhost:8000/api/transactions/customer-cryptos'
                                title="Your Stocks"
                                columnDefs={[
                                    { field: "crypto_ticket" },
                                    { field: "each_cost" },
                                    { field: "volume" },

                                ]}
                                height={490}
                                width={400}
                                pagination={false}
                            />
                        </div>

                        <div>

                            <GenericTable
                                url="http://localhost:8000/api/transactions/customer/cryptos"
                                title="transactions"
                                columnDefs={[
                                    { field: "ticket" },
                                    { field: "action" },
                                    { field: "volume" },
                                    { field: "each_cost" },
                                    { field: "date" }

                                ]}
                                height={490}
                                width={620}
                                pagination='true'
                            />
                        </div>
                    </div>
                </div>
            </div>
        </>


    );
}
export default Dashboard;


