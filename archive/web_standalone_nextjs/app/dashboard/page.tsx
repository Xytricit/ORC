import { redirect } from 'next/navigation'
import { getSession, getUser } from '@/lib/auth'
import DashboardClient from './DashboardClient'

export default async function DashboardPage() {
  const session = await getSession()

  if (!session) {
    redirect('/auth/signin')
  }

  const user = await getUser(session.userId)

  if (!user) {
    redirect('/auth/signin')
  }

  return <DashboardClient user={user} />
}
