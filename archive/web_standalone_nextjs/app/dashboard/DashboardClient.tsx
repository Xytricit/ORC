'use client'

import { useRouter } from 'next/navigation'
import Image from 'next/image'
import styles from '../../styles/dashboard.module.css'

interface User {
  id: string
  username: string
  email: string
}

export default function DashboardClient({ user }: { user: User }) {
  const router = useRouter()

  const handleSignout = async () => {
    try {
      await fetch('/api/auth/signout', { method: 'POST' })
      router.push('/')
    } catch (error) {
      console.error('Signout failed:', error)
    }
  }

  return (
    <div className={styles.dashboardContainer}>
      {/* Sidebar */}
      <aside className={styles.sidebar}>
        <div className={styles.sidebarHeader}>
          <Image 
            src="/images/orclogo.png" 
            alt="ORC Logo" 
            width={32} 
            height={32}
          />
          <span className={styles.sidebarTitle}>ORC</span>
        </div>

        <div className={styles.sidebarStats}>
          <div className={styles.statsTitle}>Quick Stats</div>
          <div className={styles.statsGrid}>
            <div className={styles.statItem}>
              <div className={styles.statValue}>0</div>
              <div className={styles.statLabel}>Files</div>
            </div>
            <div className={styles.statItem}>
              <div className={styles.statValue}>0</div>
              <div className={styles.statLabel}>Analyses</div>
            </div>
          </div>
        </div>

        <nav className={styles.sidebarNav}>
          <div className={styles.navSection}>
            <ul className={styles.navList}>
              <li className={styles.navItem}>
                <a href="#" className={`${styles.navLink} ${styles.active}`}>
                  <span className={styles.navIcon}>DH</span>
                  <span className={styles.navText}>Dashboard</span>
                </a>
              </li>
              <li className={styles.navItem}>
                <a href="#" className={styles.navLink}>
                  <span className={styles.navIcon}>PR</span>
                  <span className={styles.navText}>Projects</span>
                </a>
              </li>
              <li className={styles.navItem}>
                <a href="#" className={styles.navLink}>
                  <span className={styles.navIcon}>ST</span>
                  <span className={styles.navText}>Statistics</span>
                </a>
              </li>
              <li className={styles.navItem}>
                <a href="#" className={styles.navLink}>
                  <span className={styles.navIcon}>AI</span>
                  <span className={styles.navText}>AI Assistant</span>
                </a>
              </li>
            </ul>
          </div>
        </nav>

        <div className={styles.sidebarUser}>
          <div className={styles.userInfo}>
            <div className={styles.userAvatar}>{user.username[0].toUpperCase()}</div>
            <div className={styles.userDetails}>
              <div className={styles.userName}>{user.username}</div>
              <div className={styles.userEmail}>{user.email}</div>
            </div>
          </div>
          <button onClick={handleSignout} className={styles.signoutButton}>
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className={styles.mainContent}>
        <header className={styles.dashboardHeader}>
          <h1 className={styles.pageTitle}>Dashboard</h1>
          <p className={styles.pageSubtitle}>Welcome back, {user.username}!</p>
        </header>

        <div className={styles.dashboardGrid}>
          {/* Summary Cards */}
          <div className={styles.summaryCard}>
            <div className={styles.cardIcon}>📁</div>
            <div className={styles.cardContent}>
              <div className={styles.cardValue}>0</div>
              <div className={styles.cardLabel}>Total Projects</div>
            </div>
          </div>

          <div className={styles.summaryCard}>
            <div className={styles.cardIcon}>📊</div>
            <div className={styles.cardContent}>
              <div className={styles.cardValue}>0</div>
              <div className={styles.cardLabel}>Analyses Run</div>
            </div>
          </div>

          <div className={styles.summaryCard}>
            <div className={styles.cardIcon}>🐛</div>
            <div className={styles.cardContent}>
              <div className={styles.cardValue}>0</div>
              <div className={styles.cardLabel}>Issues Found</div>
            </div>
          </div>

          <div className={styles.summaryCard}>
            <div className={styles.cardIcon}>⚡</div>
            <div className={styles.cardContent}>
              <div className={styles.cardValue}>0</div>
              <div className={styles.cardLabel}>Optimizations</div>
            </div>
          </div>
        </div>

        {/* Getting Started */}
        <div className={styles.gettingStarted}>
          <h2 className={styles.sectionTitle}>Getting Started</h2>
          <div className={styles.stepsList}>
            <div className={styles.stepCard}>
              <div className={styles.stepNumber}>1</div>
              <div className={styles.stepContent}>
                <h3 className={styles.stepTitle}>Create a Project</h3>
                <p className={styles.stepDescription}>
                  Add your first codebase to start analyzing
                </p>
                <button className={styles.stepButton}>Create Project</button>
              </div>
            </div>

            <div className={styles.stepCard}>
              <div className={styles.stepNumber}>2</div>
              <div className={styles.stepContent}>
                <h3 className={styles.stepTitle}>Run Analysis</h3>
                <p className={styles.stepDescription}>
                  Let ORC analyze your code for issues and optimizations
                </p>
              </div>
            </div>

            <div className={styles.stepCard}>
              <div className={styles.stepNumber}>3</div>
              <div className={styles.stepContent}>
                <h3 className={styles.stepTitle}>Get Insights</h3>
                <p className={styles.stepDescription}>
                  View detailed reports and AI-powered suggestions
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
