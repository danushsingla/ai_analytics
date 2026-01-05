import { auth } from "@clerk/nextjs/server";
import { redirect } from 'next/navigation';

export default async function Home() {
  const { userId } = await auth();

  if (userId) {
    // If the user is signed in, redirect to the dashboard
    redirect('/dashboard');
  }

  return (
    <main className="flex flex-col items-center justify-center p-4">
      <h1 className="text-4xl font-bold mb-8">Welcome to AIAnalytics</h1>
      <p className="text-lg text-center max-w-2xl">
        Please sign in with a valid email to access your analytics dashboard.
      </p>
    </main>
  );
}
