"use client"

import { CartesianGrid, Line, LineChart, XAxis, YAxis } from "recharts"

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/Components/ui/card"
import { useState, useEffect } from "react"

export const description = "A linear line chart"

type LatencyPoint = {
    time: number
    average_latency_ms: number
  }

export function LatencyGraph({project_api_key, endpoint}: {project_api_key: string, endpoint: string}) {
    const [data, setData] = useState<LatencyPoint[]>([])

    // Call backend /getLatencyRollupData to get latency rollup data for this project_api_key and endpoint
    async function getData() {
        const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/getLatencyRollupData?public_api_key=${encodeURIComponent(project_api_key)}&endpoint=${encodeURIComponent(endpoint)}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        if (!res.ok) {
            const text = await res.text();
            throw new Error(`Failed to fetch latency rollup data: ${text}`);
        }
        const data = await res.json();
        const points: LatencyPoint[] = data.latency_rollups.map(
            (r: any) => ({
                time: new Date(r.time).getTime(), // Converts ISO to ms
                average_latency_ms: r.average_latency_ms,
            })
        );

        setData(points)
    }

    // Grab data every client component mount
    useEffect(() => {
        getData().catch((error) => {
            console.error('Error fetching latency rollup data:', error);
        });
    }, []);

    // Format this time for the XAxis to show hour:minute:second
    const formatTime = (ms: number) => {
        return new Date(ms).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
        })
    };

    return (
    <Card>
        <CardHeader>
        <CardTitle>Latency Chart for {endpoint}</CardTitle>
        </CardHeader>
        <CardContent>
        <LineChart
        accessibilityLayer
        data={data}
        width={700}
        height={300}
        margin={{
            left: 12,
            right: 12,
        }} 
        >
        <CartesianGrid vertical={false} />
        <XAxis
            dataKey="time"
            type="number"
            scale="time"
            domain={['dataMin', 'dataMax']}
            tickFormatter={formatTime}
            tickMargin={8}
        />
        <YAxis />
        <Line
            dataKey="average_latency_ms"
            type="linear"
            stroke="blue"
            strokeWidth={2}
            dot={false}
        />
        </LineChart>
        </CardContent>
    </Card>
    )
}
