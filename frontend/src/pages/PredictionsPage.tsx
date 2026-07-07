import React, { useEffect, useMemo, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  BrainCircuit, TrendingUp, AlertTriangle, ShieldCheck, Target,
  Flag, Activity, Sparkles, ChevronDown,
} from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../services/api'

type Scope = 'club' | 'international'

const fadeUp = {
  initial: { opacity: 0, y: 16 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -8 },
}

const ProbBar: React.FC<{ label: string; value: number; color: string; big?: boolean }> = ({
  label, value, color, big,
}) => (
  <div className="space-y-1">
    <div className="flex justify-between text-sm">
      <span className="text-emerald-100/70">{label}</span>
      <span className={`font-bold tabular-nums ${big ? 'text-lg text-white' : 'text-emerald-50'}`}>
        {(value * 100).toFixed(1)}%
      </span>
    </div>
    <div className="h-2.5 rounded-full bg-emerald-950/80 overflow-hidden">
      <motion.div
        initial={{ width: 0 }}
        animate={{ width: `${value * 100}%` }}
        transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1] }}
        className={`h-full rounded-full ${color}`}
      />
    </div>
  </div>
)

const StatChip: React.FC<{ label: string; value: React.ReactNode }> = ({ label, value }) => (
  <div className="rounded-xl bg-emerald-950/60 border border-emerald-800/40 px-3 py-2 text-center">
    <div className="text-[11px] uppercase tracking-wider text-emerald-100/50">{label}</div>
    <div className="text-base font-bold text-white tabular-nums">{value}</div>
  </div>
)

