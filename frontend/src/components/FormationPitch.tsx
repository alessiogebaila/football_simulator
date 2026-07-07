import React from 'react'
import { Shirt } from 'lucide-react'
import { MatchEvent, Player } from '../types'

// A slot is a tactical position on one half of the pitch.
// x: 0 = own goal line, 100 = halfway line. y: 0 = top touchline, 100 = bottom.
interface FormationSlot {
  accepts: string[]
  x: number
  y: number
}

const BACK_FOUR: FormationSlot[] = [
  { accepts: ['LB', 'CB'], x: 27, y: 12 },
  { accepts: ['CB'], x: 23, y: 37 },
  { accepts: ['CB'], x: 23, y: 63 },
  { accepts: ['RB', 'CB'], x: 27, y: 88 },
]

const BACK_THREE: FormationSlot[] = [
  { accepts: ['CB', 'LB'], x: 25, y: 24 },
  { accepts: ['CB'], x: 21, y: 50 },
  { accepts: ['CB', 'RB'], x: 25, y: 76 },
]

const GK_SLOT: FormationSlot = { accepts: ['GK'], x: 6, y: 50 }

const FORMATION_TEMPLATES: Record<string, FormationSlot[]> = {
  '4-3-3': [
    GK_SLOT,
    ...BACK_FOUR,
    { accepts: ['CDM', 'CM'], x: 47, y: 50 },
    { accepts: ['CM', 'CAM', 'CDM'], x: 60, y: 28 },
    { accepts: ['CM', 'CAM', 'CDM'], x: 60, y: 72 },
    { accepts: ['LW', 'CAM', 'CM'], x: 80, y: 13 },
    { accepts: ['RW', 'CAM', 'CM'], x: 80, y: 87 },
    { accepts: ['ST', 'CF', 'CAM'], x: 91, y: 50 },
  ],
  '4-2-3-1': [
    GK_SLOT,
    ...BACK_FOUR,
    { accepts: ['CDM', 'CM'], x: 46, y: 35 },
    { accepts: ['CDM', 'CM'], x: 46, y: 65 },
    { accepts: ['LW', 'CAM', 'CM'], x: 71, y: 13 },
    { accepts: ['CAM', 'CM'], x: 69, y: 50 },
    { accepts: ['RW', 'CAM', 'CM'], x: 71, y: 87 },
    { accepts: ['ST', 'CF', 'CAM'], x: 91, y: 50 },
  ],
  '4-4-2': [
    GK_SLOT,
    ...BACK_FOUR,
    { accepts: ['LW', 'CM', 'CAM'], x: 56, y: 12 },
    { accepts: ['CM', 'CDM'], x: 50, y: 37 },
    { accepts: ['CM', 'CDM'], x: 50, y: 63 },
    { accepts: ['RW', 'CM', 'CAM'], x: 56, y: 88 },
    { accepts: ['ST', 'CF'], x: 88, y: 37 },
    { accepts: ['ST', 'CF', 'CAM'], x: 88, y: 63 },
  ],
  '4-3-1-2': [
    GK_SLOT,
    ...BACK_FOUR,
    { accepts: ['CM', 'CDM'], x: 49, y: 25 },
    { accepts: ['CDM', 'CM'], x: 44, y: 50 },
    { accepts: ['CM', 'CDM'], x: 49, y: 75 },
    { accepts: ['CAM', 'CM'], x: 68, y: 50 },
    { accepts: ['ST', 'CF'], x: 88, y: 37 },
    { accepts: ['ST', 'CF', 'CAM'], x: 88, y: 63 },
  ],
  '3-5-2': [
    GK_SLOT,
    ...BACK_THREE,
    { accepts: ['LB', 'LW', 'CM'], x: 52, y: 10 },
    { accepts: ['CDM', 'CM'], x: 46, y: 50 },
    { accepts: ['CM', 'CAM'], x: 60, y: 30 },
    { accepts: ['CM', 'CAM'], x: 60, y: 70 },
    { accepts: ['RB', 'RW', 'CM'], x: 52, y: 90 },
    { accepts: ['ST', 'CF'], x: 88, y: 37 },
    { accepts: ['ST', 'CF', 'CAM'], x: 88, y: 63 },
  ],
  '3-4-2-1': [
    GK_SLOT,
    ...BACK_THREE,
    { accepts: ['LB', 'LW', 'CM'], x: 54, y: 10 },
    { accepts: ['CM', 'CDM'], x: 48, y: 37 },
    { accepts: ['CM', 'CDM'], x: 48, y: 63 },
    { accepts: ['RB', 'RW', 'CM'], x: 54, y: 90 },
    { accepts: ['CAM', 'LW', 'CM'], x: 73, y: 32 },
    { accepts: ['CAM', 'RW', 'CM'], x: 73, y: 68 },
    { accepts: ['ST', 'CF', 'CAM'], x: 91, y: 50 },
  ],
}

