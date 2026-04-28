import type { ConfiguratorRequest, ConfiguratorResponse } from "../types";
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
