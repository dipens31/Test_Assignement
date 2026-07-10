import { api } from "./client";
import { API_ENDPOINTS } from "../constants";
import type {
  Member,
  MemberCreatePayload,
  MemberUpdatePayload,
  PaginatedResponse,
} from "../types";

export interface ListMembersParams {
  skip?: number;
  limit?: number;
  name?: string;
  email?: string;
}

export const membersApi = {
  list(params: ListMembersParams = {}): Promise<PaginatedResponse<Member>> {
    const q = new URLSearchParams();
    if (params.skip != null) q.set("skip", String(params.skip));
    if (params.limit != null) q.set("limit", String(params.limit));
    if (params.name) q.set("name", params.name);
    if (params.email) q.set("email", params.email);
    const qs = q.toString();
    return api.get<PaginatedResponse<Member>>(`${API_ENDPOINTS.MEMBERS}${qs ? `?${qs}` : ""}`);
  },

  get(id: string): Promise<Member> {
    return api.get<Member>(API_ENDPOINTS.MEMBERS_DETAIL(id));
  },

  create(payload: MemberCreatePayload): Promise<Member> {
    return api.post<Member>(API_ENDPOINTS.MEMBERS, payload);
  },

  update(id: string, payload: MemberUpdatePayload): Promise<Member> {
    return api.put<Member>(API_ENDPOINTS.MEMBERS_DETAIL(id), payload);
  },

  loans(id: string, activeOnly = false): Promise<import("../types").Loan[]> {
    return api.get(`${API_ENDPOINTS.MEMBERS_LOANS(id)}${activeOnly ? "?active_only=true" : ""}`);
  },
};
