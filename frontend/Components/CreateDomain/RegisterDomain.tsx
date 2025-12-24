"use client"

import { CreateDomainSheet } from '@/Components/CreateDomain/CreateDomainSheet';
import { useState } from 'react';

export default function RegisterDomain() {
    const [openCreateDomainSheet, setOpenCreateDomainSheet] = useState(false);

    return (
        <>
            <button className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600" onClick={() => setOpenCreateDomainSheet(true)}>
                Add New Domain
            </button>

            <CreateDomainSheet open={openCreateDomainSheet} onOpenChange={setOpenCreateDomainSheet} />
        </>
    )
}