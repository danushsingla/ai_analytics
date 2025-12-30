"use client"

import { Checkbox } from "@/Components/ui/checkbox"
import { useState, useEffect } from "react";

export default function CheckBoxAddRemoveAPI({public_api_key, url}: {public_api_key?: string; url?: string}) {
    const [checked, setChecked] = useState(false);

    if(!public_api_key || !url) {
        return null;
    }

    // On first load, load the validAPIUrls from backend
    useEffect(() => {
        // Fetch updated valid URLs
        fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/get_api_urls?public_api_key=${encodeURIComponent(public_api_key)}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        }).then(async (res) => {
            if (res.ok) {
                const data = await res.json();
                const valid = data.valid_urls || [];
                setChecked(valid.includes(url));
            } else {
                console.error('Failed to fetch API URLs');
            }
        });
    }, [public_api_key, url]);

    // Toggles between adding/removing endpoint
    async function toggle(next: boolean) {
        setChecked(next);

        const endpoint = next ? 'add_valid_api_url' : 'remove_valid_api_url';

        const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ public_api_key, url }),
        });
        if (!res.ok) {
            console.error(`Failed to ${next ? 'add' : 'remove'} valid API URL`);
        }
    }

  return (
    <div>
        <Checkbox checked={checked} onCheckedChange={(value) => {
            toggle(!!value);
        }} />
    </div>
  )
}
