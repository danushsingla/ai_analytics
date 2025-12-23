// Server Component
import { auth } from '@clerk/nextjs/server';

export default async function RegisteredDomainsList() {
    const { userId } = await auth();

    const domains = async function fetchDomains() {
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
        return data.domains || [];
    }

    async function RegisterDomain() {
        const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/register_domain`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ user_id: userId, domain: "example.com" }),
        });
    }

    return (
        <div>
            <h2 className="text-2xl font-bold mb-4">Registered Domains</h2>
            <ul>
                { domains.length === 0 ? ( <li>No registered domains found.</li> ) :
                (await domains()).map((domain: string) => (
                    <li key={domain} className="mb-2">{domain}</li>
                ))}
            </ul>
            <button className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
                Add New Domain
            </button>
        </div>
    )
}