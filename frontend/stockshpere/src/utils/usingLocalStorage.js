import { useEffect, useState } from "react";

function useLocalState(defaultValue, key) {
    const [value, setValue] = useState(() => {
        try {
            const localStorageValue = localStorage.getItem(key);
            return localStorageValue !== null ? JSON.parse(localStorageValue) : defaultValue;
        } catch (error) {
            console.error(`Error parsing the local storage value for key "${key}":`, error);
            return defaultValue;
        }
    });

    useEffect(() => {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            console.error(`Error setting the local storage value for key "${key}":`, error);
        }
    }, [key, value]);

    return [value, setValue];
}

export { useLocalState };
