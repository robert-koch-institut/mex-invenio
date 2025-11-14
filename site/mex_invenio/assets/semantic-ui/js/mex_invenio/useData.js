import { useEffect, useState } from "react";

export const useData = (mexId) => {

    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!mexId) return;

        const endpoint = `/records/mex/${mexId}/json?normalised`;
        console.log("Fetching", endpoint);

        setLoading(true);
        setError(null);

        fetch(endpoint, {
            method: "GET",
            headers: {
                Accept: "application/json",
            },
        })
        .then((res) => {
            if (!res.ok) {
                throw new Error(`Fetch failed: ${res.status}`);
            }
            return res.json();
        })
        .then((json) => {
            setData(json);
            setLoading(false);
        })
        .catch((err) => {
            console.error(err);
            setError(err);
            setLoading(false);
        });
  }, [mexId]);

  return { data, loading, error };
}

