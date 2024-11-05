// Define types for the API responses
interface Clue {
  number: number
  direction: string
  text: string
  answer: string
  row: number
  column: number
}

interface Puzzle {
  id: number
  date_published: string
  author: string
  grid: string
  clues: Clue[]
}

interface PuzzleResponse {
  puzzles: Puzzle[]
  total: number
  page: number
  per_page: number
  total_pages: number
}

// API client functions
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'

export async function getPuzzles(page: number = 1, perPage: number = 10): Promise<PuzzleResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/puzzles?page=${page}&per_page=${perPage}`
  )
  if (!response.ok) {
    throw new Error('Failed to fetch puzzles')
  }
  return response.json()
}

export async function getDailyPuzzle(): Promise<Puzzle> {
  const response = await fetch(`${API_BASE_URL}/api/puzzles/daily`)
  if (!response.ok) {
    throw new Error('Failed to fetch daily puzzle')
  }
  const data = await response.json()
  return {
    ...data,
    clues: data.clues || [] // Ensure clues is always an array
  }
}

interface SearchParams {
  author?: string
  date?: string
  word?: string
  clue?: string
}

export async function searchPuzzles(params: SearchParams): Promise<PuzzleResponse> {
  const queryString = new URLSearchParams(
    Object.entries(params).filter(([_, value]) => value != null) as [string, string][]
  ).toString()
  
  const response = await fetch(
    `${API_BASE_URL}/api/puzzles/search?${queryString}`
  )
  if (!response.ok) {
    throw new Error('Failed to search puzzles')
  }
  return response.json()
} 