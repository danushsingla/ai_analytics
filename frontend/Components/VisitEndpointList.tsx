"use client";

import * as React from "react"
import { Button } from "@/Components/ui/button"
import {
  Drawer,
  DrawerClose,
  DrawerContent,
  DrawerDescription,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from "@/Components/ui/drawer"
import CheckBoxAddRemoveAPI from '@/Components/CheckBoxAddRemoveAPI';
import { ScrollArea } from "@/Components/ui/scroll-area"

export default function VisitEndpointList({ domain, public_api_key }: { domain: string; public_api_key: string }) {
    const [open, setOpen] = React.useState(false);
    const [allAPIUrls, setAllAPIUrls] = React.useState<Array<string>>([]);
    const [loading, setLoading] = React.useState(false);

    React.useEffect(() => {
        if (!open) return
        if (!public_api_key) return;

        ;(async () => {
            try {
                setLoading(true)

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
                console.log(data)
                setAllAPIUrls(data.all_urls || []);
            } catch (error) {
                console.error('Error fetching API URLs:', error);
            } finally {
                setLoading(false);
            }
        })();
    }, [open, public_api_key]);

    return (
        <Drawer open={open} onOpenChange={setOpen}>
            <DrawerTrigger asChild>
                <Button variant="outline">View API Endpoints for {domain}</Button>
            </DrawerTrigger>
        <DrawerContent className="flex flex-col h-[80vh] w-full">
            <DrawerHeader>
                <DrawerTitle>API Endpoints for {domain}</DrawerTitle>
                <DrawerDescription>
                    Below is the list of API endpoints associated with the domain {domain}.
                </DrawerDescription>
            </DrawerHeader>

            <ScrollArea className="flex-1 px-4">
                <h3 className="text-xl font-semibold mb-2">API Endpoints</h3>
                <ul className="mb-4">
                    {allAPIUrls.length === 0 ? (
                        <li>No API URLs found.</li>
                    ) : (
                        allAPIUrls.map((url: any) => 
                        <li key={url} className="mb-1 flex gap-3">{url}
                        <CheckBoxAddRemoveAPI public_api_key={public_api_key} url={url} />
                        </li>)
                    )}
                </ul>
            </ScrollArea>
            <DrawerClose asChild>
                <Button variant="outline">Close</Button>
            </DrawerClose>
        </DrawerContent>
        </Drawer>
    );
}