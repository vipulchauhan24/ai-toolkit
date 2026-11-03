"use client";

export default function C() {
  return <div>{process.env.DB_URL}</div>;
}
