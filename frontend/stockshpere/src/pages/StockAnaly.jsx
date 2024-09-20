import {  useEffect, useState } from 'react';
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { useLocalState } from '@/utils/usingLocalStorage';
import { UserNav } from './comp/user-nav';
import { MainNav } from '@/components/ui/main-nav';
import { Card, CardContent, CardFooter } from '@/components/ui/card';
import Select from 'react-select';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';

import { AgGridReact } from 'ag-grid-react';
import StockHistoryChart from './comp/StockHistoryChart ';


function StockAnl() {
    const [stocks, setStocks] = useState([]);
    const [selectedStock, setSelectedStock] = useState(null);
    const [startDate, setStartDate] = useState(new Date());
    const [endDate, setEndDate] = useState(new Date());
    const [stockHistory, setStockHistory] = useState([]);
    const [jwt] = useLocalState("", "jwt");

    // Column definitions for Ag-Grid
    const columnDefs = [
        { headerName: "Date", field: "date", sortable: true, filter: true },
        { headerName: "Close", field: "Close", sortable: true, filter: true },
        { headerName: "Open", field: "Open", sortable: true, filter: true },
        { headerName: "High", field: "High", sortable: true, filter: true },
        { headerName: "Low", field: "Low", sortable: true, filter: true },

        { headerName: "Adjusted Close", field: "Adj Close", sortable: true, filter: true },
        { headerName: "Volume", field: "Volume", sortable: true, filter: true },
       
    ];

    // Fetch stocks to populate the dropdown
    useEffect(() => {
        const fetchStocks = async () => {
            const response = await fetch('http://localhost:8000/api/stocks/', {
                method: 'GET',
                headers: {
                    Authorization: "Bearer " + jwt,
                    'Content-Type': 'application/json'
                }
            });
            if (!response.ok) {
                console.error('Failed to fetch stock data');
                return;
            }
            const data = await response.json();
            const formattedStocks = data.map(stock => ({
                label: stock.Company_ticker,
                value: stock.stock_id
            }));
            setStocks(formattedStocks);
        };

        fetchStocks();
    }, [jwt]);

    // Fetch stock history based on selected stock and date range
    const fetchStockHistory = async () => {
        if (!selectedStock) {
            alert('Please select a stock');
            return;
        }

        const response = await fetch('http://localhost:8000/api/stock-history/range', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Authorization: "Bearer " + jwt,
            },
            body: JSON.stringify({
                company_ticker: selectedStock.label,
                start_date: startDate.toISOString().slice(0, 10),  // Format as "YYYY-MM-DD"
                end_date: endDate.toISOString().slice(0, 10)  // Format as "YYYY-MM-DD"
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.error('Failed to fetch stock history:', JSON.stringify(errorData));
            alert('Failed to fetch stock history: ' + JSON.stringify(errorData));
            return;
        }

        const data = await response.json();
        setStockHistory(data);
        console.log('Stock History:', data);
    };

    return (
        <>
            <div className="flex flex-col bg-gray-100 shadow-md  dark:bg-gray-900 ">
                <nav className="bg-gray-200 shadow-md dark:bg-gray-950 flex justify-between items-center p-4 border-b">
                    <MainNav className="ml-12 dark:text-white" />
                    <UserNav className="mr-14-12" />
                </nav>

                <div className="flex flex-wrap">
                    <Card className="flex flex-row justify-center h-[80px] w-[1200px] mt-24 mx-24 dark:text-white" >
                    <CardContent as="form" className="flex flex-auto my-3">
  <Label htmlFor="stock">Stock</Label>
  <Select
      inputId="stock"
      value={selectedStock}
      onChange={setSelectedStock}
      options={stocks}
      isClearable={true}
      isSearchable={true}
      placeholder="Select stock"
      className="w-52 mx-5 dark:text-white"
  />
  <Label htmlFor="start-date">Start Date</Label>
  <DatePicker
      selected={startDate}
      onChange={setStartDate}
      className="form-input  text-black dark:text-white dark:bg-gray-900 bg-white border border-gray-300 rounded-md py-2  leading-tight focus:outline-none focus:border-blue-500"
  />
  <Label htmlFor="end-date">End Date</Label>
  <DatePicker
      selected={endDate}
      onChange={setEndDate}
      className="form-input  text-black dark:text-white dark:bg-gray-900 bg-white border border-gray-300 rounded-md py-2 leading-tight focus:outline-none focus:border-blue-500"
  />
</CardContent>
                        <CardFooter>
                            <Button type="button" onClick={fetchStockHistory} className="w-full">Fetch Stock History</Button>
                        </CardFooter>
                    </Card>
                    {stockHistory.length > 0 && (
                        
                        <Card className={`justify-center mx-24 my-16 h-[400] w-[200] dark:text-white`}>
                        <CardContent className='flex flex-row'>
                            <div className={`ag-theme-quartz`} style={{ height: 400, width: 470 }}>
                                <AgGridReact
                                    rowData={stockHistory}
                                    columnDefs={columnDefs}
                                    autoSizeStrategy={{ type: 'fitCellContents' }}
                                    pagination={true}
                                    paginationPageSize={10}
                                    rowSelection="multiple"
                                    paginationPageSizeSelector={[10, 20, 50, 100]}
                                    className='my-9'
                                />
                                  
                            </div>
                            <StockHistoryChart stockHistory={stockHistory} />
                        </CardContent>
                    </Card>
                    )}
                </div>
            </div>
        </>
    );
}

export default StockAnl;
