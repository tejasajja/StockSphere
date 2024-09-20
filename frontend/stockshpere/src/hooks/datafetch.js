import { useEffect } from 'react';

const useFetchDataWithSetter = ({ url, method ,jwt, setData }) => {
    useEffect(() => {
        const fetchData = async () => {
            try {
                const requestOptions = {
                    method: method,
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: "Bearer " + jwt,
                    },
                };
                const response = await fetch(url, requestOptions);
                if (!response.ok) {
                    const errorData = await response.json(); // Assuming the server sends back JSON with error details
                    throw new Error(`Failed to create new transaction: ${JSON.stringify(errorData)}`);
                }
                const result = await response.json();
                setData(result);
            } catch (error) {
                console.error(`Error fetching data from ${url}:`, error);
                // Optionally handle errors externally
            }
        };
        fetchData();
    }, [url, jwt, method, setData]); // Include setData in the dependency array
};

export default useFetchDataWithSetter;
