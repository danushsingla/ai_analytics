"use client";

import {use, useEffect, useRef} from 'react';
import { useUser } from '@clerk/nextjs';

export default function RegisterUserOnSignIn() {
    // Send user email to /register_user in the backend to talk to Supabase
    const { user, isLoaded, isSignedIn } = useUser();

    useEffect(() => {
        if (!isLoaded && !isSignedIn && !user) {
            return;
        }

        const run = async () => {
            if (user == null) {
                console.warn('User is null, cannot register');
                return;
            }
            const email = user.primaryEmailAddress?.emailAddress;

            if (email == null) {
                console.warn('User email is null, cannot register');
                return;
            }
            
            try {
                const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/register_user`, {
                    method: 'POST',
                    headers: {
                    'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email }),
                });

                if (!res.ok) {
                    const text = await res.text();
                    throw new Error(`Failed to register user: ${text}`);
                }
            } catch (error) {
                console.error('Error registering user:', error);
            }
        }

        run();
    }, [isLoaded, isSignedIn, user]);

    return null;
}