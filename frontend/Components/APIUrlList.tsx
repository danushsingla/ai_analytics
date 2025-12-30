import CheckBoxAddRemoveAPI from '@/Components/CheckBoxAddRemoveAPI';

export default async function APIUrlList({ domain, public_api_key }: { domain: string; public_api_key: string }) {
    const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/get_api_urls?public_api_key=` + public_api_key, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    });

    if (!res.ok) {
        console.error('Failed to fetch API URLs');
        return;
    }

    const data = await res.json();
    const allAPIUrls = data.all_urls || [];

    return (
        <div>
            <h3 className="text-xl font-semibold mb-2">API Endpoints</h3>
            <ul className="mb-4">
                {allAPIUrls.length === 0 ? (
                    <li>No API URLs found.</li>
                ) : (
                    allAPIUrls.map((url: any) => 
                    <li key={url} className="mb-1">{url}
                    <CheckBoxAddRemoveAPI public_api_key={public_api_key} url={url} />
                    </li>)
                )}
            </ul>
        </div>
    );
}