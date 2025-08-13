import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Navbar from './components/Navbar'
import HomePage from './pages/HomePage'
import TeamsPage from './pages/TeamsPage'
import MatchSimulator from './pages/MatchSimulator'
import TournamentPage from './pages/TournamentPage'
import StatsPage from './pages/StatsPage'
import './App.css'

const App: React.FC = () => {
  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-football-green via-primary-600 to-football-darkgreen">
        <Navbar />
        <main className="pt-16">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/teams" element={<TeamsPage />} />
            <Route path="/simulator" element={<MatchSimulator />} />
            <Route path="/tournament" element={<TournamentPage />} />
            <Route path="/stats" element={<StatsPage />} />
          </Routes>
        </main>
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 3000,
            style: {
              background: '#1f2937',
              color: '#fff',
              border: '1px solid #22c55e',
            },
          }}
        />
      </div>
    </Router>
  )
}

export default App
