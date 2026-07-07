import React, { useState, useEffect } from 'react'
import { Zap, Target, Activity, Users, Shirt, ArrowLeft } from 'lucide-react'
import { Team, Match, MatchEvent, Player } from '../types'
import api from '../services/api'
import toast from 'react-hot-toast'

interface TournamentMatchSimulatorProps {
  homeTeam: string
  awayTeam: string
  matchId: string
  onMatchComplete: (result: { homeScore: number; awayScore: number; winner: string }) => void
  onBack: () => void
}

const TournamentMatchSimulator: React.FC<TournamentMatchSimulatorProps> = ({
  homeTeam,
  awayTeam,
  matchId,
  onMatchComplete,
  onBack
}) => {
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
  const [simulationSpeed, setSimulationSpeed] = useState<number>(200)

  useEffect(() => {
    fetchStartingElevens()
  }, [homeTeam, awayTeam])

  // Live simulation effect
  useEffect(() => {
    if (isLiveMode && match && currentMinute < 90) {
      const timer = setTimeout(() => {
        const nextMinute = currentMinute + 1
        setCurrentMinute(nextMinute)
        
        const eventsUpToNow = match.events?.filter(event => event.minute <= nextMinute) || []
        const newEvents = match.events?.filter(event => event.minute === nextMinute) || []
        
        if (newEvents.length > 0) {
          newEvents.forEach(event => {
            let toastMessage = ''
            switch (event.event_type) {
              case 'goal':
                toastMessage = `⚽ GOAL! ${event.player} (${event.team})`
                if (event.team === homeTeam) {
                  toast.success(toastMessage, { duration: 3000, position: 'bottom-right' })
                } else {
                  toast.error(toastMessage, { duration: 3000, position: 'bottom-right' })
                }
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
        
        const goalsHome = eventsUpToNow.filter(e => e.event_type === 'goal' && e.team === homeTeam).length
        const goalsAway = eventsUpToNow.filter(e => e.event_type === 'goal' && e.team === awayTeam).length
        setLiveScore({ home: goalsHome, away: goalsAway })
        
        // Update progressive statistics
        updateLiveStats(eventsUpToNow, nextMinute)
        
        if (nextMinute >= 90) {
          setIsLiveMode(false)
          setIsSimulating(false)
          
          // Complete the match
          const finalResult = {
            homeScore: goalsHome,
            awayScore: goalsAway,
            winner: goalsHome > goalsAway ? homeTeam : awayTeam
          }
          
          toast.success(`Match Completed! ${finalResult.winner} wins ${goalsHome}-${goalsAway}!`)
          onMatchComplete(finalResult)
        }
      }, simulationSpeed)

      return () => clearTimeout(timer)
    }
  }, [isLiveMode, match, currentMinute, simulationSpeed, homeTeam, awayTeam, onMatchComplete])

  const fetchStartingElevens = async () => {
    try {
      const [homeResponse, awayResponse] = await Promise.all([
        api.getStartingEleven(homeTeam),
        api.getStartingEleven(awayTeam)
      ])
      setHomeLineup(homeResponse.players)
      setHomeFormation(homeResponse.formation)
      setAwayLineup(awayResponse.players)
      setAwayFormation(awayResponse.formation)
    } catch (error) {
      console.error('Error fetching lineups:', error)
    }
  }

  const updateLiveStats = (events: MatchEvent[], minute: number) => {
    const minuteProgress = minute / 90
    
    setLiveStats(prev => ({
      possession_home: Math.max(35, Math.min(65, 50 + (Math.random() - 0.5) * 30)),
      possession_away: 100 - prev.possession_home,
      shots_home: Math.floor(minuteProgress * (8 + Math.random() * 6)),
      shots_away: Math.floor(minuteProgress * (8 + Math.random() * 6)),
      shots_on_target_home: Math.floor(minuteProgress * (3 + Math.random() * 4)),
      shots_on_target_away: Math.floor(minuteProgress * (3 + Math.random() * 4)),
      corners_home: Math.floor(minuteProgress * (4 + Math.random() * 4)),
      corners_away: Math.floor(minuteProgress * (4 + Math.random() * 4)),
      fouls_home: events.filter(e => e.team === homeTeam && (e.event_type === 'yellow_card' || e.event_type === 'red_card')).length + Math.floor(minuteProgress * 8),
      fouls_away: events.filter(e => e.team === awayTeam && (e.event_type === 'yellow_card' || e.event_type === 'red_card')).length + Math.floor(minuteProgress * 8),
      yellow_cards_home: events.filter(e => e.team === homeTeam && e.event_type === 'yellow_card').length,
      yellow_cards_away: events.filter(e => e.team === awayTeam && e.event_type === 'yellow_card').length,
      red_cards_home: events.filter(e => e.team === homeTeam && e.event_type === 'red_card').length,
      red_cards_away: events.filter(e => e.team === awayTeam && e.event_type === 'red_card').length
    }))
  }

  const simulateMatch = async (isLive: boolean) => {
    setIsSimulating(true)
    setCurrentMinute(0)
    setLiveScore({ home: 0, away: 0 })
    setVisibleEvents([])

    try {
      let result: Match
      if (isLive) {
        result = await api.simulateLiveMatch(homeTeam, awayTeam, 1)
        setMatch(result)
        setIsLiveMode(true)
        toast.success('Live simulation started!')
      } else {
        result = await api.simulateMatch(homeTeam, awayTeam)
        setMatch(result)
        
        // Show final result immediately for quick simulation
        const finalResult = {
          homeScore: result.home_score,
          awayScore: result.away_score,
          winner: result.home_score > result.away_score ? homeTeam : awayTeam
        }
        
        toast.success(`Match Completed! ${finalResult.winner} wins ${result.home_score}-${result.away_score}!`)
        onMatchComplete(finalResult)
        setIsSimulating(false)
      }
    } catch (error) {
      toast.error('Failed to simulate match')
      setIsSimulating(false)
    }
  }

  const getPositionColor = (position: string) => {
    switch (position) {
      case 'GK': return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30'
      case 'CB': case 'LB': case 'RB': return 'bg-blue-500/20 text-blue-300 border-blue-500/30'
      case 'CDM': case 'CM': case 'CAM': case 'LW': case 'RW': return 'bg-green-500/20 text-green-300 border-green-500/30'
      case 'ST': case 'CF': return 'bg-red-500/20 text-red-300 border-red-500/30'
      default: return 'bg-gray-500/20 text-gray-300 border-gray-500/30'
    }
  }

  const renderPlayerCard = (player: Player, isHome: boolean) => {
    const events = visibleEvents.filter(e => e.player === player.name)
    const hasGoal = events.some(e => e.event_type === 'goal')
    const hasYellowCard = events.some(e => e.event_type === 'yellow_card')
    const hasRedCard = events.some(e => e.event_type === 'red_card')
    const isSubbedOut = events.some(e => e.event_type === 'substitution' && e.description?.includes('substituted out'))
    const isSubbedIn = events.some(e => e.event_type === 'substitution' && e.description?.includes('substituted in'))

    const cardSize = 'w-12 h-16 text-[8px]'
    const rotationClass = isHome ? 'transform -rotate-90' : 'transform rotate-90'

    return (
      <div className="relative flex flex-col items-center">
        {/* Event indicators */}
        {(hasGoal || hasYellowCard || hasRedCard || isSubbedOut || isSubbedIn) && (
          <div className="absolute -top-2 left-0 right-0 flex justify-center gap-1 z-10">
            {hasGoal && <span className="bg-green-900/80 text-white text-xs rounded-sm h-5 w-5 flex items-center justify-center">⚽</span>}
            {hasYellowCard && <span className="bg-yellow-500/80 text-white text-xs px-1.5 py-0.5 flex items-center justify-center" style={{height: '12px', width: '8px'}}></span>}
            {hasRedCard && <span className="bg-red-500/80 text-white text-xs px-1.5 py-0.5 flex items-center justify-center" style={{height: '12px', width: '8px'}}></span>}
            {(isSubbedOut || isSubbedIn) && <span className="bg-blue-500/80 text-white text-xs rounded-sm h-5 w-5 flex items-center justify-center">🔄</span>}
          </div>
        )}
        
        {/* Player card */}
        <div className={`${cardSize} ${isSubbedOut ? 'opacity-50' : ''} ${rotationClass} bg-gray-800/80 backdrop-blur-sm rounded-sm border ${getPositionColor(player.position)} transition-all hover:scale-105`}>
          <div className="p-1 h-full flex flex-col justify-between">
            <div className="text-center">
              <div className="font-bold leading-tight">{player.kit_number}</div>
              <div className="font-medium leading-tight">{player.position}</div>
            </div>
            <div className="text-center">
              <div className="font-semibold leading-tight">{player.name.split(' ').pop()}</div>
              <div className="text-[6px] leading-tight">{player.overall_rating}</div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Formation rendering logic (simplified version from MatchSimulator)
  const renderFormation = (lineup: Player[], teamName: string, isHome: boolean, formation: string) => {
    const getFormationLayout = (formation: string, players: Player[]) => {
      const goalkeeper = players.find(p => p.position === 'GK')
      const defenders = players.filter(p => ['CB', 'LB', 'RB'].includes(p.position))
      const midfielders = players.filter(p => ['CDM', 'CM', 'CAM', 'LW', 'RW'].includes(p.position))
      const attackers = players.filter(p => ['ST', 'CF'].includes(p.position))

      let lines = []

      switch (formation) {
        case "4-3-3":
          lines = [
            { type: 'attack', players: attackers.slice(0, 1), layout: 'center' },
            { type: 'wings', players: midfielders.filter(p => ['LW', 'RW'].includes(p.position)), layout: 'wide' },
            { type: 'midfield', players: midfielders.filter(p => ['CDM', 'CM'].includes(p.position)).slice(0, 3), layout: 'center' },
            { type: 'defense', players: defenders, layout: 'defense' },
            { type: 'goalkeeper', players: [goalkeeper].filter(Boolean), layout: 'goalkeeper' }
          ]
          break
        default:
          lines = [
            { type: 'attack', players: attackers.slice(0, 1), layout: 'center' },
            { type: 'wings', players: midfielders.filter(p => ['LW', 'RW'].includes(p.position)), layout: 'wide' },
            { type: 'midfield', players: midfielders.filter(p => ['CDM', 'CM'].includes(p.position)).slice(0, 3), layout: 'center' },
            { type: 'defense', players: defenders, layout: 'defense' },
            { type: 'goalkeeper', players: [goalkeeper].filter(Boolean), layout: 'center' }
          ]
      }

      return lines.filter(line => line.players.length > 0)
    }

    const renderLine = (line: any, index: number) => {
      const { players, layout } = line
      if (!players || players.length === 0) return null

      switch (layout) {
        case 'wide':
          return (
            <div key={index} className="flex justify-between items-center px-6 mb-4 relative w-full">
              {players.map((player: Player, pIndex: number) => (
                <div key={`${line.type}-${pIndex}`} className="flex-shrink-0">
                  {renderPlayerCard(player, isHome)}
                </div>
              ))}
            </div>
          )
        case 'defense':
          return (
            <div key={index} className="flex justify-between items-center px-3 mb-4 w-full">
              {players.sort((a: Player, b: Player) => {
                const order = ['LB', 'CB', 'CB', 'RB'];
                return order.indexOf(a.position) - order.indexOf(b.position);
              }).map((player: Player, pIndex: number) => (
                <div key={`def-${pIndex}`} className="flex-shrink-0">
                  {renderPlayerCard(player, isHome)}
                </div>
              ))}
            </div>
          )
        case 'goalkeeper':
          return (
            <div key={index} className="flex justify-center items-center mb-2">
              {players.map((player: Player, pIndex: number) => (
                <div key={`gk-${pIndex}`} className="flex-shrink-0">
                  {renderPlayerCard(player, isHome)}
                </div>
              ))}
            </div>
          )
        default:
          return (
            <div key={index} className="flex justify-center items-center gap-2 mb-4 w-full">
              {players.map((player: Player, pIndex: number) => (
                <div key={`${line.type}-${pIndex}`} className="flex-shrink-0">
                  {renderPlayerCard(player, isHome)}
                </div>
              ))}
            </div>
          )
      }
    }

    const formationLines = getFormationLayout(formation, lineup)
    return (
      <div className="h-full flex flex-col justify-between py-4">
        {formationLines.map((line, index) => renderLine(line, index))}
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <button
          onClick={onBack}
          className="flex items-center gap-2 bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors"
        >
          <ArrowLeft size={20} />
          Back to Tournament
        </button>
        
        <div className="text-center">
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <Zap className="text-primary-400" />
            {homeTeam} vs {awayTeam}
          </h1>
          <p className="text-gray-300">Tournament Match</p>
        </div>
        
        <div className="w-32"></div> {/* Spacer for alignment */}
      </div>

      {/* Match Controls */}
      <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
        <div className="flex items-center justify-center gap-4">
          <button
            onClick={() => simulateMatch(false)}
            disabled={isSimulating}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-6 py-3 rounded-lg font-semibold transition-colors flex items-center gap-2"
          >
            <Target size={20} />
            Quick Simulation
          </button>
          
          <button
            onClick={() => simulateMatch(true)}
            disabled={isSimulating}
            className="bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white px-6 py-3 rounded-lg font-semibold transition-colors flex items-center gap-2"
          >
            <Activity size={20} />
            Live Simulation
          </button>
        </div>

        {/* Live Simulation Speed */}
        {isLiveMode && (
          <div className="mt-4 text-center">
            <label className="block text-gray-300 text-sm font-medium mb-2">
              Simulation Speed
            </label>
            <div className="flex justify-center gap-2">
              {[
                { speed: 1000, label: 'Slow' },
                { speed: 200, label: 'Normal' },
                { speed: 100, label: 'Fast' }
              ].map(({ speed, label }) => (
                <button
                  key={speed}
                  onClick={() => setSimulationSpeed(speed)}
                  className={`px-3 py-1 rounded text-sm ${
                    simulationSpeed === speed
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Live Match Display */}
      {(isLiveMode || match) && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Live Statistics */}
          <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <Activity className="text-primary-400" />
              Live Stats
            </h3>

            {/* Score Display */}
            <div className="bg-gradient-to-r from-blue-900/30 to-green-900/30 rounded-lg p-4 mb-6">
              <div className="flex items-center justify-between text-white">
                <div className="text-center">
                  <div className="text-lg font-semibold">{homeTeam}</div>
                  <div className="text-3xl font-bold">{isLiveMode ? liveScore.home : (match?.home_score || 0)}</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold">-</div>
                  <div className="text-sm text-gray-300">{isLiveMode ? `${currentMinute}'` : 'FT'}</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-semibold">{awayTeam}</div>
                  <div className="text-3xl font-bold">{isLiveMode ? liveScore.away : (match?.away_score || 0)}</div>
                </div>
              </div>
            </div>

            {/* Statistics */}
            <div className="space-y-4">
              {/* Possession */}
              <div>
                <div className="flex justify-between text-sm text-gray-300 mb-1">
                  <span>{liveStats.possession_home}%</span>
                  <span>Possession</span>
                  <span>{liveStats.possession_away}%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-blue-500 h-2 rounded-full transition-all duration-500" 
                    style={{ width: `${liveStats.possession_home}%` }}
                  ></div>
                </div>
              </div>

              {/* Other Stats */}
              {[
                ['Shots', liveStats.shots_home, liveStats.shots_away],
                ['Shots on Target', liveStats.shots_on_target_home, liveStats.shots_on_target_away],
                ['Corners', liveStats.corners_home, liveStats.corners_away],
                ['Fouls', liveStats.fouls_home, liveStats.fouls_away],
                ['Yellow Cards', liveStats.yellow_cards_home, liveStats.yellow_cards_away],
                ['Red Cards', liveStats.red_cards_home, liveStats.red_cards_away]
              ].map(([stat, home, away]) => (
                <div key={stat} className="flex justify-between items-center py-2 border-b border-gray-700">
                  <span className="text-blue-400 font-semibold">{home}</span>
                  <span className="text-gray-300 text-sm">{stat}</span>
                  <span className="text-green-400 font-semibold">{away}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Formation Display */}
          <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
            <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
              <Users className="text-primary-400" />
              Match Formations
            </h3>
            
            <div className="relative border-2 border-white rounded-lg bg-gradient-to-br from-[#2a7828] to-[#1e5a1e] aspect-[2/1] p-4 overflow-hidden shadow-2xl">
              {/* Field markings (simplified) */}
              <div className="absolute inset-0">
                <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[25%] h-[50%] rounded-full border-2 border-white"></div>
                <div className="absolute top-0 bottom-0 left-1/2 transform -translate-x-1/2 w-0.5 bg-white"></div>
              </div>

              {/* Home team formation (left side) */}
              <div className="absolute inset-y-0 left-0 w-[48%] px-4">
                {homeLineup.length > 0 && renderFormation(homeLineup, homeTeam, true, homeFormation)}
              </div>
              
              {/* Away team formation (right side) */}
              <div className="absolute inset-y-0 right-0 w-[48%] px-4">
                {awayLineup.length > 0 && renderFormation(awayLineup, awayTeam, false, awayFormation)}
              </div>
            </div>
          </div>

          {/* Match Events */}
          <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <Shirt className="text-primary-400" />
              Match Events
            </h3>

            <div className="space-y-3 max-h-96 overflow-y-auto">
              {visibleEvents.length > 0 ? (
                visibleEvents
                  .sort((a, b) => b.minute - a.minute)
                  .map((event, index) => (
                    <div key={index} className="flex items-center gap-3 p-3 bg-gray-700/30 rounded-lg">
                      <span className="text-primary-400 font-bold min-w-[2rem]">{event.minute}'</span>
                      <div className="flex-1">
                        <div className="text-white font-semibold">{event.player}</div>
                        <div className="text-gray-300 text-sm">{event.description}</div>
                        <div className="text-gray-400 text-xs">{event.team}</div>
                      </div>
                      <div className="text-xl">
                        {event.event_type === 'goal' && '⚽'}
                        {event.event_type === 'yellow_card' && '🟨'}
                        {event.event_type === 'red_card' && '🟥'}
                        {event.event_type === 'substitution' && '🔄'}
                      </div>
                    </div>
                  ))
              ) : (
                <div className="text-center py-8">
                  <div className="text-gray-400 text-lg mb-2">No events yet</div>
                  <p className="text-gray-500 text-sm">
                    Start the simulation to see match events
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default TournamentMatchSimulator
