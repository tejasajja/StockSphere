import { useEffect, useRef, useState } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { useLocalState } from '@/utils/usingLocalStorage';
import AdminMainNav from '@/components/ui/Admin-main-nav';
import { UserNav } from './comp/user-nav';
import { AgGridReact } from 'ag-grid-react';
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-quartz.css";
import GenericTable from './comp/GenericTable';
import GenericChart from './comp/GenericChart';

function AdminAgents() {
    const [agents, setAgents] = useState([]);
    const [jwt] = useLocalState("", "jwt");
    const gridRef = useRef(null);

    useEffect(() => {
        const fetchAgents = async () => {
            try {
                const requestOptions = {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: "Bearer " + jwt,
                    },
                };
                const response = await fetch('http://localhost:8000/api/agents/', requestOptions);
                const data = await response.json();
                setAgents(data);
            } catch (error) {
                console.error('Error fetching agents data:', error);
            }
        };

        fetchAgents();
    }, [jwt]);

    const addNewAgent = () => {
        const newAgent = {
            tempId: new Date().getTime(), // temporary ID for the frontend
            name: "",
            contact: "",
            level: "",
        };
        setAgents([...agents, newAgent]);
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

    const onCellValueChanged = async (params) => {
        const { data } = params;
        const updateData = { ...data, [params.column.colId]: params.newValue };

        if (data.agent_id) {
            try {
                const response = await fetch(`http://localhost:8000/api/agents/${data.agent_id}`, {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${jwt}`,
                    },
                    body: JSON.stringify(updateData)
                });
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(`Failed to update agent: ${JSON.stringify(errorData)}`);
                }
                const updatedData = await response.json();
                setAgents(currentAgents =>
                    currentAgents.map(agent => agent.agent_id === data.agent_id ? { ...agent, ...updatedData } : agent)
                );
            } catch (error) {
                console.error('Error updating agent:', error);
            }
        } else {
            console.log("Saving new agent:", updateData);
            try {
                const response = await fetch(`http://localhost:8000/api/agents/`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${jwt}`,
                    },
                    body: JSON.stringify(updateData)
                });
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(`Failed to save new agent: ${JSON.stringify(errorData)}`);
                }
                const newAgentData = await response.json();
                setAgents(currentAgents =>
                    currentAgents.map(agent => agent.tempId === data.tempId ? { ...agent, ...newAgentData} : agent)
                );
            } catch (error) {
                console.error('Error saving new agent:', error);
            }
        }
    };

    const deleteSelectedAgents = async () => {
        const selectedNodes = gridRef.current.api.getSelectedNodes();
        const selectedIDs = selectedNodes.map(node => node.data.agent_id);
        const response = await fetch(`http://localhost:8000/api/agents/admin`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${jwt}`,
            },
            body: JSON.stringify({ agent_ids: selectedIDs })
        });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(`Failed to delete agents: ${JSON.stringify(errorData)}`);
        }

        const deleteResponse = await response.json();
        console.log(deleteResponse.message);
        setAgents(prevAgents => prevAgents.filter(agent => !selectedIDs.includes(agent.agent_id)));
    };

    return (
        <>
        <div className="flex flex-col bg-gray-100 shadow-md dark:bg-gray-900">
            <nav className="navbar bg-gray-200 shadow-md dark:bg-gray-950 flex justify-between items-center p-4 border-b">
                <AdminMainNav className="ml-12 dark:text-white" />
                <UserNav className="mr-12" />
            </nav>
            <main className="content">
            <div className='flex flex-wrap'>      
                <Card className="justify-center m-24 w-[620px]">
                    <CardHeader>
                        <div className='flex flex-row'>
                            <Button className='flex flex-col mx-7 m-2' onClick={addNewAgent}>Add New Agent</Button>
                            <Button className='flex flex-col mx-7 m-2 bg-red-500' onClick={deleteSelectedAgents}>Delete Selected</Button>
                        </div>
                    </CardHeader>
                    <CardContent>
                        <div className="ag-theme-quartz" style={{ height: 570, width: 570 }}>
                            <AgGridReact
                                rowData={agents}
                                ref={gridRef}
                                columnDefs={[
                                    { field: "agent_id", checkboxSelection: true, headerCheckboxSelection: true },
                                    { field: "name", editable: true },
                                    { field: "contact", editable: true },
                                    { field: "level", cellEditor: 'agSelectCellEditor',
                                    cellEditorParams: {
                                        values: ['Junior', 'Senior', 'Manger'],
                                    },editable: true , filter: true, floatingFilter: true }
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


                <GenericChart 
  url='http://localhost:8000/api/queries/agents/top-stock-transactions' 
  chartOptions={topAgentsChartOptions} 
  title="Top Agents" 
/>

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
                            </div>
            </main>
        </div>
        </>
    );
}

export default AdminAgents;
