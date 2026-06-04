import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { ThemeProvider } from './context/ThemeContext'
import Home from './pages/Home'
import PromptInjection from './pages/PromptInjection'
import RagPoisoning from './pages/RagPoisoning'

export default function App() {
  return (
    <ThemeProvider>
      <div className="relative min-h-screen flex flex-col overflow-hidden bg-bg text-primary select-none">
        {/* Responsive dot background */}
        <div className="dot-grid" />
        
        {/* Router routing container */}
        <Router>
          <div className="relative flex flex-col h-screen z-10">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/prompt-injection" element={<PromptInjection />} />
              <Route path="/rag-poisoning" element={<RagPoisoning />} />
            </Routes>
          </div>
        </Router>
      </div>
    </ThemeProvider>
  )
}
