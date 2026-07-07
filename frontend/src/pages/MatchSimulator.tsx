import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Zap, Target, Activity, Users } from 'lucide-react'
import { Team, Match, MatchEvent, Player } from '../types'
import FormationPitch from '../components/FormationPitch'
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
  const [simulationSpeed, setSimulationSpeed] = useState<number>(200) // milliseconds per minute (Normal = 5 min/sec)
  const [goalCelebration, setGoalCelebration] = useState<{ player: string; team: string; minute: number } | null>(null)

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
                setGoalCelebration({ player: event.player, team: event.team, minute: event.minute })
                setTimeout(() => setGoalCelebration(null), 2600)
                break
              case 'yellow_card':
                toastMessage = `🟨 Yellow card: ${event.player} (${event.team})`
                toast(toastMessage, { duration: 3000, position: 'bottom-right' })
                break
              case 'red_card':
                toastMessage = `🟥 Red card: ${event.player} (${event.team})`
                toast.error(toastMessage, { duration: 3000, position: 'bottom-right' })
                break
              case 'substitution':
                toastMessage = `🔄 Substitution: ${event.description}`
                toast(toastMessage, { duration: 3000, position: 'bottom-right' })
                break
              default:
                if (event.description) {
                  toast(event.description, { duration: 3000, position: 'bottom-right' })
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
      }, simulationSpeed) // Use configurable simulation speed
      
      return () => clearTimeout(timer)
    }
  }, [isLiveMode, currentMinute, match, homeTeam, awayTeam, simulationSpeed])

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
      {/* Goal celebration overlay */}
      <AnimatePresence>
        {goalCelebration && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[60] flex items-center justify-center pointer-events-none"
          >
            <motion.div
              initial={{ scale: 0.4, rotate: -8, opacity: 0 }}
              animate={{ scale: 1, rotate: 0, opacity: 1 }}
              exit={{ scale: 1.15, opacity: 0 }}
              transition={{ type: 'spring', bounce: 0.55, duration: 0.7 }}
              className={`relative px-10 py-8 rounded-3xl border-2 shadow-2xl text-center backdrop-blur-xl ${
                goalCelebration.team === homeTeam
                  ? 'bg-emerald-950/90 border-emerald-400/70 shadow-emerald-500/30'
                  : 'bg-rose-950/90 border-rose-400/70 shadow-rose-500/30'
              }`}
            >
              <motion.div
                animate={{ rotate: [0, 360] }}
                transition={{ duration: 0.9, ease: 'easeOut' }}
                className="text-6xl mb-2"
              >
                ⚽
              </motion.div>
              <div className="text-5xl font-extrabold tracking-tight text-white drop-shadow-lg">
                GOAL!
              </div>
              <div className={`mt-2 text-xl font-bold ${
                goalCelebration.team === homeTeam ? 'text-emerald-300' : 'text-rose-300'
              }`}>
                {goalCelebration.player}
              </div>
              <div className="text-sm text-white/60">
                {goalCelebration.team} · {goalCelebration.minute}'
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-4 flex items-center gap-3">
          <Zap className="text-primary-400" />
          Match Simulator
        </h1>
      </div>
      
      {/* Main 3-column layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Left column: Team selection */}
        <div className="card-glass p-6 min-h-[600px]">
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
                className="w-full bg-[#04100a] text-white border border-emerald-800/50 rounded-xl p-3 focus:border-emerald-500 focus:outline-none transition-colors duration-200"
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
                className="w-full bg-[#04100a] text-white border border-emerald-800/50 rounded-xl p-3 focus:border-emerald-500 focus:outline-none transition-colors duration-200"
              >
                <option value="">Select team</option>
                {teams.map((team) => (
                  <option key={team.name} value={team.name}>{team.name}</option>
                ))}
              </select>
            </div>
              
            <div className="pt-4 space-y-6">
              {/* Simulation Mode Section */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-white">Simulation Mode</h3>
                
                {/* Quick vs Live buttons */}
                <div className="grid grid-cols-2 gap-3">
                  <button
                    onClick={() => simulateMatch(false)}
                    disabled={!homeTeam || !awayTeam || isSimulating}
                    className="py-3 px-4 bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 disabled:from-gray-700 disabled:to-gray-700 disabled:cursor-not-allowed text-white font-semibold rounded-xl transition-all duration-300 hover:shadow-lg hover:shadow-emerald-900/50 active:scale-95 text-sm"
                  >
                    Quick Sim
                  </button>
                  <button
                    onClick={() => {
                      setIsLiveMode(true)
                      simulateMatch(true)
                    }}
                    disabled={!homeTeam || !awayTeam || isSimulating}
                    className="py-3 px-4 bg-gradient-to-r from-teal-600 to-emerald-600 hover:from-teal-500 hover:to-emerald-500 disabled:from-gray-700 disabled:to-gray-700 disabled:cursor-not-allowed text-white font-semibold rounded-xl transition-all duration-300 hover:shadow-lg hover:shadow-teal-900/50 active:scale-95 text-sm"
                  >
                    Live Sim
                  </button>
                </div>
              </div>

              {/* Live Simulation Speed */}
              <div className="space-y-3">
                <h4 className="text-md font-medium text-white">Live Simulation Speed</h4>
                <div className="space-y-2">
                  <div className="grid grid-cols-3 gap-2">
                    <button
                      onClick={() => setSimulationSpeed(1000)}
                      className={`py-2 px-3 rounded-lg text-sm font-medium transition-colors ${
                        simulationSpeed === 1000 
                          ? 'bg-primary-600 text-white' 
                          : 'bg-emerald-950/60 text-emerald-100/60 hover:bg-emerald-900/50'
                      }`}
                    >
                      Slow
                    </button>
                    <button
                      onClick={() => setSimulationSpeed(200)}
                      className={`py-2 px-3 rounded-lg text-sm font-medium transition-colors ${
                        simulationSpeed === 200 
                          ? 'bg-primary-600 text-white' 
                          : 'bg-emerald-950/60 text-emerald-100/60 hover:bg-emerald-900/50'
                      }`}
                    >
                      Normal
                    </button>
                    <button
                      onClick={() => setSimulationSpeed(100)}
                      className={`py-2 px-3 rounded-lg text-sm font-medium transition-colors ${
                        simulationSpeed === 100 
                          ? 'bg-primary-600 text-white' 
                          : 'bg-emerald-950/60 text-emerald-100/60 hover:bg-emerald-900/50'
                      }`}
                    >
                      Fast
                    </button>
                  </div>
                  <div className="text-xs text-gray-400 text-center">
                    {simulationSpeed === 1000 && 'One minute per second'}
                    {simulationSpeed === 200 && 'Five minutes per second'}
                    {simulationSpeed === 100 && 'Ten minutes per second'}
                  </div>
                </div>
              </div>

              {/* Match Control */}
              {isSimulating && isLiveMode && (
                <div className="space-y-3">
                  <h4 className="text-md font-medium text-white">Match Control</h4>
                  <button
                    onClick={() => {
                      setIsLiveMode(false)
                      setIsSimulating(false)
                    }}
                    className="w-full py-2 px-4 bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg transition-colors text-sm"
                  >
                    Stop Live Simulation
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
        
        {/* Middle column: Score and minute */}
        <div className="card-glass p-6 min-h-[600px]">
          {match ? (
            <div className="space-y-6">
              {isLiveMode && currentMinute < 90 && (
                <div className="flex justify-center">
                  <span className="inline-flex items-center gap-1.5 rounded-full bg-red-500/15 px-3 py-1 text-xs font-bold uppercase tracking-widest text-red-400">
                    <span className="h-2 w-2 animate-pulse rounded-full bg-red-500" />
                    Live
                  </span>
                </div>
              )}

              <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-3">
                <div className="text-center min-w-0">
                  <div className="truncate text-lg font-bold text-white">{homeTeam}</div>
                  <div key={`h-${liveScore.home}`} className="mt-2 text-5xl font-extrabold tabular-nums text-primary-400 score-pop">{liveScore.home}</div>
                </div>

                <div className="text-2xl font-light text-emerald-700">–</div>

                <div className="text-center min-w-0">
                  <div className="truncate text-lg font-bold text-white">{awayTeam}</div>
                  <div key={`a-${liveScore.away}`} className="mt-2 text-5xl font-extrabold tabular-nums text-primary-400 score-pop">{liveScore.away}</div>
                </div>
              </div>

              <div className="flex justify-center items-center">
                <div className="bg-emerald-950/70 border border-emerald-700/40 px-6 py-2 rounded-full">
                  <span className="font-bold text-xl text-white tabular-nums">{currentMinute < 90 ? currentMinute : 90}'</span>
                </div>
              </div>
              
              <div className="space-y-4 text-sm">
                {/* Possession with bar */}
                <div className="space-y-2">
                  <div className="flex justify-between text-xs text-gray-400">
                    <span>Possession</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-white w-8 text-left">{liveStats.possession_home}%</span>
                    <div className="flex-1 bg-emerald-950/80 rounded-full h-2">
                      <div 
                        className="bg-blue-500 h-2 rounded-full transition-all duration-500" 
                        style={{width: `${liveStats.possession_home}%`}}
                      ></div>
                    </div>
                    <span className="text-white w-8 text-right">{liveStats.possession_away}%</span>
                  </div>
                </div>
                
                {/* Shots with bar */}
                <div className="space-y-2">
                  <div className="flex justify-between text-xs text-gray-400">
                    <span>Shots</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-white w-8 text-left">{liveStats.shots_home}</span>
                    <div className="flex-1 bg-emerald-950/80 rounded-full h-2">
                      <div 
                        className="bg-green-500 h-2 rounded-full transition-all duration-500" 
                        style={{width: `${liveStats.shots_home / Math.max(liveStats.shots_home + liveStats.shots_away, 1) * 100}%`}}
                      ></div>
                    </div>
                    <span className="text-white w-8 text-right">{liveStats.shots_away}</span>
                  </div>
                </div>
                
                {/* Shots on Target with bar */}
                <div className="space-y-2">
                  <div className="flex justify-between text-xs text-gray-400">
                    <span>On Target</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-white w-8 text-left">{liveStats.shots_on_target_home}</span>
                    <div className="flex-1 bg-emerald-950/80 rounded-full h-2">
                      <div 
                        className="bg-yellow-500 h-2 rounded-full transition-all duration-500" 
                        style={{width: `${liveStats.shots_on_target_home / Math.max(liveStats.shots_on_target_home + liveStats.shots_on_target_away, 1) * 100}%`}}
                      ></div>
                    </div>
                    <span className="text-white w-8 text-right">{liveStats.shots_on_target_away}</span>
                  </div>
                </div>
                
                {/* Corners with bar */}
                <div className="space-y-2">
                  <div className="flex justify-between text-xs text-gray-400">
                    <span>Corners</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-white w-8 text-left">{match?.events?.filter(e => e.event_type === 'corner' && e.team === homeTeam).length || 0}</span>
                    <div className="flex-1 bg-emerald-950/80 rounded-full h-2">
                      <div 
                        className="bg-purple-500 h-2 rounded-full transition-all duration-500" 
                        style={{width: `${(match?.events?.filter(e => e.event_type === 'corner' && e.team === homeTeam).length || 0) / Math.max((match?.events?.filter(e => e.event_type === 'corner').length || 1), 1) * 100}%`}}
                      ></div>
                    </div>
                    <span className="text-white w-8 text-right">{match?.events?.filter(e => e.event_type === 'corner' && e.team === awayTeam).length || 0}</span>
                  </div>
                </div>
                
                {/* Yellow Cards with bar */}
                <div className="space-y-2">
                  <div className="flex justify-between text-xs text-gray-400">
                    <span>Yellow Cards</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-white w-8 text-left">{match?.events?.filter(e => e.event_type === 'yellow_card' && e.team === homeTeam).length || 0}</span>
                    <div className="flex-1 bg-emerald-950/80 rounded-full h-2">
                      <div 
                        className="bg-yellow-400 h-2 rounded-full transition-all duration-500" 
                        style={{width: `${(match?.events?.filter(e => e.event_type === 'yellow_card' && e.team === homeTeam).length || 0) / Math.max((match?.events?.filter(e => e.event_type === 'yellow_card').length || 1), 1) * 100}%`}}
                      ></div>
                    </div>
                    <span className="text-white w-8 text-right">{match?.events?.filter(e => e.event_type === 'yellow_card' && e.team === awayTeam).length || 0}</span>
                  </div>
                </div>
                
                {/* Red Cards with bar */}
                <div className="space-y-2">
                  <div className="flex justify-between text-xs text-gray-400">
                    <span>Red Cards</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-white w-8 text-left">{match?.events?.filter(e => e.event_type === 'red_card' && e.team === homeTeam).length || 0}</span>
                    <div className="flex-1 bg-emerald-950/80 rounded-full h-2">
                      <div 
                        className="bg-red-500 h-2 rounded-full transition-all duration-500" 
                        style={{width: `${(match?.events?.filter(e => e.event_type === 'red_card' && e.team === homeTeam).length || 0) / Math.max((match?.events?.filter(e => e.event_type === 'red_card').length || 1), 1) * 100}%`}}
                      ></div>
                    </div>
                    <span className="text-white w-8 text-right">{match?.events?.filter(e => e.event_type === 'red_card' && e.team === awayTeam).length || 0}</span>
                  </div>
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
        <div className="card-glass p-6 min-h-[600px]">
          <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
            <Activity className="text-primary-400" />
            Match Events
          </h2>

          {visibleEvents.length > 0 ? (
            <div className="space-y-4">
              {/* Event Summary */}
              <div className="bg-emerald-950/50 rounded-xl p-4 space-y-3 border border-emerald-800/30">
                <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wide">Event Summary</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="space-y-1">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Goals:</span>
                      <span className="text-white">{visibleEvents.filter(e => e.event_type === 'goal').length}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Yellow Cards:</span>
                      <span className="text-yellow-400">{visibleEvents.filter(e => e.event_type === 'yellow_card').length}</span>
                    </div>
                  </div>
                  <div className="space-y-1">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Red Cards:</span>
                      <span className="text-red-400">{visibleEvents.filter(e => e.event_type === 'red_card').length}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Substitutions:</span>
                      <span className="text-blue-400">{visibleEvents.filter(e => e.event_type === 'substitution').length}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Events List */}
              <div className="space-y-3 max-h-[400px] overflow-y-auto pr-1">
                {visibleEvents.slice().reverse().map((event) => (
                  <motion.div
                    key={`${event.minute}-${event.event_type}-${event.player}`}
                    initial={{ opacity: 0, x: 24 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.35, ease: 'easeOut' }}
                    className="flex items-start gap-3 p-3 bg-emerald-950/50 rounded-xl hover:bg-emerald-900/40 transition-all duration-300">
                    <div className="text-xl mt-1">{renderEventIcon(event.event_type)}</div>
                    <div className="flex-1">
                      <div className="font-medium text-white">
                        {event.event_type === 'goal' && `Goal by ${event.player}`}
                        {event.event_type === 'yellow_card' && `Yellow card: ${event.player}`}
                        {event.event_type === 'red_card' && `Red card: ${event.player}`}
                        {event.event_type === 'substitution' && `${event.description}`}
                      </div>
                      <div className="text-xs text-gray-400 mt-1 flex justify-between">
                        <span>{event.team}</span>
                        <span>{event.minute}'</span>
                      </div>
                      {event.event_type === 'goal' && (
                        <div className="text-xs text-primary-400 mt-1">
                          ⚽ Match Score Updated
                        </div>
                      )}
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          ) : (
            <div className="flex flex-col justify-center items-center h-[500px] space-y-4">
              <div className="text-6xl text-gray-600">⚽</div>
              <p className="text-gray-400 text-center">
                No events yet
                <br />
                <span className="text-sm">Start a simulation to see match events</span>
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Football Field with Formations - Always Visible */}
      <div className="card-glass p-6 mt-8">
        <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
          <Users className="text-primary-400" />
          {(homeTeam && awayTeam) ? 'Match Formations' : 'Football Pitch'}
        </h3>
        
        <FormationPitch
          homeTeam={homeTeam}
          awayTeam={awayTeam}
          homeLineup={homeLineup}
          awayLineup={awayLineup}
          homeFormation={homeFormation}
          awayFormation={awayFormation}
          events={match?.events}
        />
      </div>
    </div>
  )
}

export default MatchSimulator
