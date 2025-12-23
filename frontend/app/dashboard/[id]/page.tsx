import { redirect } from 'next/navigation';

type PageProps = {
  params: Promise<{ id: string }>;
};

export default async function DashboardPage({ params }: Readonly<PageProps>) {
    // Supabase user ID from the URL
    const { id } = await params;
    const userId = id;

    if (!userId) {
        redirect('/');
    }

    return (
        <div>
            <h1>Dashboard for User ID: {userId}</h1>
        </div>
    );
}