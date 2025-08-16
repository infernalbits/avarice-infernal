import React from 'react';
import { Box } from '@mui/material';

const BackgroundEffects = () => {
  return (
    <Box
      sx={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
        zIndex: -2,
        overflow: 'hidden'
      }}
    >
      {/* Main gradient background */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          background: 'linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 50%, #16213e 100%)',
        }}
      />

      {/* Animated gradient orbs */}
      <Box
        sx={{
          position: 'absolute',
          top: '10%',
          left: '10%',
          width: '300px',
          height: '300px',
          background: 'radial-gradient(circle, rgba(0, 212, 255, 0.3) 0%, transparent 70%)',
          borderRadius: '50%',
          animation: 'float 6s ease-in-out infinite',
          filter: 'blur(40px)',
        }}
      />

      <Box
        sx={{
          position: 'absolute',
          top: '60%',
          right: '15%',
          width: '250px',
          height: '250px',
          background: 'radial-gradient(circle, rgba(138, 43, 226, 0.3) 0%, transparent 70%)',
          borderRadius: '50%',
          animation: 'float 8s ease-in-out infinite reverse',
          filter: 'blur(40px)',
        }}
      />

      <Box
        sx={{
          position: 'absolute',
          bottom: '20%',
          left: '20%',
          width: '200px',
          height: '200px',
          background: 'radial-gradient(circle, rgba(57, 255, 20, 0.2) 0%, transparent 70%)',
          borderRadius: '50%',
          animation: 'float 7s ease-in-out infinite',
          filter: 'blur(30px)',
        }}
      />

      {/* Geometric shapes */}
      <Box
        sx={{
          position: 'absolute',
          top: '30%',
          right: '25%',
          width: '100px',
          height: '100px',
          background: 'linear-gradient(45deg, rgba(255, 7, 58, 0.2), transparent)',
          transform: 'rotate(45deg)',
          animation: 'rotate360 15s linear infinite',
          filter: 'blur(20px)',
        }}
      />

      <Box
        sx={{
          position: 'absolute',
          bottom: '40%',
          right: '10%',
          width: '80px',
          height: '80px',
          background: 'linear-gradient(45deg, rgba(255, 102, 0, 0.3), transparent)',
          borderRadius: '20px',
          animation: 'float 5s ease-in-out infinite',
          filter: 'blur(15px)',
        }}
      />

      {/* Cyber grid overlay */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          backgroundImage: `
            linear-gradient(rgba(0, 212, 255, 0.1) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 212, 255, 0.1) 1px, transparent 1px)
          `,
          backgroundSize: '100px 100px',
          opacity: 0.3,
          animation: 'matrix 30s linear infinite',
        }}
      />

      {/* Particles effect */}
      {[...Array(20)].map((_, index) => (
        <Box
          key={index}
          sx={{
            position: 'absolute',
            width: '4px',
            height: '4px',
            background: '#00d4ff',
            borderRadius: '50%',
            top: `${Math.random() * 100}%`,
            left: `${Math.random() * 100}%`,
            animation: `twinkle ${2 + Math.random() * 3}s ease-in-out infinite`,
            animationDelay: `${Math.random() * 2}s`,
            boxShadow: '0 0 10px #00d4ff',
          }}
        />
      ))}

      {/* Scanning lines effect */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '2px',
          background: 'linear-gradient(90deg, transparent, #00d4ff, transparent)',
          animation: 'scanLine 4s ease-in-out infinite',
          opacity: 0.8,
        }}
      />

      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '2px',
          height: '100%',
          background: 'linear-gradient(0deg, transparent, #8a2be2, transparent)',
          animation: 'scanLineVertical 6s ease-in-out infinite',
          opacity: 0.6,
        }}
      />

      {/* CSS for additional animations */}
      <style jsx>{`
        @keyframes twinkle {
          0%, 100% { opacity: 0; transform: scale(0); }
          50% { opacity: 1; transform: scale(1); }
        }

        @keyframes scanLine {
          0% { top: 0%; opacity: 1; }
          100% { top: 100%; opacity: 0; }
        }

        @keyframes scanLineVertical {
          0% { left: 0%; opacity: 1; }
          100% { left: 100%; opacity: 0; }
        }
      `}</style>
    </Box>
  );
};

export default BackgroundEffects;
