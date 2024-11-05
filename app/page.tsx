'use client'

import { useEffect, useState } from 'react'
import { getDailyPuzzle } from '@/lib/api'
import { CrosswordGrid } from '@/components/CrosswordGrid'
import { ClueList } from '@/components/ClueList'
import type { Puzzle, Clue, ActiveCell } from '@/types'

export default function CrosswordPage() {
  const [puzzle, setPuzzle] = useState<Puzzle | null>(null)
  const [activeCell, setActiveCell] = useState<ActiveCell | null>(null)
  const [activeClue, setActiveClue] = useState<Clue | null>(null)
  const [userProgress, setUserProgress] = useState<string[][]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function loadPuzzle() {
      try {
        setLoading(true)
        const data = await getDailyPuzzle()
        
        // Initialize puzzle state
        setPuzzle(data)
        setUserProgress(Array(15).fill(null).map(() => Array(15).fill('')))
        
        // Load saved progress if exists
        const savedProgress = localStorage.getItem('puzzleProgress')
        if (savedProgress) {
          setUserProgress(JSON.parse(savedProgress))
        }
      } catch (err) {
        console.error('Error loading puzzle:', err)
        setError('Failed to load puzzle')
      } finally {
        setLoading(false)
      }
    }
    loadPuzzle()
  }, [])

  useEffect(() => {
    // Save progress whenever it changes
    if (userProgress.length > 0 && puzzle?.id) {
      localStorage.setItem(`puzzle-progress-${puzzle.id}`, JSON.stringify(userProgress))
    }
  }, [userProgress, puzzle?.id])

  const handleCellSelect = (row: number, col: number, direction: 'across' | 'down') => {
    if (!puzzle) return

    setActiveCell({ row, col, direction })
    
    // Find corresponding clue
    const gridIndex = row * 15 + col
    const cell = puzzle.grid[gridIndex]
    
    if (cell !== '.') {
      const clue = puzzle.clues.find(c => 
        c.direction === direction && 
        (c.row === row && c.column === col || // Starts here
         (direction === 'across' && c.row === row && c.column <= col) || // Part of across word
         (direction === 'down' && c.column === col && c.row <= row)) // Part of down word
      )
      
      if (clue) {
        setActiveClue(clue)
      }
    }
  }

  const handleUpdateProgress = (row: number, col: number, value: string) => {
    setUserProgress(prev => {
      const newProgress = prev.map(r => [...r])
      newProgress[row][col] = value
      return newProgress
    })
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  if (error || !puzzle) {
    return (
      <div className="flex items-center justify-center min-h-screen text-red-500">
        {error || 'No puzzle available'}
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto p-4">
      <div className="grid grid-cols-1 lg:grid-cols-[1fr,400px] gap-8">
        {/* Crossword Grid */}
        <div className="order-2 lg:order-1">
          {activeClue && (
            <div className="mb-4 p-4 bg-blue-50 rounded">
              <span className="font-bold mr-2">{activeClue.number}.</span>
              {activeClue.text}
            </div>
          )}
          <CrosswordGrid
            puzzle={puzzle}
            activeCell={activeCell}
            onCellSelect={handleCellSelect}
            userProgress={userProgress}
            onUpdateProgress={handleUpdateProgress}
          />
        </div>

        {/* Clue Lists */}
        <div className="order-1 lg:order-2 bg-white p-4 rounded shadow-lg">
          <ClueList
            clues={puzzle.clues}
            activeClue={activeClue}
            onClueSelect={(clue) => {
              setActiveClue(clue)
              setActiveCell({
                row: clue.row,
                column: clue.column,
                direction: clue.direction
              })
            }}
          />
        </div>
      </div>
    </div>
  )
} 