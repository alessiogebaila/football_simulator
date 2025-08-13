import React, { useState, useEffect } from 'react'
import { Users, Trophy, Star } from 'lucide-react'
import { Team } from '../types'
import api from '../services/api'
import toast from 'react-hot-toast'

const TeamsPage: React.FC = () => {
  const [teams, setTeams] = useState<Team[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedTeam, setSelectedTeam] = useState<Team | null>(null)

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
          <Users className="text-primary-400" />
          Teams
        </h1>
        <p className="text-gray-300 text-lg">
          Explore all {teams.length} teams and their squads with real Transfermarkt data
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {teams.map((team) => (
          <div
            key={team.name}
            className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700 hover:border-primary-500 transition-all duration-300 cursor-pointer transform hover:scale-105"
            onClick={() => setSelectedTeam(team)}
          >
            <div className="text-center mb-4">
              <h3 className="text-xl font-bold text-white mb-2">{team.name}</h3>
              <div className="flex items-center justify-center gap-2 text-gray-400">
                <Users size={16} />
                <span>{team.players.length} players</span>
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Squad Value:</span>
                <span className="text-primary-400 font-semibold">
                  €{(team.players.reduce((sum, p) => sum + p.market_value_eur, 0) / 1000000).toFixed(1)}M
                </span>
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Avg Rating:</span>
                <span className="text-yellow-400 font-semibold flex items-center gap-1">
                  <Star size={16} />
                  {(team.players.reduce((sum, p) => sum + p.overall_rating, 0) / team.players.length).toFixed(1)}
                </span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-gray-400">Avg Age:</span>
                <span className="text-gray-300 font-semibold">
                  {(team.players.reduce((sum, p) => sum + p.age, 0) / team.players.length).toFixed(1)} yrs
                </span>
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-gray-700">
              <button className="w-full bg-primary-600 hover:bg-primary-700 text-white py-2 px-4 rounded-lg transition-colors duration-200 flex items-center justify-center gap-2">
                <Trophy size={16} />
                View Squad
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Team Detail Modal */}
      {selectedTeam && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-gray-800 rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-700">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-white">{selectedTeam.name} Squad</h2>
                <button
                  onClick={() => setSelectedTeam(null)}
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  ✕
                </button>
              </div>
            </div>
            
            <div className="p-6">
              <div className="grid gap-4">
                {selectedTeam.players.map((player, index) => (
                  <div
                    key={index}
                    className="bg-gray-700/50 rounded-lg p-4 flex items-center justify-between"
                  >
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 bg-primary-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
                        {player.kit_number}
                      </div>
                      <div>
                        <h4 className="text-white font-semibold">{player.name}</h4>
                        <p className="text-gray-400 text-sm">{player.position} • {player.age} years • {player.nationality}</p>
                      </div>
                    </div>
                    
                    <div className="text-right">
                      <p className="text-primary-400 font-semibold">
                        €{(player.market_value_eur / 1000000).toFixed(1)}M
                      </p>
                      <div className="text-yellow-400 text-sm flex items-center gap-1 justify-end">
                        <Star size={14} />
                        <span className="w-6 text-center">{player.overall_rating}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default TeamsPage
