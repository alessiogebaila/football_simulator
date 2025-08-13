import React, { useState, useEffect } from 'react'
import { Trophy, Play, Clock, Star } from 'lucide-react'
import { Team, Tournament } from '../types'
import api from '../services/api'
import toast from 'react-hot-toast'

const TournamentPage: React.FC = () => {
  const [teams, setTeams] = useState<Team[]>([])
  const [selectedTeams, setSelectedTeams] = useState<string[]>([])
  const [tournament, setTournament] = useState<Tournament | null>(null)
  const [isRunning, setIsRunning] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchTeams()
  }, [])

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

  const toggleTeamSelection = (teamName: string) => {
    setSelectedTeams(prev => 
      prev.includes(teamName)
        ? prev.filter(t => t !== teamName)
        : [...prev, teamName]
    )
  }

  const runTournament = async () => {
    if (selectedTeams.length < 4) {
      toast.error('Please select at least 4 teams')
      return
    }

    setIsRunning(true)
    try {
      const result = await api.runTournament(selectedTeams)
      setTournament(result)
      toast.success('Tournament completed!')
    } catch (error) {
      toast.error('Failed to run tournament')
    } finally {
      setIsRunning(false)
    }
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
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-4 flex items-center gap-3">
          <Trophy className="text-primary-400" />
          Tournament
        </h1>
        <p className="text-gray-300 text-lg">
          Create and run tournaments with your selected teams
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Team Selection */}
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
          <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
            <Star className="text-primary-400" />
            Select Teams ({selectedTeams.length}/16)
          </h2>

          <div className="space-y-4 max-h-96 overflow-y-auto">
            {teams.map((team) => (
              <div
                key={team.name}
                onClick={() => toggleTeamSelection(team.name)}
                className={`p-4 rounded-lg border cursor-pointer transition-all duration-200 ${
                  selectedTeams.includes(team.name)
                    ? 'bg-primary-600/20 border-primary-500'
                    : 'bg-gray-700/30 border-gray-600 hover:border-gray-500'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-white font-semibold">{team.name}</h3>
                    <p className="text-gray-400 text-sm">
                      {team.players.length} players • 
                      €{(team.players.reduce((sum, p) => sum + p.market_value_eur, 0) / 1000000).toFixed(1)}M value
                    </p>
                  </div>
                  <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
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

          <div className="mt-6 pt-6 border-t border-gray-700">
            <button
              onClick={runTournament}
              disabled={isRunning || selectedTeams.length < 4}
              className="w-full bg-primary-600 hover:bg-primary-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white py-3 px-6 rounded-lg font-semibold transition-colors duration-200 flex items-center justify-center gap-2"
            >
              {isRunning ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  Running Tournament...
                </>
              ) : (
                <>
                  <Play size={20} />
                  Run Tournament
                </>
              )}
            </button>
          </div>
        </div>

        {/* Tournament Results */}
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
          <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
            <Clock className="text-primary-400" />
            Tournament Results
          </h2>

          {tournament ? (
            <div className="space-y-6">
              <div className="text-center">
                <div className="bg-gradient-to-r from-yellow-400 to-yellow-600 text-black p-4 rounded-lg mb-4">
                  <Trophy className="mx-auto mb-2" size={32} />
                  <h3 className="text-xl font-bold">Champion</h3>
                  <p className="text-lg font-semibold">{tournament.winner}</p>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="text-lg font-bold text-white">Final Standings</h3>
                <div className="space-y-2">
                  {tournament.standings.map((standing, index) => (
                    <div
                      key={standing.team}
                      className={`flex items-center justify-between p-3 rounded-lg ${
                        index === 0 ? 'bg-yellow-600/20 border border-yellow-500' :
                        index < 4 ? 'bg-green-600/20 border border-green-500' :
                        'bg-gray-700/30'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <span className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
                          {index + 1}
                        </span>
                        <span className="text-white font-semibold">{standing.team}</span>
                      </div>
                      <div className="text-right">
                        <div className="text-white font-semibold">{standing.points} pts</div>
                        <div className="text-gray-400 text-sm">
                          {standing.won}W {standing.drawn}D {standing.lost}L
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="pt-4 border-t border-gray-700">
                <p className="text-gray-400 text-sm text-center">
                  Tournament completed with {tournament.matches.length} matches played
                </p>
              </div>
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="text-gray-400 text-lg mb-4">
                No tournament results yet
              </div>
              <p className="text-gray-500">
                Select at least 4 teams and click "Run Tournament" to see results
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default TournamentPage
