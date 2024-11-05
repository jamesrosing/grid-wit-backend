export interface Clue {
  number: number
  direction: 'across' | 'down'
  text: string
  answer: string
  row: number
  column: number
}

export interface Puzzle {
  id: number
  date_published: string
  author: string
  grid: string  // JSON string of 15x15 array
  clues: Clue[]
}

export interface Cell {
  value: string
  number?: number
  isBlack: boolean
  row: number
  col: number
  isStart: {
    across: boolean
    down: boolean
  }
}

export interface GridPosition {
  row: number
  col: number
}

export interface ActiveCell extends GridPosition {
  direction: 'across' | 'down'
}

export const GRID_SIZE = 15  // Standard crossword size 