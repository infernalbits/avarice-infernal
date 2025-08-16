import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
  Tabs, 
  Tab, 
  Box, 
  Container,
  Paper,
  Avatar,
  Chip,
  Badge,
  Tooltip
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  TrendingUp as TrendingUpIcon,
  Assessment as AssessmentIcon,
  History as HistoryIcon,
  Speed as SpeedIcon,
  AutoGraph,
  Bolt,
  Diamond,
  Rocket
} from '@mui/icons-material';

const FlashyNavigation = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [hoveredTab, setHoveredTab] = useState(null);

  const tabs = [
    { 
      label: 'Dashboard', 
      value: '/', 
      icon: <DashboardIcon />, 
      color: '#00d4ff',
      emoji: '⚡',
      description: 'Real-time overview'
    },
    { 
      label: 'Enhanced AI', 
      value: '/enhanced-ml', 
      icon: <AutoGraph />, 
      color: '#8a2be2',
      emoji: '🤖',
      description: 'Advanced ML Engine'
    },
    { 
      label: 'Predictions', 
      value: '/predictions', 
      icon: <TrendingUpIcon />, 
      color: '#39ff14',
      emoji: '🚀',
      description: 'AI-powered bets'
    },
    { 
      label: 'Live Data', 
      value: '/live-data', 
      icon: <SpeedIcon />, 
      color: '#ff073a',
      emoji: '🔥',
      description: 'Market intelligence'
    },
    { 
      label: 'SportRadar', 
      value: '/sportsradar', 
      icon: <AssessmentIcon />, 
      color: '#8a2be2',
      emoji: '📊',
      description: 'Data analysis'
    },
    { 
      label: 'Performance', 
      value: '/performance', 
      icon: <AutoGraph />, 
      color: '#ff6600',
      emoji: '📈',
      description: 'Analytics & ROI'
    },
    { 
      label: 'History', 
      value: '/history', 
      icon: <HistoryIcon />, 
      color: '#ffff00',
      emoji: '📜',
      description: 'Bet tracking'
    },
  ];

  const handleChange = (event, newValue) => {
    console.log('Navigation tab clicked:', newValue);
    navigate(newValue);
  };

  const TabComponent = ({ tab, isSelected }) => (
    <Tab
      key={tab.value}
      value={tab.value}
      onClick={() => {
        console.log('Tab clicked directly:', tab.value);
        navigate(tab.value);
      }}
      label={
        <Box 
          display="flex" 
          alignItems="center" 
          gap={{ xs: 0.5, md: 1 }}
          flexDirection={{ xs: 'column', sm: 'row' }}
        >
          <Avatar
            sx={{
              width: { xs: 20, md: 24 },
              height: { xs: 20, md: 24 },
              background: isSelected ? tab.color : 'rgba(255, 255, 255, 0.1)',
              color: isSelected ? '#000' : '#fff',
              fontSize: { xs: '0.7rem', md: '0.8rem' },
              transition: 'all 0.3s ease',
              boxShadow: isSelected ? `0 0 15px ${tab.color}60` : 'none',
              animation: isSelected ? 'pulse 2s ease-in-out infinite' : 'none'
            }}
          >
            {tab.emoji}
          </Avatar>
          <Box textAlign={{ xs: 'center', sm: 'left' }}>
            <Box 
              className="readable-text"
              sx={{ 
                fontWeight: isSelected ? 800 : 600,
                color: isSelected ? tab.color : 'rgba(255, 255, 255, 0.8)',
                textShadow: isSelected ? `0 0 10px ${tab.color}` : '0 1px 2px rgba(0, 0, 0, 0.5)',
                transition: 'all 0.3s ease',
                fontSize: { xs: '0.7rem', sm: '0.8rem', md: '0.875rem' },
                lineHeight: 1.2
              }}
            >
              {tab.label}
            </Box>
            {hoveredTab === tab.value && (
              <Box 
                className="readable-text"
                sx={{ 
                  fontSize: { xs: '0.6rem', md: '0.7rem' },
                  color: 'rgba(255, 255, 255, 0.6)',
                  textAlign: 'center',
                  textShadow: '0 1px 2px rgba(0, 0, 0, 0.5)',
                  display: { xs: 'none', md: 'block' }
                }}
              >
                {tab.description}
              </Box>
            )}
          </Box>
        </Box>
      }
      onMouseEnter={() => setHoveredTab(tab.value)}
      onMouseLeave={() => setHoveredTab(null)}
      sx={{
        minHeight: { xs: 48, md: 72 },
        borderRadius: 2,
        margin: '0 2px',
        padding: { xs: '6px 8px', md: '8px 12px' },
        transition: 'all 0.3s ease',
        border: isSelected ? `2px solid ${tab.color}` : '2px solid transparent',
        background: isSelected 
          ? `linear-gradient(135deg, ${tab.color}20, transparent)` 
          : 'transparent',
        minWidth: { xs: 60, md: 120 },
        '&:hover': {
          background: `linear-gradient(135deg, ${tab.color}30, transparent)`,
          transform: { xs: 'scale(1.05)', md: 'translateY(-2px)' },
          boxShadow: `0 8px 25px ${tab.color}40`,
        }
      }}
    />
  );

  return (
    <Paper
      elevation={0}
      sx={{
        background: 'var(--bg-glass)',
        backdropFilter: 'blur(20px)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
        position: 'relative',
        overflow: 'hidden'
      }}
    >
      {/* Animated Background */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: `
            radial-gradient(circle at 20% 50%, rgba(0, 212, 255, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 50%, rgba(138, 43, 226, 0.1) 0%, transparent 50%)
          `,
          animation: 'floatingOrbs 15s ease-in-out infinite',
          pointerEvents: 'none'
        }}
      />
      
      <Container maxWidth="xl" sx={{ position: 'relative', zIndex: 2 }}>
        <Box 
          display="flex" 
          justifyContent="space-between" 
          alignItems="center" 
          py={{ xs: 0.5, md: 1 }}
          flexDirection={{ xs: 'column', lg: 'row' }}
          gap={{ xs: 1, lg: 0 }}
        >
          {/* Logo/Brand */}
          <Box 
            display="flex" 
            alignItems="center" 
            gap={{ xs: 1, md: 2 }}
            order={{ xs: 1, lg: 1 }}
          >
            <Avatar
              sx={{
                width: { xs: 36, md: 48 },
                height: { xs: 36, md: 48 },
                background: 'var(--primary-gradient)',
                boxShadow: 'var(--shadow-neon)',
                animation: 'glow 2s ease-in-out infinite alternate'
              }}
            >
              <Diamond sx={{ fontSize: { xs: '1rem', md: '1.5rem' } }} />
            </Avatar>
            <Box display={{ xs: 'none', sm: 'block' }}>
              <Box 
                className="readable-text-strong"
                sx={{ 
                  fontFamily: 'Orbitron, monospace',
                  fontWeight: 900,
                  fontSize: { xs: '1rem', md: '1.2rem' },
                  background: 'var(--primary-gradient)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  textShadow: '0 0 20px rgba(102, 126, 234, 0.5)'
                }}
              >
                Sports AI
              </Box>
              <Box 
                className="readable-text"
                sx={{ 
                  fontSize: { xs: '0.6rem', md: '0.7rem' },
                  color: 'rgba(255, 255, 255, 0.7)',
                  fontWeight: 600,
                  textShadow: '0 1px 2px rgba(0, 0, 0, 0.5)'
                }}
              >
                Betting Intelligence
              </Box>
            </Box>
          </Box>

          {/* Navigation Tabs */}
          <Box 
            order={{ xs: 2, lg: 2 }}
            width={{ xs: '100%', lg: 'auto' }}
            display="flex"
            justifyContent="center"
          >
            <Tabs 
              value={location.pathname} 
              onChange={handleChange}
              aria-label="navigation tabs"
              variant={{ xs: 'scrollable', md: 'standard' }}
              scrollButtons={{ xs: 'auto', md: false }}
              allowScrollButtonsMobile
              sx={{
                '& .MuiTabs-indicator': {
                  display: 'none' // We'll use custom styling
                },
                '& .MuiTabs-scrollButtons': {
                  color: 'rgba(255, 255, 255, 0.7)',
                  '&.Mui-disabled': {
                    opacity: 0.3
                  }
                },
                minHeight: { xs: 48, md: 72 },
                maxWidth: { xs: '100%', lg: 'none' }
              }}
            >
              {tabs.map((tab) => (
                <TabComponent 
                  key={tab.value}
                  tab={tab}
                  isSelected={location.pathname === tab.value}
                />
              ))}
            </Tabs>
          </Box>

          {/* Status Indicators */}
          <Box 
            display="flex" 
            alignItems="center" 
            gap={{ xs: 1, md: 2 }}
            order={{ xs: 3, lg: 3 }}
            justifyContent={{ xs: 'center', lg: 'flex-end' }}
          >
            <Tooltip title="System Status">
              <Chip
                icon={<Bolt sx={{ fontSize: { xs: '0.8rem', md: '1rem' } }} />}
                label="LIVE"
                size="small"
                sx={{
                  background: 'var(--success-gradient)',
                  color: '#000',
                  fontWeight: 800,
                  fontSize: { xs: '0.7rem', md: '0.75rem' },
                  height: { xs: 24, md: 32 },
                  animation: 'pulse 1.5s ease-in-out infinite',
                  display: { xs: 'none', sm: 'flex' }
                }}
              />
            </Tooltip>
            
            <Tooltip title="Active Predictions">
              <Badge 
                badgeContent={5} 
                color="error"
                sx={{
                  '& .MuiBadge-badge': {
                    fontSize: { xs: '0.6rem', md: '0.75rem' },
                    minWidth: { xs: 16, md: 20 },
                    height: { xs: 16, md: 20 }
                  }
                }}
              >
                <Avatar
                  sx={{
                    width: { xs: 28, md: 32 },
                    height: { xs: 28, md: 32 },
                    background: 'var(--danger-gradient)',
                    animation: 'glow 2s ease-in-out infinite alternate'
                  }}
                >
                  <Rocket sx={{ fontSize: { xs: 14, md: 18 } }} />
                </Avatar>
              </Badge>
            </Tooltip>

            <Tooltip title="Market Status">
              <Avatar
                sx={{
                  width: { xs: 28, md: 32 },
                  height: { xs: 28, md: 32 },
                  background: 'var(--warning-gradient)',
                  color: '#000',
                  fontWeight: 800,
                  fontSize: { xs: '0.8rem', md: '1rem' }
                }}
              >
                🔥
              </Avatar>
            </Tooltip>
          </Box>
        </Box>
      </Container>

      {/* Bottom gradient line */}
      <Box
        sx={{
          height: 2,
          background: 'var(--primary-gradient)',
          animation: 'shimmer 3s ease-in-out infinite'
        }}
      />
    </Paper>
  );
};

export default FlashyNavigation;