const positionRing = (position: string): string => {
  if (position === 'GK') return 'ring-amber-400'
  if (['CB', 'LB', 'RB'].includes(position)) return 'ring-sky-400'
  if (['CDM', 'CM', 'CAM'].includes(position)) return 'ring-emerald-300'
  return 'ring-rose-400'
}

// Greedily fill each slot with the best-matching remaining player so all
// eleven end up on the pitch even when positions don't match the template.
const assignPlayersToSlots = (players: Player[], slots: FormationSlot[]) => {
  const remaining = [...players]
  const take = (pred: (p: Player) => boolean): Player | null => {
    const i = remaining.findIndex(pred)
    return i >= 0 ? remaining.splice(i, 1)[0] : null
  }
  const placed: Array<{ slot: FormationSlot; player: Player }> = []
  for (const slot of slots) {
    let player: Player | null = null
    for (const role of slot.accepts) {
      player = take(p => p.position === role)
      if (player) break
    }
    if (!player) {
      player = slot.accepts.includes('GK')
        ? take(() => true)
        : take(p => p.position !== 'GK') || take(() => true)
    }
    if (player) placed.push({ slot, player })
  }
  return placed
}

interface PlayerFlags {
  goals: number
  yellow: boolean
  red: boolean
  subbedOut: boolean
  subbedIn: boolean
}

const getEventFlags = (player: Player, events: MatchEvent[]): PlayerFlags => {
  const own = events.filter(
    e => e.player === player.name || e.player.startsWith(player.name + ' →')
  )
  return {
    goals: own.filter(e => e.event_type === 'goal').length,
    yellow: own.some(e => e.event_type === 'yellow_card'),
    red: own.some(e => e.event_type === 'red_card'),
    subbedOut: own.some(
      e => e.event_type === 'substitution' && e.player.startsWith(player.name + ' →')
    ),
    subbedIn: events.some(
      e => e.event_type === 'substitution' && e.player.includes('→ ' + player.name)
    ),
  }
}

const lastName = (name: string) =>
  name.includes(' ') ? name.split(' ').slice(-1)[0] : name

interface FormationPitchProps {
  homeTeam: string
  awayTeam: string
  homeLineup: Player[]
  awayLineup: Player[]
  homeFormation: string
  awayFormation: string
  events?: MatchEvent[]
}

