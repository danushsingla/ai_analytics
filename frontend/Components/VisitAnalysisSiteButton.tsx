"use client"

import { Button } from "@/Components/ui/button"
import Link from "next/link"
import { useUser } from "@clerk/nextjs"
import { useRouter } from "next/navigation"

type VisitAnalysisSiteButtonProps = {
    publicApiKey: string;
}

export default function VisitAnalysisSiteButton({
    publicApiKey,
}: VisitAnalysisSiteButtonProps) {

    // Grab userId for page redirect
    const { user, isLoaded, isSignedIn } = useUser();

    // Use router for navigation
    const router = useRouter();

    async function getUserId() {

        if (!isLoaded || !isSignedIn || !user) {
            alert("User not signed in.");
            return '/';
        }

        const userId = user.id;

        let href = "";

        if(!userId) {
            alert("User not signed in.");
            href = '/';
        }

        if(!publicApiKey) {
            alert("No public API key found for this domain.");
            href= '/dashboard';
        }

        // Redirect to the link frontend/dashboard/userId/analysis/publicApiKey
        router.push(`${process.env.NEXT_PUBLIC_FRONTEND_URL}/dashboard/${userId}/analysis/${publicApiKey}`);
    }

  return (
    <Button variant="outline" onClick={getUserId}>
        Visit Analysis Site
    </Button>
  )
}