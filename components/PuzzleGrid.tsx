'use client'

import { useEffect, useState } from 'react'
import { getDailyPuzzle } from '@/app/api/puzzles'
import type { Puzzle, Clue } from '@/types'

export default function PuzzleGrid() {
  const [puzzle, setPuzzle] = useState<Puzzle | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function loadPuzzle() {
      try {
        const data = await getDailyPuzzle()
        setPuzzle(data)
      } catch (err) {
        console.error('Error loading puzzle:', err)
        setError('Failed to load puzzle')
      } finally {
        setLoading(false)
      }
    }

    loadPuzzle()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin">Loading puzzle...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-red-500 p-4">
        {error}
      </div>
    )
  }

  if (!puzzle) {
    return (
      <div className="text-gray-500 p-4">
        No puzzle available
      </div>
    )
  }

  // Parse grid data from string to 2D array
  const gridData = JSON.parse(puzzle.grid) as string[][]

  return (
    <div className="max-w-4xl mx-auto p-4">
      <div className="mb-6">
        <h2 className="text-2xl font-bold mb-2">Daily Puzzle</h2>
        <div className="text-gray-600">By {puzzle.author}</div>
        <div className="text-gray-600">Published: {new Date(puzzle.date_published).toLocaleDateString()}</div>
      </div>

      {/* Grid */}
      <div className="mb-8">
        <div className="grid gap-px bg-gray-200" 
             style={{ 
               gridTemplateColumns: `repeat(${gridData[0].length}, minmax(0, 1fr))` 
             }}>
          {gridData.map((row, i) => 
            row.map((cell, j) => (
              <div key={`${i}-${j}`} 
                   className={`aspect-square flex items-center justify-center
                             ${cell === '.' ? 'bg-black' : 'bg-white'}`}>
                {cell !== '.' && cell}
              </div>
            ))
          )}
        </div>
      </div>

      {/* Clues */}
      <div className="grid md:grid-cols-2 gap-8">
        {/* Across Clues */}
        <div>
          <h3 className="font-bold mb-4">Across</h3>
          <div className="space-y-2">
            {puzzle.clues
              .filter(clue => clue.direction === 'across')
              .map(clue => (
                <div key={`across-${clue.number}`} className="flex gap-2">
                  <span className="font-medium w-8">{clue.number}.</span>
                  <span>{clue.text}</span>
                </div>
              ))}
          </div>
        </div>

        {/* Down Clues */}
        <div>
          <h3 className="font-bold mb-4">Down</h3>
          <div className="space-y-2">
            {puzzle.clues
              .filter(clue => clue.direction === 'down')
              .map(clue => (
                <div key={`down-${clue.number}`} className="flex gap-2">
                  <span className="font-medium w-8">{clue.number}.</span>
                  <span>{clue.text}</span>
                </div>
              ))}
          </div>
        </div>
      </div>
    </div>
  )
}