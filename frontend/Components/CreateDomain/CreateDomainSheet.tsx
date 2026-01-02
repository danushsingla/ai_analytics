"use client"

import { Button } from "@/Components/ui/button"
import { Input } from "@/Components/ui/input"
import { Label } from "@/Components/ui/label"
import {
  Sheet,
  SheetClose,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle
} from "@/Components/ui/sheet"
import { useUser } from "@clerk/nextjs"
import { useState } from "react"

export function CreateDomainSheet({
  open,
  onOpenChange,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
}) {
  // Variable to store domain
  const [domain, setDomain] = useState("");
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);

  // Grab user
  const { user, isLoaded, isSignedIn } = useUser();

  // Ensure user is loaded and signed in
  if (!isLoaded || !isSignedIn || !user) {
    return null;
  }

  // Grab user ID from Clerk
  const userId = user.id;

  // When Add is clicked, I need to call the backend /register_domain endpoint to register the domain
  async function RegisterDomain() {
    // Set loading to prevent multiple requests at once
    setLoading(true);

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/register_domain`, {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify({ user_id: userId, domain: domain, name: name }),
      });

      if (!res.ok) {
          const text = await res.text();
          throw new Error(`Failed to register domain: ${text}`);
      }
    } catch (error) {
      console.error('Error registering domain:', error);
    } finally {
      setLoading(false);
      onOpenChange(false); // Close the sheet after registering
    }
  }

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent>
        <SheetHeader>
          <SheetTitle>Add New Domain</SheetTitle>
          <SheetDescription>
            Add a new website domain to your account to start tracking analytics.
          </SheetDescription>
        </SheetHeader>
        <div className="grid flex-1 auto-rows-min gap-6 px-4">
          <div className="grid gap-3">
            <Label htmlFor="domain-name">Domain Name</Label>
            <Input id="domain-name" value={name} onChange={(e) => setName(e.target.value)} />
          </div>
          <div className="grid gap-3">
            <Label htmlFor="domain-url">Website URL</Label>
            <Input id="domain-url" value={domain} onChange={(e) => setDomain(e.target.value)} />
          </div>
        </div>
        <SheetFooter>
          <Button type="submit" onClick={RegisterDomain} disabled={loading}>{loading ? "Adding..." : "Add"}</Button>
          <SheetClose asChild>
            <Button variant="outline">Close</Button>
          </SheetClose>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  )
}
