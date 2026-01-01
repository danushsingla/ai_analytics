"use client"

import { TrendingUp } from "lucide-react"
import { CartesianGrid, Line, LineChart, XAxis, YAxis } from "recharts"

import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/Components/ui/card"

export const description = "A linear line chart"

const chartData = [
  { month: "January", desktop: 186 },
  { month: "February", desktop: 305 },
  { month: "March", desktop: 237 },
  { month: "April", desktop: 73 },
  { month: "May", desktop: 209 },
  { month: "June", desktop: 214 },
]

export function LatencyGraph({project_api_key}: {project_api_key: string}) {
    // Call backend /getLatencyRollupData to get latency rollup data for this project_api_key and its valid endpoints
    
    return (
    <Card>
        <CardHeader>
        <CardTitle>Line Chart - Linear</CardTitle>
        <CardDescription>January - June 2024</CardDescription>
        </CardHeader>
        <CardContent>
        <LineChart
        accessibilityLayer
        data={chartData}
        width={700}
        height={300}
        margin={{
            left: 12,
            right: 12,
        }}
        >
        <CartesianGrid vertical={false} />
        <XAxis
            dataKey="hour"
            tickLine={false}
            axisLine={false}
            tickMargin={8}
            tickFormatter={(value) => value.slice(0, 3)}
        />
        <YAxis
            domain={[0, 400]}
            />
        <Line
            dataKey="desktop"
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
