"use client";

import {use, useEffect, useRef} from 'react';
import { useUser } from '@clerk/nextjs';
import { auth } from '@clerk/nextjs/server';

export default function RegisterUserOnSignIn() {
    // Send user email to /register_user in the backend to talk to Supabase
    const { user, isLoaded, isSignedIn } = useUser();

    useEffect(() => {
        // Ensure the user has signed in
        if (!isLoaded && !isSignedIn && !user) {
            return;
        }

        const run = async () => {
            // Ensure user is real
            if (user == null) {
                console.warn('User is null, cannot register');
                return;
            }

            // Grab email from Clerk
            const email = user.primaryEmailAddress?.emailAddress;

            // Grab user ID from Clerk
            const id = user.id;

            // Ensure email is real
            if (email == null) {
                console.warn('User email is null, cannot register');
                return;
            }

            // Ensure Clerk user ID is real
            if (id == null) {
                console.warn('Clerk user ID is null, cannot register');
                return;
            }

            // Try to register user in our backend to send and check with supabase
            try {
                const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/register_user`, {
                    method: 'POST',
                    headers: {
                    'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email, id }),
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