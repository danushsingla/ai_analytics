"use client";
import { useParams } from "next/navigation";
import { LatencyGraphs } from "@/Components/LatencyGraphs";


export default function AnalysisPage() {
    // Grab the project api key from the URL params
    const params = useParams<{ project_api_key: string }>();
    const projectApiKey = params.project_api_key;

    return (
        <div className="flex-1 min-w-0">
            <LatencyGraphs project_api_key={projectApiKey}/>
        </div>
    );
}