import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, AppBar, Toolbar, Typography, Container } from '@mui/material';
import Dashboard from './components/Dashboard';
import FlashyDashboard from './components/FlashyDashboard';
import Predictions from './components/Predictions';
import LiveData from './components/LiveData';
import SportRadarData from './components/SportRadarData';
import Performance from './components/Performance';
import BettingHistory from './components/BettingHistory';
import FlashyNavigation from './components/FlashyNavigation';
import BackgroundEffects from './components/BackgroundEffects';
import TestNavigation from './components/TestNavigation';
import EnhancedMLDashboard from './components/EnhancedMLDashboard';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#00d4ff',
    },
    secondary: {
      main: '#8a2be2',
    },
    success: {
      main: '#39ff14',
    },
    warning: {
      main: '#ffff00',
    },
    error: {
      main: '#ff073a',
    },
    background: {
      default: 'transparent',
      paper: 'rgba(255, 255, 255, 0.1)',
    },
    text: {
      primary: '#ffffff',
      secondary: 'rgba(255, 255, 255, 0.7)',
    },
  },
  typography: {
    fontFamily: 'Inter, Arial, sans-serif',
    h1: {
      fontFamily: 'Orbitron, monospace',
      fontWeight: 900,
    },
    h2: {
      fontFamily: 'Orbitron, monospace',
      fontWeight: 800,
    },
    h3: {
      fontFamily: 'Orbitron, monospace',
      fontWeight: 700,
    },
    h4: {
      fontFamily: 'Orbitron, monospace',
      fontWeight: 700,
    },
    h5: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 600,
    },
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          background: 'linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 50%, #16213e 100%)',
          minHeight: '100vh',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          background: 'rgba(255, 255, 255, 0.1)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          borderRadius: 16,
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 25,
          textTransform: 'none',
          fontWeight: 700,
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          backdropFilter: 'blur(10px)',
          fontWeight: 600,
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <div className="App">
          <BackgroundEffects />
          <AppBar 
            position="static" 
            elevation={0}
            sx={{
              background: 'var(--bg-glass)',
              backdropFilter: 'blur(20px)',
              borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
            }}
          >
            <Toolbar sx={{ justifyContent: 'center' }}>
              <Typography 
                variant="h4" 
                component="div" 
                sx={{ 
                  fontFamily: 'Orbitron, monospace',
                  fontWeight: 900,
                  background: 'var(--primary-gradient)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  textShadow: '0 0 30px rgba(102, 126, 234, 0.5)',
                  animation: 'neonText 3s ease-in-out infinite alternate',
                  textAlign: 'center'
                }}
              >
                ⚡ SPORTS BETTING AI ⚡
              </Typography>
            </Toolbar>
          </AppBar>
          
          <FlashyNavigation />
          <TestNavigation />
          
          <Container maxWidth="xl" sx={{ mt: 3, mb: 3 }}>
            <Routes>
              <Route path="/" element={<FlashyDashboard />} />
              <Route path="/classic" element={<Dashboard />} />
              <Route path="/predictions" element={<Predictions />} />
              <Route path="/live-data" element={<LiveData />} />
              <Route path="/sportsradar" element={<SportRadarData />} />
              <Route path="/realtime" element={<FlashyDashboard />} />
              <Route path="/performance" element={<Performance />} />
              <Route path="/history" element={<BettingHistory />} />
              <Route path="/enhanced-ml" element={<EnhancedMLDashboard />} />
            </Routes>
          </Container>
        </div>
      </Router>
    </ThemeProvider>
  );
}

export default App;
