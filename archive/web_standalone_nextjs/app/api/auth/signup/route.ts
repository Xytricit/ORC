import { NextRequest, NextResponse } from 'next/server'
import { createUser, createSession } from '@/lib/auth'

export async function POST(request: NextRequest) {
  try {
    const { username, email, password } = await request.json()

    // Validation
    if (!username || !email || !password) {
      return NextResponse.json(
        { error: 'All fields are required' },
        { status: 400 }
      )
    }

    if (password.length < 8) {
      return NextResponse.json(
        { error: 'Password must be at least 8 characters' },
        { status: 400 }
      )
    }

    const user = await createUser(username, email, password)
    await createSession(user.id)

    return NextResponse.json({ success: true, user })
  } catch (error: any) {
    console.error('Signup error:', error)
    
    if (error.message === 'User already exists') {
      return NextResponse.json(
        { error: 'Username or email already exists' },
        { status: 400 }
      )
    }

    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
