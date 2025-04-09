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
        if (msg.type === "chat") {
          return (
            <Typography key={idx}>
              <strong>{msg.role}:</strong> {msg.content}
            </Typography>
          );
        } else if (msg.type === "design") {
          return (
            <div key={idx}>
              <Typography>{msg.message}</Typography>
              <img src={msg.imageUrl} alt="Design preview" style={{ maxWidth: '100%' }} />
            </div>
          );
        } else if (msg.type === "printify") {
          return (
            <Typography key={idx}>
              {msg.message}
              {msg.blueprints && (
                <ul>
                  {msg.blueprints.map((bp, i) => (
                    <li key={i}>{bp}</li>
                  ))}
                </ul>
              )}
              {msg.printProviders && (
                <ul>
                  {msg.printProviders.map((pp, i) => (
                    <li key={i}>{pp}</li>
                  ))}
                </ul>
              )}
              {msg.variants && (
                <ul>
                  {msg.variants.map((v, i) => (
                    <li key={i}>{v}</li>
                  ))}
                </ul>
              )}
            </Typography>
          );
        }
        return null; // Fallback for unhandled types
      })}
    </div>
  );
};
