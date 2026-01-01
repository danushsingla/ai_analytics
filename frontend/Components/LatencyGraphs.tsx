"use client";

import dynamic from "next/dynamic"
import { useEffect, useState } from "react";

// Prevents SSR hydration errors when trying to import LatencyGraph
// This essentially tells to not render this component on the server side (since it uses recharts which generates internal SSR errors)
const LatencyGraph = dynamic(
  () => import("@/Components/LatencyGraph").then((m) => m.LatencyGraph),
  { ssr: false }
)

export function LatencyGraphs({project_api_key}: {project_api_key: string}) {
    const [endpoints, setEndpoints] = useState<string[]>([]);

    // Call backend /get_api_urls to get all valid API URLs for this project_api_key
    async function fetchEndpoints() {
        const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/get_api_urls?public_api_key=${encodeURIComponent(project_api_key)}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!res.ok) {
            const text = await res.text();
            throw new Error(`Failed to fetch API URLs: ${text}`);
        }
        const data = await res.json();
        setEndpoints(data["valid_urls"]);
    }

    // Call fetchEndpoints when this client component mounts
    useEffect(() => {
        fetchEndpoints().catch((error) => {
            console.error('Error fetching API URLs:', error);
        });
    }, []);

    return (
        <div className="space-y-4">
            {endpoints.map((endpoint) => (
                <LatencyGraph key={endpoint} project_api_key={project_api_key} endpoint={endpoint} />
            ))}
        </div>
    )
}