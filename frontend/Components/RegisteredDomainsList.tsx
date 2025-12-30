// Server Component
import { auth } from '@clerk/nextjs/server';
import APIUrlList from './APIUrlList';

export default async function RegisteredDomainsList() {
    const { userId } = await auth();

    if (!userId) {
        return <div>Please sign in to view your registered domains.</div>;
    }

    const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/get_domains`, {
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

    return (
        <div>
            <h2 className="text-2xl font-bold mb-4">Registered Domains</h2>
            <ul>
                { domains.length === 0 ? ( <li>No registered domains found.</li> ) :
                domains.map((domain: string) => (
                    <li key={domain} className="mb-2">{domain}
                    <APIUrlList domain={domain} public_api_key={api_keys[domains.indexOf(domain)]} />
                    </li>
                ))}
            </ul>
        </div>
    )
}