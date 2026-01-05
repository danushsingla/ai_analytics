"use client"

import { Button } from "@/Components/ui/button"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/Components/ui/dialog"
import { Label } from "@/Components/ui/label"
import { useUser } from "@clerk/nextjs"
import { useEffect, useState } from "react"
import { Textarea } from "@/Components/ui/textarea"

export function CopyCard({
  open,
  onOpenChange,
  domain,
  name
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  domain: string
  name: string
}) {
    // Grab user id
    const { user, isLoaded, isSignedIn } = useUser();

    // Ensure user is loaded and signed in
    if (!isLoaded || !isSignedIn || !user) {
      return null;
    }

    const userId = user.id;

    const [copied, setCopied] = useState(false);
    const [apiKey, setApiKey] = useState("");
    const [loadingKey, setLoadingKey] = useState(false);

    async function copyToClipboard(snippet: string) {
        await navigator.clipboard.writeText(snippet)
        setCopied(true)
        setTimeout(() => setCopied(false), 1500)
    }

    async function getProjectInfo() {
        setLoadingKey(true);
        const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/get_project_copy_card`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ user_id: userId, domain: domain, name: name }),
        });
        if (res.ok) {
            const data = await res.json();
            setApiKey(data.public_api_key);
        }
        setLoadingKey(false);
    }

    // Fetch API key when dialog opens
    useEffect(() => {
        if (open) {
            getProjectInfo();
        }
    }, [open, domain, name, userId]);

    // Snippets to be copied
    const snippetOne = `<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
                new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
                j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
                'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
                })(window,document,'script','dataLayer','GTM-K4SQR86R');</script>
                        <script src="https://ai-analytics-7tka.onrender.com/gtmtracker.js"
                public-api-key="${apiKey}"></script>`;
    
    const snippetTwo = `<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-K4SQR86R"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>`
    
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <form>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Project Successfully Created</DialogTitle>
            <DialogDescription>
                Your domain has been registered successfully. Here is your api key: <strong>{apiKey}</strong>
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4">
            <div className="grid gap-3">
              <Label htmlFor="name-1">Please copy the following as high in the &lt;head&gt; as possible of your frontend</Label>
              <Textarea readOnly
                className="min-h-[120px] resize-none border-0 bg-transparent font-mono text-sm focus-visible:ring-0"
                onClick={(e) => (e.target as HTMLTextAreaElement).select()}
                value = {loadingKey ? "Loading..." :snippetOne}
              />

                  <Button
                    size="sm"
                    variant="secondary"
                    className="bottom"
                    onClick={() => copyToClipboard(snippetOne)}
                    >
                    {copied ? "Copied!" : "Copy"}
                </Button>
                <Label htmlFor="name-1">Please copy the following just after the opening &lt;body&gt; tag your frontend</Label>
              <Textarea readOnly
                className="min-h-[120px] resize-none border-0 bg-transparent font-mono text-sm focus-visible:ring-0"
                onClick={(e) => (e.target as HTMLTextAreaElement).select()}
                value = {snippetTwo}
              />

                  <Button
                    size="sm"
                    variant="secondary"
                    className="bottom"
                    onClick={() => copyToClipboard(snippetTwo)}
                    >
                    {copied ? "Copied!" : "Copy"}
                </Button>
            </div>
          </div>
        </DialogContent>
      </form>
    </Dialog>
  )
}
