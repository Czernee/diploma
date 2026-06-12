import type {
  ConfiguratorAssistantRequest,
  ConfiguratorAssistantResponse,
  ConfiguratorRequest,
  ConfiguratorResponse
} from "../types";
import { apiRequest } from "./http";

export function recommendConfiguration(
  token: string,
  payload: ConfiguratorRequest
): Promise<ConfiguratorResponse> {
  return apiRequest<ConfiguratorResponse>("/api/configurator/recommend", {
    method: "POST",
    token,
    body: payload
  });
}

export function askConfiguratorAssistant(
  token: string,
  payload: ConfiguratorAssistantRequest
): Promise<ConfiguratorAssistantResponse> {
  return apiRequest<ConfiguratorAssistantResponse>("/api/configurator/assistant", {
    method: "POST",
    token,
    body: payload
  });
}
