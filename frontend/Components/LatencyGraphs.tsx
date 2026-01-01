import dynamic from "next/dynamic"

// Prevents SSR hydration errors when trying to import LatencyGraph
// This essentially tells to not render this component on the server side (since it uses recharts which generates internal SSR errors)
const LatencyGraph = dynamic(
  () => import("@/Components/LatencyGraph").then((m) => m.LatencyGraph),
  { ssr: false }
)

export function LatencyGraphs({project_api_key}: {project_api_key: string}) {
    // Call backend /get_api_urls to get all valid API URLs for this project_api_key

    return (
        <div className="space-y-4">
            <LatencyGraph project_api_key={project_api_key} />
            <LatencyGraph project_api_key={project_api_key} />
            <LatencyGraph project_api_key={project_api_key} />
        </div>
    )
}