import { z } from 'zod';

/** === Agent Message Discriminated Union Types === **/

// Chat-only message
export const ChatMessageSchema = z.object({
  type: z.literal("chat"),
  role: z.enum(["user", "assistant"]),
  content: z.string(),
});

// Design message from DesignAgent
export const DesignMessageSchema = z.object({
  type: z.literal("design"),
  role: z.literal("assistant"),
  imageUrl: z.string(),
  message: z.string(),
  status: z.enum(["refining", "approved"]),
  originalPrompt: z.string(),
  currentPrompt: z.string(),
});

// All current message types
export const AgentMessageSchema = z.discriminatedUnion("type", [
  ChatMessageSchema,
  DesignMessageSchema,
]);

export type AgentMessage = z.infer<typeof AgentMessageSchema>;

/** === Agent Response with Messages + Context === **/
export const AgentResponseSchema = z.object({
  sessionId: z.string(),
  messages: z.array(AgentMessageSchema),
  context: z.record(z.any()).optional(),
});

export type AgentResponse = z.infer<typeof AgentResponseSchema>;

/** === Context Shape === **/
export const ChatContextSchema = z.object({
  last_prompt: z.string().optional(),
  design: z
    .object({
      image_url: z.string(),
      status: z.enum(["refining", "approved"]),
      original_prompt: z.string(),
      current_prompt: z.string(),
    })
    .optional(),
  blueprint_id: z.number().optional(),
  selected_variant_ids: z.array(z.number()).optional(),
});

export type ChatContext = z.infer<typeof ChatContextSchema>;

/** === Agent Request Payload === **/
export const AgentRequestSchema = z.object({
  input: z.string(),
  sessionId: z.string(),
  context: ChatContextSchema.optional(),
});

export type AgentRequest = z.infer<typeof AgentRequestSchema>;
