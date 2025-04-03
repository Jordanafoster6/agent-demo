import React from 'react';
import { Container, Typography } from '@mui/material';
import AgentForm from './components/AgentForm';

function App() {
  return (
    <Container maxWidth="sm">
      <Typography variant="h4" gutterBottom>
        AI Agent Interface
      </Typography>
      <AgentForm />
    </Container>
  );
}

export default App;