const PredictionsPage: React.FC = () => {
  const [scope, setScope] = useState<Scope>('club')
  const [teams, setTeams] = useState<{ club: Record<string, string[]>; international: string[] } | null>(null)
  const [homeTeam, setHomeTeam] = useState('')
  const [awayTeam, setAwayTeam] = useState('')
  const [neutral, setNeutral] = useState(false)
  const [showOdds, setShowOdds] = useState(false)
  const [odds, setOdds] = useState({ home: '', draw: '', away: '' })
  const [prediction, setPrediction] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [loadingTeams, setLoadingTeams] = useState(true)

  useEffect(() => {
    api.getEngineTeams()
      .then(setTeams)
      .catch(() => toast.error('Prediction engine unavailable — is the backend running?'))
      .finally(() => setLoadingTeams(false))
  }, [])

  const teamOptions = useMemo(() => {
    if (!teams) return []
    if (scope === 'international') return teams.international
    return Object.entries(teams.club).flatMap(([league, names]) =>
      names.map(n => ({ league, name: n }))
    )
  }, [teams, scope])

  const runPrediction = async () => {
    if (!homeTeam || !awayTeam || homeTeam === awayTeam) {
      toast.error('Pick two different teams')
      return
    }
    setLoading(true)
    try {
      const bookmaker_odds =
        showOdds && odds.home && odds.draw && odds.away
          ? { home: +odds.home, draw: +odds.draw, away: +odds.away }
          : undefined
      const p = await api.getEnginePrediction({
        home_team: homeTeam, away_team: awayTeam, scope, neutral, bookmaker_odds,
      })
      setPrediction(p)
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Prediction failed')
    } finally {
      setLoading(false)
    }
  }

  const selectCls =
    'w-full bg-[#04100a] text-white border border-emerald-800/50 rounded-xl p-3 focus:border-emerald-500 focus:outline-none transition-colors duration-200'

  const probs = prediction?.probabilities

  return (
    <div className="container mx-auto px-4 py-8">
      <motion.div {...fadeUp} className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
          <BrainCircuit className="text-primary-400" />
          Match Predictions
        </h1>
        <p className="text-emerald-100/60">
          Real-data engine: Dixon-Coles + Elo + calibrated gradient boosting, 50,000 Monte Carlo simulations
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: fixture setup */}
        <motion.div {...fadeUp} className="card-glass p-6 space-y-5 h-fit lg:sticky lg:top-24">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Target className="text-primary-400" size={20} />
            Fixture
          </h2>

          {/* Scope toggle */}
          <div className="grid grid-cols-2 gap-2 p-1 rounded-xl bg-emerald-950/70 border border-emerald-800/40">
            {(['club', 'international'] as Scope[]).map(s => (
              <button
                key={s}
                onClick={() => { setScope(s); setHomeTeam(''); setAwayTeam(''); setPrediction(null) }}
                className={`py-2 rounded-lg text-sm font-semibold capitalize transition-all duration-300 ${
                  scope === s
                    ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-900/40'
                    : 'text-emerald-100/60 hover:text-white'
                }`}
              >
                {s === 'club' ? 'Clubs' : 'National teams'}
              </button>
            ))}
          </div>

          {loadingTeams ? (
            <div className="loading-spinner" />
          ) : (
            <>
              <div>
                <label className="block text-emerald-100/70 text-sm font-medium mb-2">Home team</label>
                <select value={homeTeam} onChange={e => setHomeTeam(e.target.value)} className={selectCls}>
                  <option value="">Select team</option>
                  {scope === 'club'
                    ? (teamOptions as { league: string; name: string }[]).map(t => (
                        <option key={t.name} value={t.name}>{t.name} · {t.league}</option>
                      ))
                    : (teamOptions as string[]).map(t => <option key={t} value={t}>{t}</option>)}
                </select>
              </div>

              <div>
                <label className="block text-emerald-100/70 text-sm font-medium mb-2">Away team</label>
                <select value={awayTeam} onChange={e => setAwayTeam(e.target.value)} className={selectCls}>
                  <option value="">Select team</option>
                  {scope === 'club'
                    ? (teamOptions as { league: string; name: string }[]).map(t => (
                        <option key={t.name} value={t.name}>{t.name} · {t.league}</option>
                      ))
                    : (teamOptions as string[]).map(t => <option key={t} value={t}>{t}</option>)}
                </select>
              </div>

              <label className="flex items-center gap-3 text-sm text-emerald-100/70 cursor-pointer">
                <input
                  type="checkbox"
                  checked={neutral}
                  onChange={e => setNeutral(e.target.checked)}
                  className="h-4 w-4 accent-emerald-500"
                />
                Neutral venue (cup final / tournament)
              </label>

              {/* Odds input */}
              <button
                onClick={() => setShowOdds(v => !v)}
                className="flex w-full items-center justify-between text-sm font-semibold text-emerald-300 hover:text-emerald-200 transition-colors"
              >
                <span className="flex items-center gap-2"><TrendingUp size={16} /> Compare bookmaker odds</span>
                <ChevronDown size={16} className={`transition-transform duration-300 ${showOdds ? 'rotate-180' : ''}`} />
              </button>
              <AnimatePresence>
                {showOdds && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                    className="overflow-hidden"
                  >
                    <div className="grid grid-cols-3 gap-2">
                      {(['home', 'draw', 'away'] as const).map(k => (
                        <input
                          key={k}
                          type="number" step="0.01" min="1.01"
                          placeholder={k === 'home' ? '1' : k === 'draw' ? 'X' : '2'}
                          value={odds[k]}
                          onChange={e => setOdds(o => ({ ...o, [k]: e.target.value }))}
                          className={`${selectCls} text-center`}
                        />
                      ))}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              <button onClick={runPrediction} disabled={loading} className="btn-primary w-full py-3 text-base">
                {loading ? 'Running 50,000 simulations…' : 'Predict match'}
              </button>
            </>
          )}
        </motion.div>

        {/* Right: results */}
        <div className="lg:col-span-2 space-y-6">
          <AnimatePresence mode="wait">
            {!prediction && !loading && (
              <motion.div {...fadeUp} key="empty" className="card-glass p-12 text-center">
                <Sparkles className="mx-auto mb-4 text-emerald-500/60" size={48} />
                <p className="text-emerald-100/60 text-lg">
                  Pick a fixture to get full probability distributions, xG, value bets and more.
                </p>
              </motion.div>
            )}

            {loading && (
              <motion.div {...fadeUp} key="loading" className="card-glass p-12 text-center">
                <div className="loading-spinner" />
                <p className="text-emerald-100/60">Fitting models & simulating…</p>
              </motion.div>
            )}

            {prediction && !loading && (
              <motion.div {...fadeUp} key={prediction.match} className="space-y-6">
                {/* Header card */}
                <div className="card-glass p-6">
                  <div className="flex flex-wrap items-center justify-between gap-3 mb-5">
                    <h2 className="text-2xl font-extrabold text-white">{prediction.match}</h2>
                    <div className="flex items-center gap-2">
                      <span className="rounded-full bg-emerald-500/15 border border-emerald-500/30 px-3 py-1 text-xs font-semibold text-emerald-300">
                        {prediction.context?.league}
                      </span>
                      <span className="rounded-full bg-emerald-950/70 border border-emerald-800/50 px-3 py-1 text-xs font-semibold text-emerald-100/70">
                        Confidence {(prediction.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
                    <StatChip
                      label="Home xG"
                      value={<span className="text-emerald-300">{prediction.predicted_xg.home}</span>}
                    />
                    <StatChip
                      label="xG range"
                      value={
                        <span className="text-emerald-100/80 text-sm">
                          {prediction.xg_uncertainty.home_range.join('–')} / {prediction.xg_uncertainty.away_range.join('–')}
                        </span>
                      }
                    />
                    <StatChip
                      label="Away xG"
                      value={<span className="text-rose-300">{prediction.predicted_xg.away}</span>}
                    />
                  </div>

                  <div className="space-y-3">
                    <ProbBar label={`${prediction.match.split(' vs ')[0]} win`} value={probs.home_win} color="bg-gradient-to-r from-emerald-500 to-emerald-400" big />
                    <ProbBar label="Draw" value={probs.draw} color="bg-gradient-to-r from-slate-500 to-slate-400" big />
                    <ProbBar label={`${prediction.match.split(' vs ')[1]} win`} value={probs.away_win} color="bg-gradient-to-r from-rose-500 to-rose-400" big />
                  </div>
                </div>

                {/* Markets grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="card-glass p-6">
                    <h3 className="font-bold text-white mb-4 flex items-center gap-2">
                      <Activity size={18} className="text-primary-400" /> Most likely scorelines
                    </h3>
                    <div className="grid grid-cols-4 gap-2">
                      {prediction.probabilities.top_scorelines.map((s: any, i: number) => (
                        <motion.div
                          key={s.score}
                          initial={{ opacity: 0, scale: 0.8 }}
                          animate={{ opacity: 1, scale: 1 }}
                          transition={{ delay: i * 0.05 }}
                          className={`rounded-xl border px-2 py-3 text-center ${
                            i === 0
                              ? 'bg-emerald-500/15 border-emerald-500/40'
                              : 'bg-emerald-950/60 border-emerald-800/40'
                          }`}
                        >
                          <div className="text-lg font-extrabold text-white tabular-nums">{s.score}</div>
                          <div className="text-xs text-emerald-100/60">{(s.probability * 100).toFixed(1)}%</div>
                        </motion.div>
                      ))}
                    </div>
                  </div>

                  <div className="card-glass p-6 space-y-4">
                    <h3 className="font-bold text-white flex items-center gap-2">
                      <Flag size={18} className="text-primary-400" /> Goals & totals
                    </h3>
                    <ProbBar label="Over 2.5 goals" value={probs.totals['over_2.5']} color="bg-emerald-500" />
                    <ProbBar label="Under 2.5 goals" value={probs.totals['under_2.5']} color="bg-teal-600" />
                    <ProbBar label="Both teams to score" value={probs.btts_yes} color="bg-emerald-400" />
                    <div className="grid grid-cols-3 gap-2 pt-2">
                      <StatChip label="Corners" value={prediction.secondary_markets.corners.total_avg} />
                      <StatChip label="Fouls" value={prediction.secondary_markets.fouls.total_avg} />
                      <StatChip label="Yellows" value={prediction.secondary_markets.cards.total_yellows_avg} />
                    </div>
                  </div>
                </div>

                {/* Value bets */}
                {prediction.value_analysis && (
                  <div className="card-glass p-6">
                    <h3 className="font-bold text-white mb-4 flex items-center gap-2">
                      <TrendingUp size={18} className="text-primary-400" /> Value analysis
                    </h3>
                    {prediction.value_analysis.value_bets?.length ? (
                      <div className="space-y-3">
                        {prediction.value_analysis.value_bets.map((b: any) => (
                          <div key={b.market} className="flex flex-wrap items-center justify-between gap-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 p-4">
                            <div>
                              <div className="font-bold text-emerald-300">{b.market} @ {b.bookmaker_odds}</div>
                              <div className="text-sm text-emerald-100/60">
                                Model {(b.model_probability * 100).toFixed(1)}% vs market {(b.market_fair_probability * 100).toFixed(1)}%
                              </div>
                            </div>
                            <div className="text-right">
                              <div className="text-lg font-extrabold text-emerald-300">+{b.expected_value_pct}% EV</div>
                              <div className="text-xs text-emerald-100/50">¼-Kelly stake: {(b.kelly_fraction * 100).toFixed(1)}% of bankroll</div>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-emerald-100/60 text-sm">{prediction.value_analysis.note}</p>
                    )}
                  </div>
                )}

                {/* Reasons + warnings */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="card-glass p-6">
                    <h3 className="font-bold text-white mb-3 flex items-center gap-2">
                      <ShieldCheck size={18} className="text-primary-400" /> Key reasons
                    </h3>
                    <ul className="space-y-2 text-sm text-emerald-100/80">
                      {prediction.key_reasons.map((r: string, i: number) => (
                        <li key={i} className="flex gap-2"><span className="text-emerald-400">•</span>{r}</li>
                      ))}
                    </ul>
                    {prediction.form && (
                      <div className="mt-4 flex gap-4 text-xs text-emerald-100/60">
                        <span>Home form: <b className="text-white">{prediction.form.home.form_string || '—'}</b></span>
                        <span>Away form: <b className="text-white">{prediction.form.away.form_string || '—'}</b></span>
                      </div>
                    )}
                  </div>

                  <div className="card-glass p-6">
                    <h3 className="font-bold text-white mb-3 flex items-center gap-2">
                      <AlertTriangle size={18} className="text-amber-400" /> Warnings
                    </h3>
                    <ul className="space-y-2 text-sm text-amber-200/70">
                      {prediction.warnings.map((w: string, i: number) => (
                        <li key={i} className="flex gap-2"><span>⚠</span>{w}</li>
                      ))}
                    </ul>
                    <p className="mt-4 text-xs text-emerald-100/40 italic">{prediction.disclaimer}</p>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  )
}

export default PredictionsPage
