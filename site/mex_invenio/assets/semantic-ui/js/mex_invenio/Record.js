import React from "react";
import { useData } from "./useData";

export const Record = ({ mex_id }) => {
  const { data, loading, error } = useData({mex_id});

  if (loading) return <p>Loading…</p>;
  if (error) return <p style={{ color: "red" }}>Error: {error.message}</p>;

  return <pre>{JSON.stringify(data, null, 2)}</pre>;
}