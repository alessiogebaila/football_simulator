import React, { useState, useEffect } from 'react'
import { BarChart3, TrendingUp, Users, Trophy, Target } from 'lucide-react'
import api from '../services/api'
import toast from 'react-hot-toast'

interface GlobalStats {
  total_teams: number
  total_players: number
  total_market_value: number
  average_age: number
  top_valued_players: Array<{
    name: string
    team: string
    position: string
    market_value_eur: number
    overall_rating: number
  }>
  team_rankings: Array<{
    team: string
    total_value: number
    avg_rating: number
    player_count: number
  }>
}

const StatsPage: React.FC = () => {
  const [stats, setStats] = useState<GlobalStats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      const data = await api.getGlobalStats()
      setStats(data)
    } catch (error) {
      toast.error('Failed to fetch statistics')
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

  if (!stats) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center text-gray-400">
          No statistics available
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-4 flex items-center gap-3">
          <BarChart3 className="text-primary-400" />
          Statistics
        </h1>
        <p className="text-gray-300 text-lg">
          Global statistics and insights from the football simulator
        </p>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total Teams</p>
              <p className="text-2xl font-bold text-white">{stats.total_teams}</p>
            </div>
            <Users className="text-primary-400" size={32} />
          </div>
        </div>

        <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total Players</p>
              <p className="text-2xl font-bold text-white">{stats.total_players}</p>
            </div>
            <Target className="text-primary-400" size={32} />
          </div>
        </div>

        <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total Market Value</p>
              <p className="text-2xl font-bold text-white">
                €{(stats.total_market_value / 1000000000).toFixed(1)}B
              </p>
            </div>
            <TrendingUp className="text-green-400" size={32} />
          </div>
        </div>

        <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Average Age</p>
              <p className="text-2xl font-bold text-white">{stats.average_age.toFixed(1)} yrs</p>
            </div>
            <Trophy className="text-yellow-400" size={32} />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Top Valued Players */}
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
          <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
            <TrendingUp className="text-primary-400" />
            Top Valued Players
          </h2>

          <div className="space-y-4">
            {stats.top_valued_players.map((player, index) => (
              <div
                key={`${player.name}-${player.team}`}
                className="flex items-center justify-between p-4 bg-gray-700/30 rounded-lg"
              >
                <div className="flex items-center gap-4">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-sm ${
                    index === 0 ? 'bg-yellow-500' :
                    index === 1 ? 'bg-gray-400' :
                    index === 2 ? 'bg-amber-600' :
                    'bg-gray-600'
                  }`}>
                    {index + 1}
                  </div>
                  <div>
                    <h4 className="text-white font-semibold">{player.name}</h4>
                    <p className="text-gray-400 text-sm">
                      {player.team} • {player.position} • Rating: {player.overall_rating}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-primary-400 font-semibold">
                    €{(player.market_value_eur / 1000000).toFixed(1)}M
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Team Rankings */}
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
          <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
            <Trophy className="text-primary-400" />
            Team Rankings by Value
          </h2>

          <div className="space-y-4">
            {stats.team_rankings.map((team, index) => (
              <div
                key={team.team}
                className="flex items-center justify-between p-4 bg-gray-700/30 rounded-lg"
              >
                <div className="flex items-center gap-4">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-sm ${
                    index < 3 ? 'bg-primary-600' : 'bg-gray-600'
                  }`}>
                    {index + 1}
                  </div>
                  <div>
                    <h4 className="text-white font-semibold">{team.team}</h4>
                    <p className="text-gray-400 text-sm">
                      {team.player_count} players • Avg Rating: {team.avg_rating.toFixed(1)}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-primary-400 font-semibold">
                    €{(team.total_value / 1000000).toFixed(1)}M
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default StatsPage
