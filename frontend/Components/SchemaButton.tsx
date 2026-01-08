"use client";

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
import { Input } from "@/Components/ui/input"
import { Label } from "@/Components/ui/label"

import { useState, useEffect } from "react";

import { toast } from "sonner";

export default function SchemaButton({checked, public_api_key, url}: {checked: boolean; public_api_key?: string; url?: string}) {
    if (!public_api_key || !url) {
        return null;
    }

    const [userMessage, setUserMessage] = useState("");
    const [aiResponse, setAiResponse] = useState("");
    
    // Function to get current schema from backend
    useEffect(() => {
        if(!public_api_key || !url) {
            return;
        }
        
        // Fetch current schema
        fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/get_schema?public_api_key=${encodeURIComponent(public_api_key)}&url=${encodeURIComponent(url)}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        }).then(async (res) => {
            if (res.ok) {
                const data = await res.json();
                // Use data.message_paths to set initial values if needed
                setUserMessage(data.user_request || "");
                setAiResponse(data.ai_response || "");
            } else {
                console.error('Failed to fetch message paths');
            }
        });

    }, [public_api_key, url]);

    async function saveChanges() {
        if(!public_api_key || !url) {
            return;
        }
        
        // Save the updated schema to backend
        const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/set_schema?public_api_key=${encodeURIComponent(public_api_key)}&url=${encodeURIComponent(url)}&user_request_path=${encodeURIComponent(userMessage)}&ai_response_path=${encodeURIComponent(aiResponse)}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (!res.ok) {
            toast.error("Failed to save message paths");
        } else {
            toast.success("Message paths saved successfully!");
        }
    }

  return (
    <Dialog>
      <form>
        <DialogTrigger asChild>
          <Button variant="outline">View Message Paths</Button>
        </DialogTrigger>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Change message paths</DialogTitle>
            <DialogDescription>
                Change the paths from which messages are extracted for both your request and response to this endpoint.
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4">
            <div className="grid gap-3">
              <Label htmlFor="name-1">Request Path</Label>
              <Input id="name-1" name="name" defaultValue={userMessage} onChange={(e) => setUserMessage(e.target.value)} />
            </div>
            <div className="grid gap-3">
              <Label htmlFor="username-1">Response Path</Label>
              <Input id="username-1" name="username" defaultValue={aiResponse} onChange={(e) => setAiResponse(e.target.value)} />
            </div>
          </div>
          <DialogFooter>
            <DialogClose asChild>
              <Button variant="outline">Cancel</Button>
            </DialogClose>
            <DialogClose asChild>
                <Button type="submit" onClick={saveChanges}>Save changes</Button>
            </DialogClose>
          </DialogFooter>
        </DialogContent>
      </form>
    </Dialog>
  )
}