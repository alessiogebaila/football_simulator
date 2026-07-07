import React, { useState, useEffect } from 'react'
import { Trophy, Star, Users, Play, X, Zap, Clock } from 'lucide-react'
import { Team } from '../types'
import api from '../services/api'
import toast from 'react-hot-toast'
import TournamentMatchSimulator from '../components/TournamentMatchSimulator'

interface BracketMatch {
  id: string
  homeTeam: string | null
  awayTeam: string | null
  winner: string | null
  homeScore: number
  awayScore: number
  round: number
  matchIndex: number
  isPlayed: boolean
}

interface TournamentBracket {
  matches: BracketMatch[]
  teams: string[]
  currentRound: number
  totalRounds: number
  winner: string | null
}

const TournamentPage: React.FC = () => {
  const [teams, setTeams] = useState<Team[]>([])
  const [tournamentSize, setTournamentSize] = useState<4 | 8 | 16>(8)
  const [selectedTeams, setSelectedTeams] = useState<string[]>([])
  const [bracket, setBracket] = useState<TournamentBracket | null>(null)
  const [isSimulating, setIsSimulating] = useState(false)
  const [currentMatch, setCurrentMatch] = useState<BracketMatch | null>(null)
  const [showLiveMatch, setShowLiveMatch] = useState(false)
  const [simulationMode, setSimulationMode] = useState<'quick' | 'live'>('quick')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchTeams()
  }, [])

  useEffect(() => {
    // Auto-select random teams when tournament size changes
    if (teams.length > 0 && selectedTeams.length !== tournamentSize) {
      const shuffled = [...teams].sort(() => Math.random() - 0.5)
      setSelectedTeams(shuffled.slice(0, tournamentSize).map(t => t.name))
    }
  }, [tournamentSize, teams])

  const fetchTeams = async () => {
    try {
      const data = await api.getTeams()
      setTeams(data)
    } catch (error) {
      toast.error('Failed to fetch teams')
    } finally {
      setLoading(false)
    }
  }

  const createBracket = () => {
    if (selectedTeams.length !== tournamentSize) {
      toast.error(`Please select exactly ${tournamentSize} teams`)
      return
    }

    // Shuffle teams randomly
    const shuffledTeams = [...selectedTeams].sort(() => Math.random() - 0.5)
    const totalRounds = Math.log2(tournamentSize)
    const matches: BracketMatch[] = []

    // Create first round matches
    for (let i = 0; i < shuffledTeams.length; i += 2) {
      matches.push({
        id: `r1-m${i/2}`,
        homeTeam: shuffledTeams[i],
        awayTeam: shuffledTeams[i + 1],
        winner: null,
        homeScore: 0,
        awayScore: 0,
        round: 1,
        matchIndex: i / 2,
        isPlayed: false
      })
    }

    // Create subsequent round placeholders
    let matchesInPreviousRound = matches.length
    for (let round = 2; round <= totalRounds; round++) {
      const matchesInThisRound = matchesInPreviousRound / 2
      for (let i = 0; i < matchesInThisRound; i++) {
        matches.push({
          id: `r${round}-m${i}`,
          homeTeam: null,
          awayTeam: null,
          winner: null,
          homeScore: 0,
          awayScore: 0,
          round: round,
          matchIndex: i,
          isPlayed: false
        })
      }
      matchesInPreviousRound = matchesInThisRound
    }

    const newBracket: TournamentBracket = {
      matches,
      teams: shuffledTeams,
      currentRound: 1,
      totalRounds,
      winner: null
    }

    setBracket(newBracket)
    toast.success('Tournament bracket created!')
  }

  const simulateMatch = async (match: BracketMatch) => {
    if (!match.homeTeam || !match.awayTeam || match.isPlayed) return

    if (simulationMode === 'live') {
      // Show live match simulator
      setCurrentMatch(match)
      setShowLiveMatch(true)
      return
    }

    // Quick simulation
    setIsSimulating(true)

    try {
      const result = await api.simulateMatch(match.homeTeam, match.awayTeam)

      const updatedMatch: BracketMatch = {
        ...match,
        homeScore: result.home_score,
        awayScore: result.away_score,
        winner: result.home_score > result.away_score ? match.homeTeam : match.awayTeam,
        isPlayed: true
      }

      updateBracketWithResult(updatedMatch)
      toast.success(`${result.home_score > result.away_score ? match.homeTeam : match.awayTeam} wins ${result.home_score}-${result.away_score}!`)

    } catch (error) {
      toast.error('Failed to simulate match')
    } finally {
      setIsSimulating(false)
    }
  }

  const updateBracketWithResult = (updatedMatch: BracketMatch) => {
    setBracket(prev => {
      if (!prev) return null

      const updatedMatches = prev.matches.map(m => 
        m.id === updatedMatch.id ? updatedMatch : m
      )

      // Advance winner to next round
      advanceWinner(updatedMatches, updatedMatch)

      // Check if round is complete
      const currentRoundMatches = updatedMatches.filter(m => m.round === prev.currentRound)
      const allCurrentRoundPlayed = currentRoundMatches.every(m => m.isPlayed)
      
      let newCurrentRound = prev.currentRound
      let winner = prev.winner

      if (allCurrentRoundPlayed && prev.currentRound < prev.totalRounds) {
        newCurrentRound = prev.currentRound + 1
        toast.success(`Round ${prev.currentRound} completed!`)
      } else if (allCurrentRoundPlayed && prev.currentRound === prev.totalRounds) {
        // Tournament complete
        const finalMatch = updatedMatches.find(m => m.round === prev.totalRounds)
        winner = finalMatch?.winner || null
        toast.success(`🏆 Tournament completed! Winner: ${winner}`)
      }

      return {
        ...prev,
        matches: updatedMatches,
        currentRound: newCurrentRound,
        winner
      }
    })
  }

  const handleLiveMatchComplete = (result: { homeScore: number; awayScore: number; winner: string }) => {
    if (!currentMatch) return

    const updatedMatch: BracketMatch = {
      ...currentMatch,
      homeScore: result.homeScore,
      awayScore: result.awayScore,
      winner: result.winner,
      isPlayed: true
    }

    updateBracketWithResult(updatedMatch)
    setShowLiveMatch(false)
    setCurrentMatch(null)
  }

  const advanceWinner = (matches: BracketMatch[], completedMatch: BracketMatch) => {
    if (!completedMatch.winner || completedMatch.round === Math.log2(tournamentSize)) return

    const nextRound = completedMatch.round + 1
    const nextMatchIndex = Math.floor(completedMatch.matchIndex / 2)
    const nextMatch = matches.find(m => m.round === nextRound && m.matchIndex === nextMatchIndex)

    if (nextMatch) {
      if (completedMatch.matchIndex % 2 === 0) {
        // Even index goes to home team of next match
        nextMatch.homeTeam = completedMatch.winner
      } else {
        // Odd index goes to away team of next match
        nextMatch.awayTeam = completedMatch.winner
      }
    }
  }

  const simulateAllMatches = async () => {
    if (!bracket) return

    setIsSimulating(true)
    const unplayedMatches = bracket.matches.filter(m => 
      !m.isPlayed && m.homeTeam && m.awayTeam && m.round === bracket.currentRound
    )

    for (const match of unplayedMatches) {
      await simulateMatch(match)
      // Add small delay between matches
      await new Promise(resolve => setTimeout(resolve, 1000))
    }
    setIsSimulating(false)
  }

  const resetTournament = () => {
    setBracket(null)
    setCurrentMatch(null)
    toast.success('Tournament reset')
  }

  const toggleTeamSelection = (teamName: string) => {
    if (selectedTeams.length >= tournamentSize && !selectedTeams.includes(teamName)) {
      toast.error(`Maximum ${tournamentSize} teams allowed`)
      return
    }

    setSelectedTeams(prev => 
      prev.includes(teamName)
        ? prev.filter(t => t !== teamName)
        : [...prev, teamName]
    )
  }

  const getRoundName = (round: number, totalRounds: number) => {
    if (round === totalRounds) return 'Final'
    if (round === totalRounds - 1) return 'Semi-Final'
    if (round === totalRounds - 2) return 'Quarter-Final'
    return `Round ${round}`
  }

  const BracketVisualization: React.FC<{ bracket: TournamentBracket }> = ({ bracket }) => {
    const rounds: BracketMatch[][] = []
    
    // Group matches by round
    for (let round = 1; round <= bracket.totalRounds; round++) {
      rounds.push(bracket.matches.filter(m => m.round === round))
    }

    return (
      <div className="bg-gradient-to-br from-green-900/30 to-green-800/30 rounded-xl p-6 border border-green-500/30 overflow-x-auto">
        <div className="flex gap-8 min-w-max">
          {rounds.map((roundMatches, roundIndex) => (
            <div key={roundIndex} className="flex flex-col justify-center space-y-4">
              <h3 className="text-center text-white font-bold mb-4">
                {getRoundName(roundIndex + 1, bracket.totalRounds)}
              </h3>
              <div className={`flex flex-col justify-center space-y-${roundIndex === 0 ? '3' : roundIndex === 1 ? '6' : '12'}`}>
                {roundMatches.map((match, matchIndex) => (
                  <div key={match.id} className="relative">
                    {/* Match Card */}
                    <div className={`bg-gray-800/80 border rounded-lg p-3 min-w-[180px] ${
                      match.isPlayed 
                        ? 'border-green-500/50 bg-green-900/20' 
                        : match.homeTeam && match.awayTeam 
                          ? 'border-blue-500/50 bg-blue-900/20 cursor-pointer hover:bg-blue-900/30' 
                          : 'border-gray-600/50'
                    }`}
                    onClick={() => match.homeTeam && match.awayTeam && !match.isPlayed && simulateMatch(match)}
                    >
                      {/* Home Team */}
                      <div className={`flex justify-between items-center p-2 rounded ${
                        match.isPlayed && match.homeScore > match.awayScore ? 'bg-green-600/30' : ''
                      }`}>
                        <span className="text-white text-sm font-medium truncate">
                          {match.homeTeam || 'TBD'}
                        </span>
                        {match.isPlayed && (
                          <span className="text-white font-bold">{match.homeScore}</span>
                        )}
                      </div>
                      
                      <div className="border-t border-gray-600 my-1"></div>
                      
                      {/* Away Team */}
                      <div className={`flex justify-between items-center p-2 rounded ${
                        match.isPlayed && match.awayScore > match.homeScore ? 'bg-green-600/30' : ''
                      }`}>
                        <span className="text-white text-sm font-medium truncate">
                          {match.awayTeam || 'TBD'}
                        </span>
                        {match.isPlayed && (
                          <span className="text-white font-bold">{match.awayScore}</span>
                        )}
                      </div>

                      {/* Play Button */}
                      {match.homeTeam && match.awayTeam && !match.isPlayed && (
                        <div className="mt-2 text-center">
                          <button 
                            className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-xs"
                            onClick={(e) => {
                              e.stopPropagation()
                              simulateMatch(match)
                            }}
                          >
                            <Play size={12} className="inline mr-1" />
                            Play
                          </button>
                        </div>
                      )}
                    </div>

                    {/* Connection Lines */}
                    {roundIndex < rounds.length - 1 && (
                      <div className="absolute top-1/2 -right-8 w-8 h-0.5 bg-white/30"></div>
                    )}
                    {roundIndex < rounds.length - 1 && matchIndex % 2 === 0 && matchIndex < roundMatches.length - 1 && (
                      <>
                        <div className="absolute top-1/2 -right-8 w-0.5 h-8 bg-white/30"></div>
                        <div className="absolute top-1/2 -right-8 translate-y-8 w-0.5 h-8 bg-white/30"></div>
                      </>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}
          
          {/* Trophy for Winner */}
          {bracket.winner && (
            <div className="flex flex-col justify-center items-center ml-8">
              <div className="bg-gradient-to-b from-yellow-400 to-yellow-600 text-black p-6 rounded-full">
                <Trophy size={48} />
              </div>
              <div className="mt-4 text-center">
                <h3 className="text-yellow-400 font-bold text-lg">CHAMPION</h3>
                <p className="text-white font-semibold">{bracket.winner}</p>
              </div>
            </div>
          )}
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-500"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      {/* Live Match Modal */}
      {showLiveMatch && currentMatch && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-slate-800 rounded-lg w-full max-w-6xl max-h-[90vh] overflow-auto">
            <div className="p-4 border-b border-slate-700 flex items-center justify-between">
              <h2 className="text-xl font-bold text-white">
                Tournament Match: {currentMatch.homeTeam} vs {currentMatch.awayTeam}
              </h2>
              <button
                onClick={() => setShowLiveMatch(false)}
                className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-gray-400" />
              </button>
            </div>
            <TournamentMatchSimulator
              homeTeam={currentMatch.homeTeam!}
              awayTeam={currentMatch.awayTeam!}
              onMatchComplete={handleLiveMatchComplete}
            />
          </div>
        </div>
      )}

      {/* Header */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-white mb-4 flex items-center justify-center gap-3">
          <Trophy className="text-primary-400" />
          Tournament Bracket
        </h1>
        <p className="text-gray-300 text-lg">
          Create knockout tournaments with 4, 8, or 16 teams
        </p>
        <div className="mt-4 flex justify-center">
          <div className="flex items-center gap-2">
            <Zap className="w-5 h-5 text-blue-400" />
            <select
              value={simulationMode}
              onChange={(e) => setSimulationMode(e.target.value as 'quick' | 'live')}
              className="px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white"
            >
              <option value="quick">Quick Simulation</option>
              <option value="live">Live Simulation</option>
            </select>
          </div>
        </div>
      </div>

      {/* Tournament Setup */}
      {!bracket && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Tournament Configuration */}
          <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
            <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
              <Star className="text-primary-400" />
              Tournament Setup
            </h2>

            {/* Tournament Size Selection */}
            <div className="mb-6">
              <label className="block text-gray-300 text-sm font-medium mb-3">
                Tournament Size
              </label>
              <div className="grid grid-cols-3 gap-3">
                {[4, 8, 16].map(size => (
                  <button
                    key={size}
                    onClick={() => {
                      setTournamentSize(size as 4 | 8 | 16)
                      setSelectedTeams([])
                    }}
                    className={`py-3 px-4 rounded-lg font-medium transition-colors ${
                      tournamentSize === size
                        ? 'bg-primary-600 text-white'
                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                    }`}
                  >
                    {size} Teams
                  </button>
                ))}
              </div>
            </div>

            {/* Simulation Mode */}
            <div className="mb-6">
              <label className="block text-gray-300 text-sm font-medium mb-3">
                Simulation Mode
              </label>
              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={() => setSimulationMode('quick')}
                  className={`py-2 px-4 rounded-lg font-medium transition-colors ${
                    simulationMode === 'quick'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  <Clock size={16} className="inline mr-2" />
                  Quick
                </button>
                <button
                  onClick={() => setSimulationMode('live')}
                  className={`py-2 px-4 rounded-lg font-medium transition-colors ${
                    simulationMode === 'live'
                      ? 'bg-green-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  <Play size={16} className="inline mr-2" />
                  Live
                </button>
              </div>
            </div>

            {/* Create Tournament Button */}
            <button
              onClick={createBracket}
              disabled={selectedTeams.length !== tournamentSize}
              className="w-full bg-primary-600 hover:bg-primary-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white py-3 px-6 rounded-lg font-semibold transition-colors duration-200 flex items-center justify-center gap-2"
            >
              <Trophy size={20} />
              Create Tournament Bracket
            </button>
          </div>

          {/* Team Selection */}
          <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
            <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
              <Star className="text-primary-400" />
              Select Teams ({selectedTeams.length}/{tournamentSize})
            </h2>

            <div className="space-y-3 max-h-96 overflow-y-auto">
              {teams.map((team) => (
                <div
                  key={team.name}
                  onClick={() => toggleTeamSelection(team.name)}
                  className={`p-3 rounded-lg border cursor-pointer transition-all duration-200 ${
                    selectedTeams.includes(team.name)
                      ? 'bg-primary-600/20 border-primary-500'
                      : 'bg-gray-700/30 border-gray-600 hover:border-gray-500'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-white font-semibold text-sm">{team.name}</h3>
                      <p className="text-gray-400 text-xs">
                        {team.players.length} players
                      </p>
                    </div>
                    <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                      selectedTeams.includes(team.name)
                        ? 'bg-primary-500 border-primary-500'
                        : 'border-gray-400'
                    }`}>
                      {selectedTeams.includes(team.name) && (
                        <div className="w-2 h-2 bg-white rounded-full"></div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Tournament Bracket */}
      {bracket && (
        <div className="space-y-6">
          {/* Tournament Controls */}
          <div className="flex justify-center gap-4">
            <button
              onClick={simulateAllMatches}
              disabled={isSimulating || bracket.winner !== null}
              className="bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white py-2 px-6 rounded-lg font-semibold transition-colors duration-200 flex items-center gap-2"
            >
              {isSimulating ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Simulating...
                </>
              ) : (
                <>
                  <Play size={16} />
                  Simulate Round
                </>
              )}
            </button>
            <button
              onClick={resetTournament}
              className="bg-red-600 hover:bg-red-700 text-white py-2 px-6 rounded-lg font-semibold transition-colors duration-200"
            >
              Reset Tournament
            </button>
          </div>

          {/* Bracket Display */}
          <BracketVisualization bracket={bracket} />

          {/* Tournament Status */}
          <div className="text-center">
            {bracket.winner ? (
              <div className="bg-gradient-to-r from-yellow-400/20 to-yellow-600/20 border border-yellow-500/30 rounded-lg p-4">
                <h3 className="text-yellow-400 font-bold text-xl mb-2">🏆 Tournament Complete!</h3>
                <p className="text-white text-lg">Champion: <span className="font-bold">{bracket.winner}</span></p>
              </div>
            ) : (
              <div className="bg-gray-800/50 rounded-lg p-4">
                <p className="text-gray-300">
                  Current Round: <span className="text-white font-semibold">
                    {getRoundName(bracket.currentRound, bracket.totalRounds)}
                  </span>
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default TournamentPage
