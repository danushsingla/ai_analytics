import { Button } from "@/Components/ui/button"
import Link from "next/link"
import { auth } from '@clerk/nextjs/server';

type VisitAnalysisSiteButtonProps = {
    publicApiKey: string;
}

export default async function VisitAnalysisSiteButton({
    publicApiKey,
}: VisitAnalysisSiteButtonProps) {
    // Grab userId for page redirect
    const { userId } = await auth();
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
    href = (`${process.env.NEXT_PUBLIC_FRONTEND_URL}/dashboard/${userId}/analysis/${publicApiKey}`);

  return (
    <div>
        <Button asChild variant="outline">
            <Link href={href}>Visit Analysis Site</Link>
        </Button>
    </div>
  )
}