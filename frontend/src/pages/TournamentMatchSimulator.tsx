import React, { useState, useEffect } from 'react'
import api from '../services/api'
import { Team, Player, Match, MatchEvent } from '../types'

interface TournamentMatchSimulatorProps {
  homeTeam: string
  awayTeam: string
  onMatchComplete: (result: { homeScore: number; awayScore: number; winner: string }) => void
}

interface ExtendedMatchEvent extends MatchEvent {
  id: string
  type: string
}

const TournamentMatchSimulator: React.FC<TournamentMatchSimulatorProps> = ({
  homeTeam,
  awayTeam,
  onMatchComplete
}) => {
  const [match, setMatch] = useState<Match | null>(null)
  const [events, setEvents] = useState<ExtendedMatchEvent[]>([])
  const [homeTeamData, setHomeTeamData] = useState<Team | null>(null)
  const [awayTeamData, setAwayTeamData] = useState<Team | null>(null)
  const [homeFormation, setHomeFormation] = useState<Player[]>([])
  const [awayFormation, setAwayFormation] = useState<Player[]>([])
  const [isSimulating, setIsSimulating] = useState(false)
  const [matchCompleted, setMatchCompleted] = useState(false)

  useEffect(() => {
    loadTeamData()
  }, [homeTeam, awayTeam])

  const loadTeamData = async () => {
    try {
      const [homeResponse, awayResponse] = await Promise.all([
        api.getTeam(homeTeam),
        api.getTeam(awayTeam)
      ])
      setHomeTeamData(homeResponse)
      setAwayTeamData(awayResponse)
      setHomeFormation(homeResponse.players.slice(0, 11))
      setAwayFormation(awayResponse.players.slice(0, 11))
    } catch (error) {
      console.error('Failed to load team data:', error)
    }
  }

  const startLiveSimulation = async () => {
    if (!homeTeamData || !awayTeamData) return

    setIsSimulating(true)
    setEvents([])
    setMatch(null)

    try {
      const result = await api.simulateLiveMatch(homeTeam, awayTeam)
      setMatch(result)
      
      // Simulate live events
      const eventTypes = ['goal', 'yellow_card', 'red_card', 'substitution', 'corner', 'free_kick']
      const simulatedEvents: MatchEvent[] = []

      // Add goals based on final score
      for (let i = 0; i < result.home_score; i++) {
        simulatedEvents.push({
          id: `home_goal_${i}`,
          type: 'goal',
          minute: Math.floor(Math.random() * 90) + 1,
          event_type: 'goal',
          team: homeTeam,
          player: homeTeamData.players[Math.floor(Math.random() * 11)].name,
          description: `Goal by ${homeTeamData.players[Math.floor(Math.random() * 11)].name}`
        })
      }

      for (let i = 0; i < result.away_score; i++) {
        simulatedEvents.push({
          id: `away_goal_${i}`,
          type: 'goal',
          minute: Math.floor(Math.random() * 90) + 1,
          event_type: 'goal',
          team: awayTeam,
          player: awayTeamData.players[Math.floor(Math.random() * 11)].name,
          description: `Goal by ${awayTeamData.players[Math.floor(Math.random() * 11)].name}`
        })
      }

      // Add some random events
      for (let i = 0; i < Math.floor(Math.random() * 5) + 2; i++) {
        const eventType = eventTypes[Math.floor(Math.random() * eventTypes.length)]
        const isHomeTeam = Math.random() > 0.5
        const team = isHomeTeam ? homeTeamData : awayTeamData
        const teamName = isHomeTeam ? homeTeam : awayTeam

        simulatedEvents.push({
          id: `event_${i}`,
          type: eventType,
          minute: Math.floor(Math.random() * 90) + 1,
          event_type: eventType,
          team: teamName,
          player: team.players[Math.floor(Math.random() * 11)].name,
          description: `${eventType.replace('_', ' ')} - ${team.players[Math.floor(Math.random() * 11)].name}`
        })
      }

      // Sort events by minute
      simulatedEvents.sort((a, b) => a.minute - b.minute)

      // Animate events
      for (const event of simulatedEvents) {
        await new Promise(resolve => setTimeout(resolve, 1000))
        setEvents(prev => [...prev, event as ExtendedMatchEvent])
      }

      setMatchCompleted(true)
      
      // Call completion callback
      onMatchComplete({
        homeScore: result.home_score,
        awayScore: result.away_score,
        winner: result.home_score > result.away_score ? homeTeam : awayTeam
      })

    } catch (error) {
      console.error('Failed to simulate match:', error)
    } finally {
      setIsSimulating(false)
    }
  }

  const getPositionStyle = (position: string, index: number, isHome: boolean) => {
    const formations = {
      'GK': { x: isHome ? 5 : 95, y: 50 },
      'LB': { x: isHome ? 20 : 80, y: 15 },
      'CB': { x: isHome ? 20 : 80, y: index % 2 === 0 ? 35 : 65 },
      'RB': { x: isHome ? 20 : 80, y: 85 },
      'LM': { x: isHome ? 40 : 60, y: 20 },
      'CM': { x: isHome ? 40 : 60, y: 50 },
      'RM': { x: isHome ? 40 : 60, y: 80 },
      'LW': { x: isHome ? 70 : 30, y: 25 },
      'ST': { x: isHome ? 70 : 30, y: 50 },
      'RW': { x: isHome ? 70 : 30, y: 75 }
    }

    const basePosition = formations[position as keyof typeof formations] || formations['CM']
    
    return {
      left: `${basePosition.x}%`,
      top: `${basePosition.y}%`,
      transform: 'translate(-50%, -50%)'
    }
  }

  const getPlayersByPosition = (players: Player[]) => {
    const positions = {
      'GK': players.filter(p => p.position === 'GK').slice(0, 1),
      'LB': players.filter(p => p.position === 'LB').slice(0, 1),
      'CB': players.filter(p => p.position === 'CB').slice(0, 2),
      'RB': players.filter(p => p.position === 'RB').slice(0, 1),
      'LM': players.filter(p => p.position === 'LM').slice(0, 1),
      'CM': players.filter(p => p.position === 'CM').slice(0, 1),
      'RM': players.filter(p => p.position === 'RM').slice(0, 1),
      'LW': players.filter(p => p.position === 'LW').slice(0, 1),
      'ST': players.filter(p => p.position === 'ST').slice(0, 1),
      'RW': players.filter(p => p.position === 'RW').slice(0, 1)
    }

    return positions
  }

  return (
    <div className="bg-gradient-to-br from-green-900/20 to-blue-900/20 min-h-screen p-6">
      <div className="max-w-7xl mx-auto">
        {/* Match Header */}
        <div className="bg-slate-800 rounded-lg p-6 mb-6 border border-slate-700">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-4">
              <div className="text-center">
                <h2 className="text-2xl font-bold text-white">{homeTeam}</h2>
                <p className="text-gray-400">Home</p>
              </div>
              <div className="text-4xl font-bold text-white mx-8">
                {match ? `${match.home_score} - ${match.away_score}` : 'VS'}
              </div>
              <div className="text-center">
                <h2 className="text-2xl font-bold text-white">{awayTeam}</h2>
                <p className="text-gray-400">Away</p>
              </div>
            </div>
            <div className="text-right">
              {!isSimulating && !matchCompleted && (
                <button
                  onClick={startLiveSimulation}
                  className="bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-6 rounded-lg transition-colors"
                >
                  Start Live Match
                </button>
              )}
              {isSimulating && (
                <div className="text-yellow-400 font-bold">
                  Match in Progress...
                </div>
              )}
              {matchCompleted && (
                <div className="text-green-400 font-bold">
                  Match Completed!
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Football Field */}
          <div className="lg:col-span-2">
            <div className="bg-gradient-to-br from-green-600 to-green-700 rounded-lg p-6 relative h-96 border-2 border-white">
              {/* Field markings */}
              <div className="absolute inset-4 border-2 border-white rounded">
                {/* Center circle */}
                <div className="absolute left-1/2 top-1/2 w-20 h-20 border-2 border-white rounded-full transform -translate-x-1/2 -translate-y-1/2"></div>
                <div className="absolute left-1/2 top-1/2 w-1 h-1 bg-white rounded-full transform -translate-x-1/2 -translate-y-1/2"></div>
                
                {/* Center line */}
                <div className="absolute left-1/2 top-0 bottom-0 w-0.5 bg-white transform -translate-x-1/2"></div>
                
                {/* Goals */}
                <div className="absolute left-0 top-1/2 w-4 h-16 border-2 border-white border-l-0 transform -translate-y-1/2"></div>
                <div className="absolute right-0 top-1/2 w-4 h-16 border-2 border-white border-r-0 transform -translate-y-1/2"></div>
                
                {/* Penalty boxes */}
                <div className="absolute left-0 top-1/2 w-16 h-32 border-2 border-white border-l-0 transform -translate-y-1/2"></div>
                <div className="absolute right-0 top-1/2 w-16 h-32 border-2 border-white border-r-0 transform -translate-y-1/2"></div>
              </div>

              {/* Home Team Players */}
              {homeFormation.map((player) => {
                const positions = getPlayersByPosition(homeFormation)
                let positionKey = 'CM'
                let positionIndex = 0

                for (const [pos, players] of Object.entries(positions)) {
                  const playerIndex = players.findIndex(p => p.name === player.name)
                  if (playerIndex !== -1) {
                    positionKey = pos
                    positionIndex = playerIndex
                    break
                  }
                }

                return (
                  <div
                    key={`home-${player.name}`}
                    className="absolute"
                    style={getPositionStyle(positionKey, positionIndex, true)}
                  >
                    <div className="w-8 h-8 bg-blue-600 rounded-full border-2 border-white flex items-center justify-center text-white text-xs font-bold shadow-lg">
                      {player.name.split(' ').map(n => n[0]).join('').slice(0, 2)}
                    </div>
                    <div className="text-white text-xs mt-1 text-center font-semibold bg-black bg-opacity-50 rounded px-1">
                      {player.name.split(' ').pop()?.slice(0, 8)}
                    </div>
                  </div>
                )
              })}

              {/* Away Team Players */}
              {awayFormation.map((player) => {
                const positions = getPlayersByPosition(awayFormation)
                let positionKey = 'CM'
                let positionIndex = 0

                for (const [pos, players] of Object.entries(positions)) {
                  const playerIndex = players.findIndex(p => p.name === player.name)
                  if (playerIndex !== -1) {
                    positionKey = pos
                    positionIndex = playerIndex
                    break
                  }
                }

                return (
                  <div
                    key={`away-${player.name}`}
                    className="absolute"
                    style={getPositionStyle(positionKey, positionIndex, false)}
                  >
                    <div className="w-8 h-8 bg-red-600 rounded-full border-2 border-white flex items-center justify-center text-white text-xs font-bold shadow-lg">
                      {player.name.split(' ').map(n => n[0]).join('').slice(0, 2)}
                    </div>
                    <div className="text-white text-xs mt-1 text-center font-semibold bg-black bg-opacity-50 rounded px-1">
                      {player.name.split(' ').pop()?.slice(0, 8)}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Match Events */}
          <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
            <h3 className="text-xl font-bold text-white mb-4">Match Events</h3>
            <div className="space-y-3 max-h-80 overflow-y-auto">
              {events.length === 0 && !isSimulating && (
                <p className="text-gray-400 text-center py-8">
                  Start the match to see live events
                </p>
              )}
              {events.map((event) => (
                <div key={event.id} className="bg-slate-700 rounded p-3">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-yellow-400 font-bold">{event.minute}'</span>
                    <span className={`text-sm ${
                      event.type === 'goal' ? 'text-green-400' : 
                      event.type === 'red_card' ? 'text-red-400' :
                      event.type === 'yellow_card' ? 'text-yellow-400' :
                      'text-blue-400'
                    }`}>
                      {event.type.replace('_', ' ').toUpperCase()}
                    </span>
                  </div>
                  <p className="text-white text-sm">{event.team}</p>
                  <p className="text-gray-300 text-xs">{event.description}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Match Statistics */}
        {match && (
          <div className="bg-slate-800 rounded-lg p-6 mt-6 border border-slate-700">
            <h3 className="text-xl font-bold text-white mb-4">Match Statistics</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-400">{match.stats?.possession_home || 50}%</div>
                <div className="text-gray-400">Possession</div>
                <div className="text-gray-400">{homeTeam}</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-400">{match.stats?.possession_away || 50}%</div>
                <div className="text-gray-400">Possession</div>
                <div className="text-gray-400">{awayTeam}</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-400">{match.stats?.shots_home || 0}</div>
                <div className="text-gray-400">Shots</div>
                <div className="text-gray-400">{homeTeam}</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-400">{match.stats?.shots_away || 0}</div>
                <div className="text-gray-400">Shots</div>
                <div className="text-gray-400">{awayTeam}</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default TournamentMatchSimulator
