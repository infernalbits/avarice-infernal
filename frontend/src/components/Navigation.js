import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
  Tabs, 
  Tab, 
  Box, 
  Container 
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  TrendingUp as TrendingUpIcon,
  Assessment as AssessmentIcon,
  History as HistoryIcon,
  Speed as SpeedIcon
} from '@mui/icons-material';

const Navigation = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const tabs = [
    { label: 'Dashboard', value: '/', icon: <DashboardIcon /> },
    { label: 'Predictions', value: '/predictions', icon: <TrendingUpIcon /> },
    { label: 'Live Data', value: '/live-data', icon: <SpeedIcon /> },
    { label: 'SportRadar', value: '/sportsradar', icon: <AssessmentIcon /> },
    { label: 'Performance', value: '/performance', icon: <AssessmentIcon /> },
    { label: 'History', value: '/history', icon: <HistoryIcon /> },
  ];

  const handleChange = (event, newValue) => {
    navigate(newValue);
  };

  return (
    <Box sx={{ borderBottom: 1, borderColor: 'divider', backgroundColor: 'white' }}>
      <Container maxWidth="xl">
        <Tabs 
          value={location.pathname} 
          onChange={handleChange}
          aria-label="navigation tabs"
        >
          {tabs.map((tab) => (
            <Tab
              key={tab.value}
              label={tab.label}
              value={tab.value}
              icon={tab.icon}
              iconPosition="start"
            />
          ))}
        </Tabs>
      </Container>
    </Box>
  );
};

export default Navigation;
