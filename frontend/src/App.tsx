import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Navbar from './components/Navbar'
import HomePage from './pages/HomePage'
import TeamsPage from './pages/TeamsPage'
import MatchSimulator from './pages/MatchSimulator'
import TournamentPage from './pages/TournamentPage'
import StatsPage from './pages/StatsPage'
import PredictionsPage from './pages/PredictionsPage'
import './App.css'

const App: React.FC = () => {
  return (
    <Router>
      <div className="min-h-screen">
        <Navbar />
        <main className="pt-16">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/teams" element={<TeamsPage />} />
            <Route path="/simulator" element={<MatchSimulator />} />
            <Route path="/predictions" element={<PredictionsPage />} />
            <Route path="/tournament" element={<TournamentPage />} />
            <Route path="/stats" element={<StatsPage />} />
          </Routes>
        </main>
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 3000,
            style: {
              background: 'rgba(6, 25, 16, 0.95)',
              color: '#d1fae5',
              border: '1px solid rgba(16, 185, 129, 0.4)',
              backdropFilter: 'blur(8px)',
            },
          }}
        />
      </div>
    </Router>
  )
}

export default App
