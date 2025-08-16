import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Box, Button, Typography } from '@mui/material';

const TestNavigation = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const testRoutes = [
    { path: '/', label: 'Home' },
    { path: '/predictions', label: 'Predictions' },
    { path: '/live-data', label: 'Live Data' },
    { path: '/performance', label: 'Performance' },
    { path: '/history', label: 'History' },
    { path: '/sportsradar', label: 'SportRadar' }
  ];

  const handleNavigation = (path) => {
    console.log('Navigating to:', path);
    navigate(path);
  };

  return (
    <Box sx={{ 
      position: 'fixed', 
      top: 10, 
      right: 10, 
      background: 'rgba(0,0,0,0.8)', 
      p: 2, 
      borderRadius: 2,
      zIndex: 10000
    }}>
      <Typography variant="h6" sx={{ color: 'white', mb: 1 }}>
        Navigation Test
      </Typography>
      <Typography variant="body2" sx={{ color: 'white', mb: 2 }}>
        Current: {location.pathname}
      </Typography>
      {testRoutes.map((route) => (
        <Button
          key={route.path}
          variant={location.pathname === route.path ? 'contained' : 'outlined'}
          size="small"
          onClick={() => handleNavigation(route.path)}
          sx={{ 
            display: 'block', 
            mb: 1, 
            width: '100%',
            color: 'white',
            borderColor: 'white'
          }}
        >
          {route.label}
        </Button>
      ))}
    </Box>
  );
};

export default TestNavigation;
