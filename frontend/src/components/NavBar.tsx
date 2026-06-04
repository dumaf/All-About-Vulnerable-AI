import { useNavigate } from 'react-router-dom'
import { ChevronLeft, Shield, Sun, Moon } from 'lucide-react'
import { useTheme } from '../context/ThemeContext'

interface NavBarProps {
  title:     string
  subtitle?: string
}

export default function NavBar({ title, subtitle }: NavBarProps) {
  const navigate = useNavigate()
  const { theme, toggle } = useTheme()

  return (
    <header className="flex items-center gap-4 px-6 py-4 glass border-b border-white/[0.08] z-10">
      <button
        id="nav-back-btn"
        onClick={() => navigate('/')}
        className="flex items-center gap-1 text-sub hover:text-cyan transition-colors text-sm"
      >
        <ChevronLeft size={16} />
        Home
      </button>

      <div className="w-px h-5 bg-white/10" />

      <div className="flex items-center gap-2">
        <Shield size={16} className="text-green" />
        <span className="font-mono text-sm font-semibold text-primary">{title}</span>
        {subtitle && <span className="text-xs text-muted font-mono">/ {subtitle}</span>}
      </div>

      <div className="ml-auto flex items-center gap-3">
        <span className="text-xs text-muted font-mono">AAVAI</span>
        <div className="w-1.5 h-1.5 bg-green animate-pulse-slow" />
        <button
          id="nav-theme-toggle"
          onClick={toggle}
          className="text-muted hover:text-primary transition-colors"
          title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
        >
          {theme === 'dark' ? <Sun size={15} /> : <Moon size={15} />}
        </button>
      </div>
    </header>
  )
}
