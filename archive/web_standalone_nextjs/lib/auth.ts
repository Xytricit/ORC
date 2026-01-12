import bcrypt from 'bcryptjs'
import { cookies } from 'next/headers'

// Simple in-memory user store (in production, use a database)
const users: Map<string, {
  id: string
  username: string
  email: string
  passwordHash: string
}> = new Map()

// Session store
const sessions: Map<string, {
  userId: string
  expiresAt: number
}> = new Map()

export async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, 10)
}

export async function verifyPassword(password: string, hash: string): Promise<boolean> {
  return bcrypt.compare(password, hash)
}

export function generateSessionToken(): string {
  return Math.random().toString(36).substring(2) + Date.now().toString(36)
}

export async function createUser(username: string, email: string, password: string) {
  // Check if user exists
  for (const user of users.values()) {
    if (user.username === username || user.email === email) {
      throw new Error('User already exists')
    }
  }

  const userId = Date.now().toString()
  const passwordHash = await hashPassword(password)

  const user = {
    id: userId,
    username,
    email,
    passwordHash,
  }

  users.set(userId, user)
  return { id: userId, username, email }
}

export async function authenticateUser(usernameOrEmail: string, password: string) {
  for (const user of users.values()) {
    if (user.username === usernameOrEmail || user.email === usernameOrEmail) {
      const valid = await verifyPassword(password, user.passwordHash)
      if (valid) {
        return { id: user.id, username: user.username, email: user.email }
      }
    }
  }
  return null
}

export async function createSession(userId: string): Promise<string> {
  const token = generateSessionToken()
  const expiresAt = Date.now() + (7 * 24 * 60 * 60 * 1000) // 7 days

  sessions.set(token, { userId, expiresAt })

  // Set cookie
  const cookieStore = cookies()
  cookieStore.set('session', token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: 7 * 24 * 60 * 60, // 7 days
    path: '/',
  })

  return token
}

export async function getSession(): Promise<{ userId: string } | null> {
  const cookieStore = cookies()
  const token = cookieStore.get('session')?.value

  if (!token) return null

  const session = sessions.get(token)
  if (!session) return null

  // Check if expired
  if (Date.now() > session.expiresAt) {
    sessions.delete(token)
    return null
  }

  return { userId: session.userId }
}

export async function deleteSession(): Promise<void> {
  const cookieStore = cookies()
  const token = cookieStore.get('session')?.value

  if (token) {
    sessions.delete(token)
  }

  cookieStore.delete('session')
}

export async function getUser(userId: string) {
  const user = users.get(userId)
  if (!user) return null

  return {
    id: user.id,
    username: user.username,
    email: user.email,
  }
}
