// Server Component
import { auth } from '@clerk/nextjs/server';
import APIUrlList from './VisitEndpointList';
import ProjectsTable from './ProjectsTable';


export default async function RegisteredDomainsList() {
    const { userId } = await auth();

    if (!userId) {
        return <div>Please sign in to view your registered domains.</div>;
    }

    const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/get_projects_info`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id: userId }),
    });

    if(!res.ok) {
        console.error('Failed to fetch domains');
        return [];
    }
    const data = await res.json();
    const domains = Array.isArray(data?.domains) ? data.domains : [];
    const api_keys = Array.isArray(data?.api_keys) ? data.api_keys : [];
    const names = Array.isArray(data?.names) ? data.names : [];

    const projects = domains.map((domain: string, index: number) => ({
        domain,
        name: names[index],
        project_api_key: api_keys[index],
    }));


    return (
        <div>
            <ProjectsTable projects={projects} />
            <ul>
                { projects.map((project: any) => (
                    <li key={project.project_api_key} className="mb-2">
                    <APIUrlList domain={project.domain} public_api_key={project.project_api_key} />
                    </li>
                ))}
            </ul>
        </div>
    )
}