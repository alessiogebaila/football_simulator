import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  Trophy, 
  Users, 
  Zap, 
  BarChart3, 
  Gamepad2,
  TrendingUp,
  Award,
  Activity
} from 'lucide-react';
import footballApi from '../services/api';
import { GlobalStats } from '../types';
import toast from 'react-hot-toast';

const HomePage: React.FC = () => {
  const [stats, setStats] = useState<GlobalStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await footballApi.getGlobalStats();
        setStats(data);
      } catch (error) {
        console.error('Error fetching stats:', error);
        toast.error('Failed to load statistics');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  const features = [
    {
      icon: <Users className="h-8 w-8" />,
      title: "Real Team Data",
      description: "Explore squads from top European clubs with real Transfermarkt data",
      link: "/teams",
      color: "from-blue-500 to-blue-600"
    },
    {
      icon: <Zap className="h-8 w-8" />,
      title: "AI Match Simulation",
      description: "Advanced Bayesian & ML algorithms predict realistic match outcomes",
      link: "/simulator",
      color: "from-yellow-500 to-orange-500"
    },
    {
      icon: <Gamepad2 className="h-8 w-8" />,
      title: "Tournament Mode",
      description: "Create custom tournaments and watch teams compete",
      link: "/tournament",
      color: "from-purple-500 to-purple-600"
    },
    {
      icon: <BarChart3 className="h-8 w-8" />,
      title: "Advanced Analytics",
      description: "Deep insights into team performance and player statistics",
      link: "/stats",
      color: "from-green-500 to-green-600"
    }
  ];

  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Hero Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <div className="flex justify-center mb-6">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
              className="p-4 bg-white/20 rounded-full backdrop-blur-sm"
            >
              <Trophy className="h-16 w-16 text-white" />
            </motion.div>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold text-white mb-6">
            Ultimate Football
            <span className="block bg-gradient-to-r from-yellow-400 to-orange-500 bg-clip-text text-transparent">
              Simulator
            </span>
          </h1>
          
          <p className="text-xl md:text-2xl text-green-100 mb-8 max-w-3xl mx-auto">
            Experience the future of football simulation with AI-powered predictions, 
            real player data, and advanced statistical modeling.
          </p>

          <motion.div
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Link
              to="/simulator"
              className="inline-flex items-center px-8 py-4 text-lg font-semibold text-white bg-gradient-to-r from-yellow-500 to-orange-500 rounded-full shadow-lg hover:shadow-xl transition-all duration-300 btn-glow"
            >
              <Zap className="mr-3 h-6 w-6" />
              Start Simulating
            </Link>
          </motion.div>
        </motion.div>

        {/* Stats Overview */}
        {stats && !loading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-16"
          >
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 text-center">
              <Users className="h-8 w-8 text-blue-400 mx-auto mb-2" />
              <div className="text-3xl font-bold text-white">{stats.total_teams}</div>
              <div className="text-green-200">Teams</div>
            </div>
            
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 text-center">
              <Activity className="h-8 w-8 text-green-400 mx-auto mb-2" />
              <div className="text-3xl font-bold text-white">{stats.total_players}</div>
              <div className="text-green-200">Players</div>
            </div>
            
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 text-center">
              <TrendingUp className="h-8 w-8 text-yellow-400 mx-auto mb-2" />
              <div className="text-3xl font-bold text-white">
                €{Math.round(stats.total_market_value / 1_000_000)}M
              </div>
              <div className="text-green-200">Total Value</div>
            </div>
            
            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 text-center">
              <Award className="h-8 w-8 text-purple-400 mx-auto mb-2" />
              <div className="text-2xl font-bold text-white">
                {stats.top_valued_players?.[0]?.name || 'N/A'}
              </div>
              <div className="text-green-200">Top Player</div>
            </div>
          </motion.div>
        )}

        {/* Features Grid */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="grid md:grid-cols-2 gap-8 mb-16"
        >
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 * index }}
              whileHover={{ scale: 1.02, y: -5 }}
              className="card-hover"
            >
              <Link to={feature.link}>
                <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-8 h-full hover:bg-white/15 transition-all duration-300">
                  <div className={`inline-flex p-3 rounded-xl bg-gradient-to-r ${feature.color} mb-6`}>
                    {feature.icon}
                  </div>
                  
                  <h3 className="text-2xl font-bold text-white mb-4">
                    {feature.title}
                  </h3>
                  
                  <p className="text-green-100 text-lg leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              </Link>
            </motion.div>
          ))}
        </motion.div>

        {/* Technology Stack */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          className="bg-white/5 backdrop-blur-sm rounded-2xl p-8 text-center"
        >
          <h2 className="text-3xl font-bold text-white mb-6">
            Powered by Advanced AI
          </h2>
          
          <div className="grid md:grid-cols-3 gap-6">
            <div className="p-4">
              <div className="text-lg font-semibold text-white mb-2">
                🧠 Bayesian Learning
              </div>
              <p className="text-green-200">
                PyMC-powered probabilistic modeling for realistic predictions
              </p>
            </div>
            
            <div className="p-4">
              <div className="text-lg font-semibold text-white mb-2">
                🤖 Machine Learning
              </div>
              <p className="text-green-200">
                Scikit-learn algorithms analyze team performance patterns
              </p>
            </div>
            
            <div className="p-4">
              <div className="text-lg font-semibold text-white mb-2">
                📊 Real Data
              </div>
              <p className="text-green-200">
                Live Transfermarkt data for authentic player statistics
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default HomePage;
