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
