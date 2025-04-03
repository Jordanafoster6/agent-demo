import React from 'react';
import { AgentMessage } from "@shared/types";
import { Typography, Card, CardMedia, CardContent } from '@mui/material';

interface ChatWindowProps {
  messages: AgentMessage[];
}

export const ChatWindow = (props: ChatWindowProps) => {
  return (
    <div>
      {props.messages.map((msg, idx) => {
        if (msg.type === "design") {
          return (
            <div key={idx}>
              <p>{msg.message}</p>
              <img src={msg.imageUrl} alt="Design preview" style={{ maxWidth: '100%' }} />
            </div>
          );
        }

        // Default chat rendering
        return (
          <div key={idx}>
            <strong>{msg.role}:</strong> {msg.content}
          </div>
        );
      })}
    </div>
  );
};


        // <Card sx={{ maxWidth: 400, my: 2, borderRadius: 4, boxShadow: 3 }}>
        //   <CardMedia
        //     component="img"
        //     image={output}
        //     alt="Generated design"
        //     sx={{ borderRadius: 2 }}
        //   />
        // </Card>

        // <Card sx={{ my: 2, p: 2, borderRadius: 4, boxShadow: 2 }}>
        //   <CardContent>
        //     <Typography variant="body1">{output}</Typography>
        //   </CardContent>
        // </Card>