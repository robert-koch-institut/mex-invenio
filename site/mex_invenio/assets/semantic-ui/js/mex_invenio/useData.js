import { useEffect, useState } from "react";

export const useData = ({ mex_id }) => {

    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!mex_id) return;

        const endpoint = `/records/mex/${mex_id}/json`;
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
  }, [mex_id]);

  return { data, loading, error };
}

