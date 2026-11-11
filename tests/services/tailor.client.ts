import { APIRequestContext, APIResponse } from "@playwright/test";

export interface TailorRequestPayload {
  job_description?: string;
  job_text?: string;
  job_spec?: any;
  target_role?: string;
  template?: string;
  lang?: string;
  provider?: string;
}

export class TailorClient {
  constructor(private readonly request: APIRequestContext) {}

  private getHeaders(token?: string) {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    return headers;
  }

  async analyzeJob(jobText: string, provider: string = "auto"): Promise<APIResponse> {
    return this.request.post("/api/analyze-job", {
      headers: { "Content-Type": "application/json" },
      data: {
        job_text: jobText,
        provider,
      },
    });
  }

  async tailor(payload: TailorRequestPayload, token?: string): Promise<APIResponse> {
    return this.request.post("/api/tailor", {
      headers: this.getHeaders(token),
      data: payload,
    });
  }

  async refine(
    currentData: any,
    instruction: string,
    lang: string = "pl",
    token?: string
  ): Promise<APIResponse> {
    return this.request.post("/api/refine-cv", {
      headers: this.getHeaders(token),
      data: {
        current_cv_data: currentData,
        user_instruction: instruction,
        lang,
      },
    });
  }

  async renderPreview(
    profile: any,
    template: string = "pro_qa_sidebar",
    lang: string = "pl",
    token?: string
  ): Promise<APIResponse> {
    return this.request.post("/preview/render", {
      headers: this.getHeaders(token),
      data: {
        profile,
        template,
        lang,
      },
    });
  }

  async exportPdf(payload: any, token?: string): Promise<APIResponse> {
    return this.request.post("/api/export/pdf", {
      headers: this.getHeaders(token),
      data: payload,
    });
  }
}
