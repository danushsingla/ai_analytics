// Server Component
import { auth } from '@clerk/nextjs/server';
import APIUrlList from './APIUrlList';
import VisitAnalysisSiteButton from './VisitAnalysisSiteButton';
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

    return (
        <div>
            <ProjectsTable names={names} domains={domains} api_keys={api_keys} />
            <ul>
                { domains.map((domain: string, index: number) => (
                    <li key={domain} className="mb-2">
                    <APIUrlList domain={domain} public_api_key={api_keys[index]} />
                    <VisitAnalysisSiteButton publicApiKey={api_keys[index]}/>
                    </li>
                ))}
            </ul>
        </div>
    )
}