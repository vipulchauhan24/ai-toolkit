"use client";

export function Url() {
  return <p>{process.env.DB_URL}</p>;
}
