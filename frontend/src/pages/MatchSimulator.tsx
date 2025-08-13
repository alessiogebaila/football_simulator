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
  const [simulationSpeed, setSimulationSpeed] = useState<number>(200) // milliseconds per minute (Normal = 5 min/sec)

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

  const renderPlayerCard = (player: Player, isHome: boolean = true) => {
    const getPositionColor = (position: string) => {
      switch (position) {
        case 'GK': return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30'
        case 'CB':
        case 'LB': 
        case 'RB': return 'bg-blue-500/20 text-blue-300 border-blue-500/30'
        case 'CDM':
        case 'CM':
        case 'CAM': return 'bg-green-500/20 text-green-300 border-green-500/30'
        case 'LW':
        case 'RW':
        case 'ST':
        case 'CF': return 'bg-red-500/20 text-red-300 border-red-500/30'
        default: return 'bg-gray-500/20 text-gray-300 border-gray-500/30'
      }
    }

    // Use fixed width for cards to ensure consistent sizing
    const cardSize = 'w-16 p-2'
    const textSize = 'text-xs'
    
    // Apply rotation based on team: home team faces right, away team faces left
    // Counter-rotate the cards so text remains readable
    const rotationClass = isHome ? 'transform -rotate-90' : 'transform rotate-90'
    
    // Check for player events
    const playerEvents = match && match.events ? match.events.filter(e => 
      (e.player === player.name || e.player.startsWith(player.name + ' →'))
    ) : [];
    
    const hasGoal = playerEvents.some(e => e.event_type === 'goal');
    const hasYellowCard = playerEvents.some(e => e.event_type === 'yellow_card');
    const hasRedCard = playerEvents.some(e => e.event_type === 'red_card');
    const isSubbedOut = playerEvents.some(e => e.event_type === 'substitution' && e.player.startsWith(player.name + ' →'));
    const isSubbedIn = match && match.events ? match.events.some(e => 
      e.event_type === 'substitution' && e.player.includes('→ ' + player.name)
    ) : false;
    
    // Extract last name or first name if no space
    const lastName = player.name.includes(' ') ? 
      player.name.split(' ').slice(-1)[0] : 
      player.name;

    return (
      <div className="relative flex flex-col items-center">
        {/* Event indicators above player card */}
        {(hasGoal || hasYellowCard || hasRedCard || isSubbedOut || isSubbedIn) && (
          <div className="absolute -top-2 left-0 right-0 flex justify-center gap-1 z-10">
            {hasGoal && <span className="bg-green-900/80 text-white text-xs rounded-sm h-5 w-5 flex items-center justify-center">⚽</span>}
            {hasYellowCard && <span className="bg-yellow-500/80 text-white text-xs px-1.5 py-0.5 flex items-center justify-center" style={{height: '12px', width: '8px'}}></span>}
            {hasRedCard && <span className="bg-red-500/80 text-white text-xs px-1.5 py-0.5 flex items-center justify-center" style={{height: '12px', width: '8px'}}></span>}
            {(isSubbedOut || isSubbedIn) && <span className="bg-blue-500/80 text-white text-xs rounded-sm h-5 w-5 flex items-center justify-center">🔄</span>}
          </div>
        )}
        
        {/* Player card with fixed dimensions */}
        <div className={`${cardSize} ${isSubbedOut ? 'opacity-50' : ''} ${rotationClass} bg-gray-800/80 backdrop-blur-sm rounded-sm border ${getPositionColor(player.position)} transition-all hover:scale-105`}>
          <div className="text-center">
            <div className={`${textSize} opacity-80`}>
              {player.position}
            </div>
            {player.kit_number !== '-' && (
              <div className={`${textSize} text-gray-400`}>
                #{player.kit_number}
              </div>
            )}
          </div>
        </div>
        
        {/* Player name positioned below the card */}
        <div className="mt-1 text-center">
          <span className="text-[10px] font-medium text-white bg-gray-800/70 px-1 py-0.5 rounded">
            {lastName}
          </span>
        </div>
      </div>
    )
  }

  const renderFormation = (lineup: Player[], teamName: string, isHome: boolean, formation: string) => {
    // Formation-specific positioning logic
    const getFormationLayout = (formation: string, players: Player[]) => {
      const goalkeeper = players.find(p => p.position === 'GK')
      
      // Special handling for Barcelona - make sure CDMs are shown as CMs in 4-2-3-1
      if (teamName.includes('Barcelona') && (formation === '4-2-3-1' || formation === '4-3-2-1')) {
        players.forEach(player => {
          if (player.position === 'CDM') player.position = 'CM'
        })
      }
      
      // Special handling for Real Madrid - ensure CDMs are positioned correctly in midfield line
      if (teamName.includes('Real Madrid') && formation === '4-3-1-2') {
        // Adjust positioning for Real Madrid's midfield
        const cdmPlayers = players.filter(p => p.position === 'CDM')
        if (cdmPlayers.length > 0) {
          // Keep one CDM as CDM, convert others to CM to place them in the midfield line
          if (cdmPlayers.length > 1) {
            cdmPlayers.slice(1).forEach(p => p.position = 'CM')
          }
        }
      }
      
      // For away team, swap LB/RB and LW/RW to mirror the formation
      const defenders = players.filter(p => ['CB', 'LB', 'RB'].includes(p.position))
      
      // If away team, swap wingers and fullbacks to mirror formations
      if (!isHome) {
        defenders.forEach(player => {
          if (player.position === 'LB') player.position = 'RB'
          else if (player.position === 'RB') player.position = 'LB'
        })
      }
      
      const midfielders = players.filter(p => ['CDM', 'CM', 'CAM', 'LW', 'RW'].includes(p.position))
      
      // Mirror LW/RW for away team
      if (!isHome) {
        midfielders.forEach(player => {
          if (player.position === 'LW') player.position = 'RW'
          else if (player.position === 'RW') player.position = 'LW'
        })
      }
      
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

        case "4-2-3-1":
          lines = [
            { type: 'attack', players: attackers.slice(0, 1), layout: 'center' },
            { type: 'attacking', players: [
              ...midfielders.filter(p => p.position === 'LW').slice(0, 1),
              ...midfielders.filter(p => p.position === 'CAM').slice(0, 1),
              ...midfielders.filter(p => p.position === 'RW').slice(0, 1)
            ], layout: 'attacking-line' },
            { type: 'defensive-mid', players: midfielders.filter(p => ['CDM', 'CM'].includes(p.position)).slice(0, 2), layout: 'center' },
            { type: 'defense', players: defenders, layout: 'defense' },
            { type: 'goalkeeper', players: [goalkeeper].filter(Boolean), layout: 'goalkeeper' }
          ]
          break

        case "4-4-2":
          lines = [
            { type: 'attack', players: attackers.slice(0, 2), layout: 'center' },
            { type: 'midfield-flat', players: [
              ...midfielders.filter(p => p.position === 'LW').slice(0, 1),
              ...midfielders.filter(p => p.position === 'CM').slice(0, 2),
              ...midfielders.filter(p => p.position === 'RW').slice(0, 1)
            ], layout: 'flat-four' },
            { type: 'defense', players: defenders, layout: 'defense' },
            { type: 'goalkeeper', players: [goalkeeper].filter(Boolean), layout: 'center' }
          ]
          break

        case "3-4-2-1":
          lines = [
            { type: 'attack', players: attackers.slice(0, 1), layout: 'center' },
            { type: 'attacking', players: midfielders.filter(p => p.position === 'CAM').slice(0, 2), layout: 'center' },
            { type: 'midfield-flat', players: [
              ...midfielders.filter(p => ['LW', 'LB'].includes(p.position)).slice(0, 1),
              ...midfielders.filter(p => p.position === 'CM').slice(0, 2),
              ...midfielders.filter(p => ['RW', 'RB'].includes(p.position)).slice(0, 1)
            ], layout: 'flat-four' },
            { type: 'defense', players: defenders.filter(p => p.position === 'CB').slice(0, 3), layout: 'center' },
            { type: 'goalkeeper', players: [goalkeeper].filter(Boolean), layout: 'center' }
          ]
          break

        case "3-5-2":
          lines = [
            { type: 'attack', players: attackers.slice(0, 2), layout: 'center' },
            { type: 'midfield-five', players: [
              ...midfielders.filter(p => ['LW', 'LB'].includes(p.position)).slice(0, 1),
              ...midfielders.filter(p => p.position === 'CDM').slice(0, 1),
              ...midfielders.filter(p => p.position === 'CM').slice(0, 2),
              ...midfielders.filter(p => ['RW', 'RB'].includes(p.position)).slice(0, 1)
            ], layout: 'flat-five' },
            { type: 'defense', players: defenders.filter(p => p.position === 'CB').slice(0, 3), layout: 'center' },
            { type: 'goalkeeper', players: [goalkeeper].filter(Boolean), layout: 'center' }
          ]
          break

        case "4-3-1-2":
          lines = [
            { type: 'attack', players: attackers.slice(0, 2), layout: 'center' },
            { type: 'attacking', players: midfielders.filter(p => p.position === 'CAM').slice(0, 1), layout: 'center' },
            { type: 'midfield', players: midfielders.filter(p => ['CDM', 'CM'].includes(p.position)).slice(0, 3), layout: 'center' },
            { type: 'defense', players: defenders, layout: 'defense' },
            { type: 'goalkeeper', players: [goalkeeper].filter(Boolean), layout: 'center' }
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
            <div key={index} className="flex justify-between items-center px-16 mb-6 relative">
              {players.map((player: Player, pIndex: number) => (
                <div key={`${line.type}-${pIndex}`} className={`flex-shrink-0 ${pIndex === 0 ? 'absolute left-4' : 'absolute right-4'}`}>
                  {renderPlayerCard(player, isHome)}
                </div>
              ))}
            </div>
          )

        case 'attacking-line':
          return (
            <div key={index} className="flex justify-between items-center px-8 mb-6 relative">
              {players.slice(0, 1).map((player: Player, pIndex: number) => (
                <div key={`lw-${pIndex}`} className="absolute left-4">
                  {renderPlayerCard(player, isHome)}
                </div>
              ))}
              {players.slice(1, 2).map((player: Player, pIndex: number) => (
                <div key={`cam-${pIndex}`} className="mx-auto">
                  {renderPlayerCard(player, isHome)}
                </div>
              ))}
              {players.slice(2, 3).map((player: Player, pIndex: number) => (
                <div key={`rw-${pIndex}`} className="absolute right-4">
                  {renderPlayerCard(player, isHome)}
                </div>
              ))}
            </div>
          )

        case 'defense':
          return (
            <div key={index} className="flex justify-between items-center px-4 mb-6">
              {players.map((player: Player, pIndex: number) => {
                let positionClass = ""
                if (player.position === 'LB') positionClass = "mr-auto"
                else if (player.position === 'RB') positionClass = "ml-auto"
                else if (player.position === 'CB' && pIndex === 1) positionClass = "mx-6"
                else if (player.position === 'CB' && pIndex === 2) positionClass = "mx-6"
                
                return (
                  <div key={`def-${pIndex}`} className={`flex-shrink-0 ${positionClass}`}>
                    {renderPlayerCard(player, isHome)}
                  </div>
                )
              })}
            </div>
          )

        case 'flat-four':
          return (
            <div key={index} className="flex justify-between items-center px-8 mb-6">
              {players.map((player: Player, pIndex: number) => (
                <div key={`mid-${pIndex}`} className="flex-shrink-0">
                  {renderPlayerCard(player, isHome)}
                </div>
              ))}
            </div>
          )

        case 'flat-five':
          return (
            <div key={index} className="flex justify-between items-center px-4 mb-6">
              {players.map((player: Player, pIndex: number) => (
                <div key={`mid5-${pIndex}`} className="flex-shrink-0">
                  {renderPlayerCard(player, isHome)}
                </div>
              ))}
            </div>
          )

        case 'goalkeeper':
          return (
            <div key={index} className="flex justify-center items-center mb-0">
              {players.map((player: Player, pIndex: number) => (
                <div key={`gk-${pIndex}`} className="flex-shrink-0">
                  {renderPlayerCard(player, isHome)}
                </div>
              ))}
            </div>
          )

        default:
          return (
            <div key={index} className="flex justify-center items-center gap-6 mb-6">
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
    
    // For home team: normal formation, then rotate 90 degrees
    // For away team: normal formation (strikers face up), then rotate -90 degrees
    const displayLines = formationLines

    return (
      <div className="relative">
        <div className="flex items-center justify-between mb-4">
          <h3 className={`text-xl font-bold flex items-center gap-2 ${isHome ? 'text-blue-400' : 'text-red-400'}`}>
            <Shirt size={20} />
            {teamName}
          </h3>
          <div className={`px-3 py-1 rounded-full text-sm font-semibold ${isHome ? 'bg-blue-500/20 text-blue-300' : 'bg-red-500/20 text-red-300'}`}>
            {formation}
          </div>
        </div>
        
        <div className={`relative rounded-lg p-4 min-h-[500px] ${isHome ? 'transform rotate-90' : 'transform -rotate-90'}`}>
          <div className="relative h-full flex flex-col justify-between py-6">
            {displayLines.map((line, index) => renderLine(line, index))}
          </div>
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
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700 h-[600px]">
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
              
            <div className="pt-4 space-y-6">
              {/* Simulation Mode Section */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-white">Simulation Mode</h3>
                
                {/* Quick vs Live buttons */}
                <div className="grid grid-cols-2 gap-3">
                  <button
                    onClick={() => simulateMatch(false)}
                    disabled={!homeTeam || !awayTeam || isSimulating}
                    className="py-3 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors text-sm"
                  >
                    Quick Sim
                  </button>
                  <button
                    onClick={() => {
                      setIsLiveMode(true)
                      simulateMatch(true)
                    }}
                    disabled={!homeTeam || !awayTeam || isSimulating}
                    className="py-3 px-4 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors text-sm"
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
                          : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                      }`}
                    >
                      Slow
                    </button>
                    <button
                      onClick={() => setSimulationSpeed(200)}
                      className={`py-2 px-3 rounded-lg text-sm font-medium transition-colors ${
                        simulationSpeed === 200 
                          ? 'bg-primary-600 text-white' 
                          : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                      }`}
                    >
                      Normal
                    </button>
                    <button
                      onClick={() => setSimulationSpeed(100)}
                      className={`py-2 px-3 rounded-lg text-sm font-medium transition-colors ${
                        simulationSpeed === 100 
                          ? 'bg-primary-600 text-white' 
                          : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
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
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700 h-[600px]">
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
              
              <div className="space-y-4 text-sm">
                {/* Possession with bar */}
                <div className="space-y-2">
                  <div className="flex justify-between text-xs text-gray-400">
                    <span>Possession</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-white w-8 text-left">{liveStats.possession_home}%</span>
                    <div className="flex-1 bg-gray-700 rounded-full h-2">
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
                    <div className="flex-1 bg-gray-700 rounded-full h-2">
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
                    <div className="flex-1 bg-gray-700 rounded-full h-2">
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
                    <div className="flex-1 bg-gray-700 rounded-full h-2">
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
                    <div className="flex-1 bg-gray-700 rounded-full h-2">
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
                    <div className="flex-1 bg-gray-700 rounded-full h-2">
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
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700 h-[600px]">
          <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
            <Activity className="text-primary-400" />
            Match Events
          </h2>

          {visibleEvents.length > 0 ? (
            <div className="space-y-4">
              {/* Event Summary */}
              <div className="bg-gray-700/30 rounded-lg p-4 space-y-3">
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
                  </div>
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
      <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700 mt-8">
        <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
          <Users className="text-primary-400" />
          {(homeTeam && awayTeam) ? 'Match Formations' : 'Football Pitch'}
        </h3>
        
        {/* Enhanced football field with horizontal formations */}
        <div className="relative border-2 border-white rounded-lg bg-gradient-to-br from-[#2a7828] to-[#1e5a1e] aspect-[2/1] p-4 overflow-hidden shadow-2xl">
          {/* Field markings */}
          <div className="absolute inset-0">
            {/* Center circle */}
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[25%] h-[50%] rounded-full border-2 border-white"></div>
            {/* Center dot */}
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-2 h-2 rounded-full bg-white"></div>
            {/* Center line */}
            <div className="absolute top-0 bottom-0 left-1/2 transform -translate-x-1/2 w-0.5 bg-white"></div>
            
            {/* Left penalty area */}
            <div className="absolute top-1/2 left-0 transform -translate-y-1/2 w-[18%] h-[55%] border-r-2 border-t-2 border-b-2 border-white"></div>
            {/* Right penalty area */}
            <div className="absolute top-1/2 right-0 transform -translate-y-1/2 w-[18%] h-[55%] border-l-2 border-t-2 border-b-2 border-white"></div>
            
            {/* Left goal area */}
            <div className="absolute top-1/2 left-0 transform -translate-y-1/2 w-[8%] h-[25%] border-r-2 border-t-2 border-b-2 border-white"></div>
            {/* Right goal area */}
            <div className="absolute top-1/2 right-0 transform -translate-y-1/2 w-[8%] h-[25%] border-l-2 border-t-2 border-b-2 border-white"></div>
            
            {/* Goals */}
            <div className="absolute top-1/2 left-0 transform -translate-y-1/2 -translate-x-full w-3 h-[20%] bg-white border border-gray-300"></div>
            <div className="absolute top-1/2 right-0 transform -translate-y-1/2 translate-x-full w-3 h-[20%] bg-white border border-gray-300"></div>
            
            {/* Corner arcs */}
            <div className="absolute top-0 left-0 w-4 h-4 border-r-2 border-b-2 border-white rounded-br-full"></div>
            <div className="absolute top-0 right-0 w-4 h-4 border-l-2 border-b-2 border-white rounded-bl-full"></div>
            <div className="absolute bottom-0 left-0 w-4 h-4 border-r-2 border-t-2 border-white rounded-tr-full"></div>
            <div className="absolute bottom-0 right-0 w-4 h-4 border-l-2 border-t-2 border-white rounded-tl-full"></div>
            
            {/* Penalty spots */}
            <div className="absolute top-1/2 left-[12%] transform -translate-x-1/2 -translate-y-1/2 w-1.5 h-1.5 rounded-full bg-white"></div>
            <div className="absolute top-1/2 right-[12%] transform translate-x-1/2 -translate-y-1/2 w-1.5 h-1.5 rounded-full bg-white"></div>
          </div>

          {/* Home team formation (left side) */}
          <div className="absolute inset-y-0 left-0 w-[48%] px-4">
            {homeLineup.length > 0 && renderFormation(homeLineup, homeTeam, true, homeFormation)}
          </div>
          
          {/* Away team formation (right side) */}
          <div className="absolute inset-y-0 right-0 w-[48%] px-4">
            {awayLineup.length > 0 && renderFormation(awayLineup, awayTeam, false, awayFormation)}
          </div>

          {/* Empty pitch message when no teams selected */}
          {(!homeTeam || !awayTeam) && (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-white/60 text-center">
                <div className="text-4xl mb-2">⚽</div>
                <div className="text-lg font-medium">Select teams to see formations</div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default MatchSimulator
