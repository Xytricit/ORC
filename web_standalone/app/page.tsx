'use client'

import Link from 'next/link'
import Image from 'next/image'
import styles from '../styles/landing.module.css'

export default function LandingPage() {
  return (
    <div className={styles.landingContainer}>
      {/* Header */}
      <header className={styles.header}>
        <div className={styles.headerContent}>
          <div className={styles.logo}>
            <Image 
              src="/images/orclogo.png" 
              alt="ORC Logo" 
              width={40} 
              height={40}
            />
            <span className={styles.logoText}>ORC</span>
          </div>
          <nav className={styles.nav}>
            <Link href="/auth/signin" className={styles.navLink}>
              Sign In
            </Link>
            <Link href="/auth/signup" className={styles.navButton}>
              Get Started
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <main className={styles.main}>
        <div className={styles.hero}>
          <h1 className={styles.heroTitle}>
            Optimize Your Code with <span className={styles.highlight}>AI</span>
          </h1>
          <p className={styles.heroSubtitle}>
            ORC is an AI-powered code analysis and optimization tool that helps you write better, 
            faster, and more maintainable code.
          </p>
          <div className={styles.heroButtons}>
            <Link href="/auth/signup" className={styles.primaryButton}>
              Start Free Trial
            </Link>
            <Link href="#features" className={styles.secondaryButton}>
              Learn More
            </Link>
          </div>
        </div>

        {/* Features Section */}
        <div id="features" className={styles.features}>
          <h2 className={styles.sectionTitle}>Why Choose ORC?</h2>
          <div className={styles.featureGrid}>
            <div className={styles.featureCard}>
              <div className={styles.featureIcon}>🔍</div>
              <h3 className={styles.featureTitle}>Code Analysis</h3>
              <p className={styles.featureDescription}>
                Deep code analysis to find bugs, vulnerabilities, and performance issues.
              </p>
            </div>
            <div className={styles.featureCard}>
              <div className={styles.featureIcon}>🤖</div>
              <h3 className={styles.featureTitle}>AI-Powered</h3>
              <p className={styles.featureDescription}>
                Leverage AI to get intelligent suggestions and automated refactoring.
              </p>
            </div>
            <div className={styles.featureCard}>
              <div className={styles.featureIcon}>⚡</div>
              <h3 className={styles.featureTitle}>Fast & Efficient</h3>
              <p className={styles.featureDescription}>
                Analyze thousands of lines of code in seconds with our optimized engine.
              </p>
            </div>
            <div className={styles.featureCard}>
              <div className={styles.featureIcon}>📊</div>
              <h3 className={styles.featureTitle}>Visual Insights</h3>
              <p className={styles.featureDescription}>
                Beautiful dashboards and visualizations to understand your codebase.
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className={styles.footer}>
        <p>&copy; 2026 ORC. Made with 💚 by developers, for developers.</p>
      </footer>
    </div>
  )
}
