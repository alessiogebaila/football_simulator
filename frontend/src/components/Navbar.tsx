import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  Trophy,
  Users,
  Zap,
  BarChart3,
  Settings,
  Menu,
  X,
  Gamepad2,
  BrainCircuit
} from 'lucide-react';

interface NavItem {
  name: string;
  path: string;
  icon: React.ReactNode;
}

const Navbar: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();

  const navItems: NavItem[] = [
    { name: 'Home', path: '/', icon: <Trophy size={20} /> },
    { name: 'Teams', path: '/teams', icon: <Users size={20} /> },
    { name: 'Simulator', path: '/simulator', icon: <Zap size={20} /> },
    { name: 'Predictions', path: '/predictions', icon: <BrainCircuit size={20} /> },
    { name: 'Tournament', path: '/tournament', icon: <Gamepad2 size={20} /> },
    { name: 'Stats', path: '/stats', icon: <BarChart3 size={20} /> },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-[#04100a]/80 backdrop-blur-xl border-b border-emerald-800/40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <motion.div
              whileHover={{ rotate: 360 }}
              transition={{ duration: 0.5 }}
              className="p-2 bg-emerald-500/15 border border-emerald-500/30 rounded-xl"
            >
              <Trophy className="h-8 w-8 text-emerald-300" />
            </motion.div>
            <div className="hidden sm:block">
              <h1 className="text-xl font-bold text-white">
                Football Simulator
              </h1>
              <p className="text-xs text-green-100">Ultimate AI Edition</p>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:block">
            <div className="flex items-center space-x-1">
              {navItems.map((item) => (
                <Link key={item.path} to={item.path}>
                  <motion.div
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className={`
                      relative px-4 py-2 rounded-lg flex items-center space-x-2 transition-all duration-200
                      ${isActive(item.path)
                        ? 'bg-emerald-500/15 text-emerald-300 shadow-glow'
                        : 'text-emerald-100/70 hover:bg-emerald-500/10 hover:text-white'
                      }
                    `}
                  >
                    {item.icon}
                    <span className="font-medium">{item.name}</span>
                    
                    {isActive(item.path) && (
                      <motion.div
                        layoutId="activeTab"
                        className="absolute inset-0 bg-white/10 rounded-lg"
                        transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                      />
                    )}
                  </motion.div>
                </Link>
              ))}
            </div>
          </div>

          {/* Settings Button */}
          <motion.button
            whileHover={{ rotate: 90 }}
            transition={{ duration: 0.2 }}
            className="hidden md:block p-2 text-green-100 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
          >
            <Settings size={20} />
          </motion.button>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <motion.button
              whileTap={{ scale: 0.95 }}
              onClick={() => setIsOpen(!isOpen)}
              className="p-2 text-green-100 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
            >
              {isOpen ? <X size={24} /> : <Menu size={24} />}
            </motion.button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      <motion.div
        initial={false}
        animate={{ height: isOpen ? 'auto' : 0, opacity: isOpen ? 1 : 0 }}
        transition={{ duration: 0.3 }}
        className="md:hidden overflow-hidden bg-white/5 backdrop-blur-sm"
      >
        <div className="px-4 pt-2 pb-4 space-y-1">
          {navItems.map((item) => (
            <Link key={item.path} to={item.path} onClick={() => setIsOpen(false)}>
              <motion.div
                whileTap={{ scale: 0.95 }}
                className={`
                  flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200
                  ${isActive(item.path) 
                    ? 'bg-white/20 text-white' 
                    : 'text-green-100 hover:bg-white/10 hover:text-white'
                  }
                `}
              >
                {item.icon}
                <span className="font-medium">{item.name}</span>
              </motion.div>
            </Link>
          ))}
          
          <motion.div
            whileTap={{ scale: 0.95 }}
            className="flex items-center space-x-3 px-4 py-3 rounded-lg text-green-100 hover:bg-white/10 hover:text-white transition-colors cursor-pointer"
          >
            <Settings size={20} />
            <span className="font-medium">Settings</span>
          </motion.div>
        </div>
      </motion.div>
    </nav>
  );
};

export default Navbar;
