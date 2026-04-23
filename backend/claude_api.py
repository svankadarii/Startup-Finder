import os
import json
import anthropic
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = """You are a startup research expert helping someone find a job at a startup.
Analyze the given startup and return ONLY a valid JSON object — no markdown, no explanation, no extra text.

The JSON must have exactly these fields:
{
  "research_summary": "2-3 sentences about what they do and why it matters",
  "hiring_score": 75,
  "hiring_reasoning": "Why this score — specific signals from their stage/size/industry",
  "best_time_to_reach": "When to contact them and why",
  "contact_titles": ["CTO", "VP Engineering", "Engineering Manager"],
  "contact_search_tips": "LinkedIn search: 'company name engineer'. GitHub: check their org page. Twitter: search company handle + hiring.",
  "cold_message_template": "Hi [NAME], I've been following [COMPANY] and really admire [SPECIFIC_DETAIL]. I'm a [YOUR_ROLE] with experience in [RELEVANT_SKILL]. Would love to chat about [SPECIFIC_OPPORTUNITY]. — [YOUR_NAME]",
  "pain_points": [
    "Pain point description 1",
    "Pain point description 2",
    "Pain point description 3",
    "Pain point description 4"
  ],
  "project_ideas": [
    {
      "name": "Project Name",
      "description": "What it does and why it solves their problem",
      "solves_pain_point": "Which pain point this addresses",
      "tech_stack": ["React", "Python"],
      "build_time": "2-3 days"
    }
  ]
}

hiring_score must be an integer 0-100.
pain_points must be a list of 4-6 plain strings.
project_ideas must be a list of 3-5 objects."""


class ClaudeAPI:
    def __init__(self):
        key = os.environ.get("ANTHROPIC_API_KEY", "")
        if key:
            self.client = anthropic.Anthropic(api_key=key)
        else:
            self.client = None
            print("WARNING: ANTHROPIC_API_KEY not set. Claude features disabled.")

    def analyze_startup(self, startup: dict) -> dict:
        """
        Single Claude call that returns everything: research, hiring score,
        contacts, pain points, and project ideas. Results should be cached
        by the caller — never call this twice for the same startup.
        """
        if not self.client:
            return {"error": "ANTHROPIC_API_KEY not set. Add it to backend/.env"}

        name = startup.get("name", "Unknown")
        prompt = f"""Analyze this startup for a job seeker:

Name: {name}
Website: {startup.get("website") or "N/A"}
Description: {startup.get("description") or "N/A"}
Industry: {startup.get("industry") or "N/A"}
Funding Stage: {startup.get("funding_stage") or "N/A"}
Funding Amount: {startup.get("funding_amount") or "N/A"}
Team Size: {startup.get("team_size") or "N/A"}
LinkedIn Followers: {startup.get("linkedin_followers") or "N/A"}
YC Batch: {startup.get("yc_batch") or "N/A"}

Return the JSON object described in the system prompt. Be specific and actionable."""

        try:
            msg = self.client.messages.create(
                model=MODEL,
                max_tokens=2000,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            text = msg.content[0].text.strip()

            # Strip markdown fences if model adds them
            if text.startswith("```"):
                parts = text.split("```")
                text = parts[1] if len(parts) > 1 else text
                if text.startswith("json"):
                    text = text[4:]

            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(text[start:end])

            return {"error": "Claude returned non-JSON response", "raw": text[:500]}

        except json.JSONDecodeError as e:
            return {"error": f"JSON parse error: {e}"}
        except anthropic.APIError as e:
            return {"error": f"Claude API error: {e}"}
        except Exception as e:
            return {"error": str(e)}
