import React, { useState, useEffect } from 'react'
import { Zap, Target, Activity, Users, Shirt } from 'lucide-react'
import { Team, Match, MatchEvent, Player } from '../types'
import api from '../services/api'
import toast from 'react-hot-toast'

const MatchSimulator: React.FC = () => {
  const [teams, setTeams] = useState<Team[]>([])
  const [homeTeam, setHomeTeam] = useState<string>('')
  const [awayTeam, setAwayTeam] = useState<string>('')
  const [match, setMatch] = useState<Match | null>(null)
  const [isSimulating, setIsSimulating] = useState(false)
  const [isLiveMode, setIsLiveMode] = useState(false)
  const [currentMinute, setCurrentMinute] = useState(0)
  const [visibleEvents, setVisibleEvents] = useState<MatchEvent[]>([])
  const [liveScore, setLiveScore] = useState({ home: 0, away: 0 })
  const [liveStats, setLiveStats] = useState({
    possession_home: 50, possession_away: 50,
    shots_home: 0, shots_away: 0,
    shots_on_target_home: 0, shots_on_target_away: 0,
    corners_home: 0, corners_away: 0,
    fouls_home: 0, fouls_away: 0,
    yellow_cards_home: 0, yellow_cards_away: 0,
    red_cards_home: 0, red_cards_away: 0
  })
  const [homeLineup, setHomeLineup] = useState<Player[]>([])
  const [awayLineup, setAwayLineup] = useState<Player[]>([])
  const [homeFormation, setHomeFormation] = useState<string>('')
  const [awayFormation, setAwayFormation] = useState<string>('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchTeams()
  }, [])

  // Fetch starting lineups when teams are selected
  useEffect(() => {
    if (homeTeam) {
      fetchStartingEleven(homeTeam, 'home')
    }
  }, [homeTeam])

  useEffect(() => {
    if (awayTeam) {
      fetchStartingEleven(awayTeam, 'away')
    }
  }, [awayTeam])

  // Live simulation effect with statistics updates and event animations
  useEffect(() => {
    if (isLiveMode && match && currentMinute < 90) {
      const timer = setTimeout(() => {
        const nextMinute = currentMinute + 1
        setCurrentMinute(nextMinute)
        
        // Show events up to current minute
        const eventsUpToNow = match.events?.filter(event => event.minute <= nextMinute) || []
        
        // Check if there are new events at this minute
        const newEvents = match.events?.filter(event => event.minute === nextMinute) || []
        if (newEvents.length > 0) {
          // For each new event, show a toast notification
          newEvents.forEach(event => {
            let toastMessage = ''
            // Default to regular toast
            switch (event.event_type) {
              case 'goal':
                toastMessage = `⚽ GOAL! ${event.player} (${event.team})`
                if (event.team === homeTeam) {
                  toast.success(toastMessage, { duration: 3000, position: 'bottom-center' })
                } else {
                  toast.error(toastMessage, { duration: 3000, position: 'bottom-center' })
                }
                break
              case 'yellow_card':
                toastMessage = `🟨 Yellow card: ${event.player} (${event.team})`
                toast(toastMessage, { duration: 3000, position: 'bottom-center' })
                break
              case 'red_card':
                toastMessage = `🟥 Red card: ${event.player} (${event.team})`
                toast.error(toastMessage, { duration: 3000, position: 'bottom-center' })
                break
              case 'substitution':
                toastMessage = `🔄 Substitution: ${event.description}`
                toast(toastMessage, { duration: 3000, position: 'bottom-center' })
                break
              default:
                if (event.description) {
                  toast(event.description, { duration: 3000, position: 'bottom-center' })
                }
            }
          })
        }
        
        setVisibleEvents(eventsUpToNow)
        
        // Update live score
        const goalsHome = eventsUpToNow.filter(e => e.event_type === 'goal' && e.team === homeTeam).length
        const goalsAway = eventsUpToNow.filter(e => e.event_type === 'goal' && e.team === awayTeam).length
        setLiveScore({ home: goalsHome, away: goalsAway })
        
        // Progressive statistics updates
        if (match.stats) {
          const progress = nextMinute / 90
          setLiveStats({
            possession_home: Math.round(match.stats.possession_home * progress + 50 * (1 - progress)),
            possession_away: Math.round(match.stats.possession_away * progress + 50 * (1 - progress)),
            shots_home: Math.round(match.stats.shots_home * progress),
            shots_away: Math.round(match.stats.shots_away * progress),
            shots_on_target_home: Math.round(match.stats.shots_on_target_home * progress),
            shots_on_target_away: Math.round(match.stats.shots_on_target_away * progress),
            corners_home: Math.round(match.stats.corners_home * progress),
            corners_away: Math.round(match.stats.corners_away * progress),
            fouls_home: Math.round(match.stats.fouls_home * progress),
            fouls_away: Math.round(match.stats.fouls_away * progress),
            yellow_cards_home: eventsUpToNow.filter(e => e.event_type === 'yellow_card' && e.team === homeTeam).length,
            yellow_cards_away: eventsUpToNow.filter(e => e.event_type === 'yellow_card' && e.team === awayTeam).length,
            red_cards_home: eventsUpToNow.filter(e => e.event_type === 'red_card' && e.team === homeTeam).length,
            red_cards_away: eventsUpToNow.filter(e => e.event_type === 'red_card' && e.team === awayTeam).length
          })
        }
      }, 50) // 50ms per minute for fast simulation
      
      return () => clearTimeout(timer)
    }
  }, [isLiveMode, currentMinute, match, homeTeam, awayTeam])

  const fetchTeams = async () => {
    try {
      const data = await api.getTeams()
      setTeams(data)
    } catch (error) {
      console.error('Error fetching teams:', error)
      toast.error('Failed to load teams')
    } finally {
      setLoading(false)
    }
  }

  const fetchStartingEleven = async (teamName: string, side: 'home' | 'away') => {
    try {
      const response = await api.getStartingEleven(teamName)
      if (side === 'home') {
        setHomeLineup(response.players)
        setHomeFormation(response.formation)
      } else {
        setAwayLineup(response.players)
        setAwayFormation(response.formation)
      }
    } catch (error) {
      console.error(`Error fetching starting eleven for ${teamName}:`, error)
      toast.error(`Failed to load starting eleven for ${teamName}`)
    }
  }

  const simulateMatch = async (liveMode = false) => {
    if (!homeTeam || !awayTeam) {
      toast.error('Please select both teams')
      return
    }

    if (homeTeam === awayTeam) {
      toast.error('Please select different teams')
      return
    }

    setIsSimulating(true)
    setIsLiveMode(liveMode)
    setCurrentMinute(0)
    setVisibleEvents([])
    setLiveScore({ home: 0, away: 0 })
    setLiveStats({
      possession_home: 50, possession_away: 50,
      shots_home: 0, shots_away: 0,
      shots_on_target_home: 0, shots_on_target_away: 0,
      corners_home: 0, corners_away: 0,
      fouls_home: 0, fouls_away: 0,
      yellow_cards_home: 0, yellow_cards_away: 0,
      red_cards_home: 0, red_cards_away: 0
    })

    try {
      const matchData = await api.simulateMatch(homeTeam, awayTeam, 'detailed')
      setMatch(matchData)
      
      if (!liveMode) {
        setVisibleEvents(matchData.events || [])
        setCurrentMinute(90)
        if (matchData.stats) {
          setLiveStats({
            possession_home: matchData.stats.possession_home,
            possession_away: matchData.stats.possession_away,
            shots_home: matchData.stats.shots_home,
            shots_away: matchData.stats.shots_away,
            shots_on_target_home: matchData.stats.shots_on_target_home,
            shots_on_target_away: matchData.stats.shots_on_target_away,
            corners_home: matchData.stats.corners_home,
            corners_away: matchData.stats.corners_away,
            fouls_home: matchData.stats.fouls_home,
            fouls_away: matchData.stats.fouls_away,
            yellow_cards_home: matchData.stats.yellow_cards_home,
            yellow_cards_away: matchData.stats.yellow_cards_away,
            red_cards_home: matchData.stats.red_cards_home,
            red_cards_away: matchData.stats.red_cards_away
          })
        }
        setLiveScore({ home: matchData.home_score, away: matchData.away_score })
      }
      
      toast.success(liveMode ? 'Live simulation started!' : 'Match simulation completed!')
    } catch (error) {
      console.error('Error simulating match:', error)
      toast.error('Failed to simulate match')
    } finally {
      setIsSimulating(false)
    }
  }

  const renderEventIcon = (eventType: string) => {
    switch (eventType) {
      case 'goal': return '⚽'
      case 'yellow_card': return '🟨'
      case 'red_card': return '🟥'
      case 'substitution': return '🔄'
      case 'corner': return '🚩'
      default: return '📝'
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
          <Zap className="text-primary-400" />
          Match Simulator
        </h1>
      </div>
      
      {/* Main 3-column layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Left column: Team selection */}
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700 h-min">
          <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
            <Target className="text-primary-400" />
            Select Teams
          </h2>

          <div className="space-y-4">
            <div>
              <label className="block text-gray-300 text-sm font-medium mb-2">
                Home Team
              </label>
              <select
                value={homeTeam}
                onChange={(e) => setHomeTeam(e.target.value)}
                className="w-full bg-gray-900 text-white border border-gray-700 rounded-lg p-3"
              >
                <option value="">Select team</option>
                {teams.map((team) => (
                  <option key={team.name} value={team.name}>{team.name}</option>
                ))}
              </select>
            </div>
            
            <div className="flex items-center justify-center">
              <span className="text-2xl font-bold text-primary-400">VS</span>
            </div>
            
            <div>
              <label className="block text-gray-300 text-sm font-medium mb-2">
                Away Team
              </label>
              <select
                value={awayTeam}
                onChange={(e) => setAwayTeam(e.target.value)}
                className="w-full bg-gray-900 text-white border border-gray-700 rounded-lg p-3"
              >
                <option value="">Select team</option>
                {teams.map((team) => (
                  <option key={team.name} value={team.name}>{team.name}</option>
                ))}
              </select>
            </div>
              
            <div className="pt-4 space-y-4">
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="liveMode"
                  checked={isLiveMode}
                  onChange={(e) => setIsLiveMode(e.target.checked)}
                  className="rounded text-primary-500 focus:ring-primary-500 h-4 w-4"
                />
                <label htmlFor="liveMode" className="text-gray-300 text-sm">Live Simulation</label>
              </div>
              
              <button
                onClick={() => simulateMatch()}
                disabled={!homeTeam || !awayTeam || isSimulating}
                className="w-full py-3 px-6 bg-primary-600 hover:bg-primary-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors"
              >
                {isSimulating ? 'Simulating...' : 'Simulate Match'}
              </button>
            </div>
          </div>
        </div>
        
        {/* Middle column: Score and minute */}
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700 h-min">
          {match ? (
            <div className="space-y-6">
              <div className="flex justify-center items-center">
                <div className="text-center px-4">
                  <div className="text-xl font-bold text-white">{homeTeam}</div>
                  <div className="text-4xl font-bold text-primary-400 mt-2">{liveScore.home}</div>
                </div>
                
                <div className="px-4">
                  <div className="text-xl text-gray-400 mb-2">VS</div>
                </div>
                
                <div className="text-center px-4">
                  <div className="text-xl font-bold text-white">{awayTeam}</div>
                  <div className="text-4xl font-bold text-primary-400 mt-2">{liveScore.away}</div>
                </div>
              </div>
              
              <div className="flex justify-center items-center">
                <div className="bg-gray-700/50 px-6 py-2 rounded-full">
                  <span className="font-bold text-xl text-white">{currentMinute < 90 ? currentMinute : 90}'</span>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-white">{liveStats.possession_home}%</span>
                  <span className="text-gray-400">Possession</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Possession</span>
                  <span className="text-white">{liveStats.possession_away}%</span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-white">{liveStats.shots_home}</span>
                  <span className="text-gray-400">Shots</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Shots</span>
                  <span className="text-white">{liveStats.shots_away}</span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-white">{liveStats.shots_on_target_home}</span>
                  <span className="text-gray-400">On Target</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">On Target</span>
                  <span className="text-white">{liveStats.shots_on_target_away}</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex justify-center items-center h-48">
              <p className="text-gray-400 text-xl">Select teams and start simulation</p>
            </div>
          )}
        </div>
        
        {/* Right column: Events */}
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
          <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
            <Activity className="text-primary-400" />
            Match Events
          </h2>

          {visibleEvents.length > 0 ? (
            <div className="space-y-3 max-h-[400px] overflow-y-auto pr-1">
              {visibleEvents.slice().reverse().map((event, index) => (
                <div key={index} className="flex items-start gap-3 p-3 bg-gray-700/50 rounded-lg hover:bg-gray-700/70 transition-colors">
                  <div className="text-xl mt-1">{renderEventIcon(event.event_type)}</div>
                  <div className="flex-1">
                    <div className="font-medium text-white">
                      {event.event_type === 'goal' && `Goal by ${event.player}`}
                      {event.event_type === 'yellow_card' && `Yellow card: ${event.player}`}
                      {event.event_type === 'red_card' && `Red card: ${event.player}`}
                      {event.event_type === 'substitution' && `${event.description}`}
                    </div>
                    <div className="text-xs text-gray-400 mt-1">
                      {event.team} - {event.minute}'
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex justify-center items-center h-48">
              <p className="text-gray-400">No events yet</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default MatchSimulator
