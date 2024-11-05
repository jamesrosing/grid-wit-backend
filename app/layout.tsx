import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Grid Wit - Daily Crossword Puzzle',
  description: 'Challenge yourself with our daily crossword puzzle',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} min-h-screen bg-gray-50`}>
        <main className="container mx-auto px-4 py-8">
          <header className="mb-8">
            <h1 className="text-3xl font-bold text-center text-gray-800">
              Grid Wit
            </h1>
            <p className="text-center text-gray-600">
              Daily Crossword Puzzle
            </p>
          </header>
          {children}
        </main>
      </body>
    </html>
  )
} 