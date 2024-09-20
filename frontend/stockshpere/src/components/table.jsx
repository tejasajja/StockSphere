"use strict";

import React, {
    useCallback,
    useMemo,
    useRef,
    useState,
    StrictMode,
  } from "react";
  import { createRoot } from "react-dom/client";
  import { AgGridReact } from "ag-grid-react";
  import "ag-grid-community/styles/ag-grid.css";
  import "ag-grid-community/styles/ag-theme-quartz.css";
//   import "./styles.css";
  
  const GridExample = () => {
    const containerStyle = useMemo(() => ({ width: "100%", height: "100%" }), []);
    const gridStyle = useMemo(() => ({ height: "100%", width: "100%" }), []);
    const [rowData, setRowData] = useState();
    const [columnDefs, setColumnDefs] = useState([
      { field: "athlete" },
      { field: "age", maxWidth: 120 },
      { field: "country" },
      { field: "year", maxWidth: 120 },
      { field: "sport" },
      { field: "gold" },
      { field: "silver" },
      { field: "bronze" },
      { field: "total" },
    ]);
    const defaultColDef = useMemo(() => {
      return {
        flex: 1,
        minWidth: 150,
        filter: true,
      };
    }, []);
  
    const onGridReady = useCallback((params) => {
      fetch("https://www.ag-grid.com/example-assets/olympic-winners.json")
        .then((resp) => resp.json())
        .then((data) => setRowData(data));
    }, []);
  
    return (
      <div style={containerStyle}>
        <div
          style={gridStyle}
          className={
            "ag-theme-quartz-dark"
          }
        >
          <AgGridReact
            rowData={rowData}
            columnDefs={columnDefs}
            defaultColDef={defaultColDef}
            onGridReady={onGridReady}
          />
        </div>
      </div>
    );
  };
  
  const root = createRoot(document.getElementById("root"));
  root.render(
    <StrictMode>
      <GridExample />
    </StrictMode>,
  );
  export default GridExample;