const FormationPitch: React.FC<FormationPitchProps> = ({
  homeTeam,
  awayTeam,
  homeLineup,
  awayLineup,
  homeFormation,
  awayFormation,
  events,
}) => {
  const renderTeam = (lineup: Player[], formation: string, isHome: boolean) => {
    if (lineup.length === 0) return null
    const slots = FORMATION_TEMPLATES[formation] || FORMATION_TEMPLATES['4-3-3']
    const placed = assignPlayersToSlots(lineup, slots)

    return placed.map(({ slot, player }) => {
      // Map half-pitch coordinates onto the full pitch; away team is mirrored.
      const left = isHome ? 2.5 + slot.x * 0.455 : 97.5 - slot.x * 0.455
      const top = isHome ? 8 + slot.y * 0.82 : 8 + (100 - slot.y) * 0.82
      const flags = getEventFlags(player, events || [])

      return (
        <div
          key={`${isHome ? 'h' : 'a'}-${player.name}`}
          className="absolute z-10 flex flex-col items-center"
          style={{ left: `${left}%`, top: `${top}%`, transform: 'translate(-50%, -50%)' }}
        >
          <div
            className={`relative flex h-8 w-8 items-center justify-center rounded-full text-[10px] font-bold text-white shadow-lg ring-2 sm:h-10 sm:w-10 sm:text-xs ${positionRing(
              player.position
            )} ${
              isHome
                ? 'bg-gradient-to-b from-blue-500 to-blue-800'
                : 'bg-gradient-to-b from-red-500 to-red-800'
            } ${flags.subbedOut ? 'opacity-50' : ''}`}
          >
            {player.overall_rating}
            {flags.goals > 0 && (
              <span className="absolute -right-1.5 -top-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-white text-[9px] shadow">
                ⚽{flags.goals > 1 ? flags.goals : ''}
              </span>
            )}
            {(flags.yellow || flags.red) && (
              <span
                className={`absolute -left-1 -top-1.5 h-3.5 w-2.5 rounded-[2px] shadow ${
                  flags.red ? 'bg-red-500' : 'bg-yellow-400'
                }`}
              />
            )}
            {(flags.subbedOut || flags.subbedIn) && (
              <span className="absolute -bottom-1.5 -right-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-blue-100 text-[8px] shadow">
                🔄
              </span>
            )}
          </div>
          <span className="mt-1 max-w-[80px] truncate rounded-full bg-black/60 px-1.5 py-0.5 text-[9px] font-semibold text-white sm:text-[10px]">
            {lastName(player.name)}
          </span>
          <span className="text-[8px] font-medium text-white/70">{player.position}</span>
        </div>
      )
    })
  }

  const teamHeader = (name: string, formation: string, isHome: boolean) => (
    <div className={`flex items-center gap-2 ${isHome ? '' : 'flex-row-reverse'}`}>
      <Shirt size={18} className={isHome ? 'text-blue-400' : 'text-red-400'} />
      <span className="truncate text-base font-bold text-white sm:text-lg">
        {name || (isHome ? 'Home team' : 'Away team')}
      </span>
      {formation && (
        <span
          className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${
            isHome ? 'bg-blue-500/20 text-blue-300' : 'bg-red-500/20 text-red-300'
          }`}
        >
          {formation}
        </span>
      )}
    </div>
  )

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-4">
        {teamHeader(homeTeam, homeFormation, true)}
        {teamHeader(awayTeam, awayFormation, false)}
      </div>

      <div className="relative w-full overflow-hidden rounded-2xl border border-emerald-800/50 bg-gradient-to-br from-[#0d3b24] via-[#0a2e1c] to-[#072216] shadow-2xl shadow-black/50 aspect-[4/3] sm:aspect-[16/9]">
        {/* Mowing stripes */}
        <div
          className="absolute inset-0"
          style={{
            backgroundImage:
              'repeating-linear-gradient(90deg, rgba(255,255,255,0.05) 0px, rgba(255,255,255,0.05) 48px, transparent 48px, transparent 96px)',
          }}
        />

        {/* Pitch markings */}
        <div className="absolute inset-[2.5%] rounded-sm border-2 border-white/25">
          <div className="absolute bottom-0 left-1/2 top-0 w-0.5 -translate-x-1/2 bg-white/25" />
          <div className="absolute left-1/2 top-1/2 h-[38%] aspect-square -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-white/25" />
          <div className="absolute left-1/2 top-1/2 h-1.5 w-1.5 -translate-x-1/2 -translate-y-1/2 rounded-full bg-white/70" />
          {/* Penalty areas */}
          <div className="absolute left-0 top-1/2 h-[58%] w-[15%] -translate-y-1/2 border-2 border-l-0 border-white/25" />
          <div className="absolute right-0 top-1/2 h-[58%] w-[15%] -translate-y-1/2 border-2 border-r-0 border-white/25" />
          {/* Goal areas */}
          <div className="absolute left-0 top-1/2 h-[28%] w-[6%] -translate-y-1/2 border-2 border-l-0 border-white/25" />
          <div className="absolute right-0 top-1/2 h-[28%] w-[6%] -translate-y-1/2 border-2 border-r-0 border-white/25" />
          {/* Penalty spots */}
          <div className="absolute left-[11%] top-1/2 h-1 w-1 -translate-y-1/2 rounded-full bg-white/70" />
          <div className="absolute right-[11%] top-1/2 h-1 w-1 -translate-y-1/2 rounded-full bg-white/70" />
        </div>

        {renderTeam(homeLineup, homeFormation, true)}
        {renderTeam(awayLineup, awayFormation, false)}

        {(!homeTeam || !awayTeam) && (
          <div className="absolute inset-0 z-20 flex items-center justify-center bg-black/30">
            <div className="text-center text-white/80">
              <div className="mb-2 text-4xl">⚽</div>
              <div className="text-lg font-medium">Select teams to see formations</div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default FormationPitch
