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

export function ConfirmDeleteProjects({
    projects,
    open,
    onOpenChange
} : {
    projects: Array<{domain: string, name: string, project_api_key: string}>
    open: boolean
    onOpenChange: (open: boolean) => void
}) {
    console.log(projects)

    async function deleteSelectedRows() {
        const apiKeysToDelete = projects.map(project => project.project_api_key)

        try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/delete_projects`, {
            method: 'POST',
            headers: {
            'Content-Type': 'application/json',
            },
            body: JSON.stringify({ project_api_keys: apiKeysToDelete }),
        })
        } catch (error) {
        console.error("Error deleting projects:", error)
        }
        // Refresh the page to reflect deletions
        window.location.reload()
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <form>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Confirm Delete</DialogTitle>
            <DialogDescription>
              Please confirm you want to delete the following projects:
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4">
            <ul className="list-disc ml-5 mt-2">
                {projects.map((project) => (
                    <li key={project.project_api_key}>{project.name} ({project.domain}) - {project.project_api_key}</li>
                ))}
            </ul>
          </div>
          <DialogFooter>
            <DialogClose asChild>
              <Button variant="outline">Cancel</Button>
            </DialogClose>
            <Button type="submit" variant="destructive" onClick={deleteSelectedRows}>Delete</Button>
          </DialogFooter>
        </DialogContent>
      </form>
    </Dialog>
  )
}
