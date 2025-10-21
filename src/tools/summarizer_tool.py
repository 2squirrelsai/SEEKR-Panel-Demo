"""
Policy summarizer tool.

Condenses long policy documents into concise, actionable summaries.
"""

import logging
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

logger = logging.getLogger("ecom_cs_agent.tools")


class PolicySummarizerInput(BaseModel):
    """Input schema for policy summarizer."""
    policy_text: str = Field(
        ...,
        description="The policy text to summarize"
    )
    focus_area: str = Field(
        default="general",
        description="Specific area to focus on: general, timeframes, requirements, or process"
    )


class PolicySummarizerTool(BaseTool):
    """
    Tool to summarize long policy documents into key points.

    Extracts and highlights the most important information from
    policy documents, making them easier to understand and apply.
    """

    name: str = "policy_summarizer"
    description: str = (
        "Summarize long policy documents into concise key points. "
        "Use this to extract the most important information from lengthy policies. "
        "Can focus on specific areas like timeframes, requirements, or processes."
    )
    args_schema: Type[BaseModel] = PolicySummarizerInput

    def _run(self, policy_text: str, focus_area: str = "general") -> str:
        """
        Summarize policy text into key points.

        Args:
            policy_text: Full policy text to summarize
            focus_area: Area to focus the summary on

        Returns:
            Summarized policy information
        """
        logger.info(f"Summarizing policy (focus: {focus_area})")
        logger.debug(f"Policy text length: {len(policy_text)} characters")

        try:
            # This is a rule-based summarizer focusing on key patterns
            # In production, this could use an LLM for better summarization

            lines = policy_text.split('\n')
            key_points = []

            # Keywords to identify important information
            timeframe_keywords = ['days', 'day', 'within', 'deadline', 'period', 'window']
            requirement_keywords = ['must', 'required', 'need', 'necessary', 'should']
            process_keywords = ['step', 'process', 'procedure', 'how to', 'contact']
            condition_keywords = ['if', 'unless', 'provided', 'condition', 'eligible']

            # Select keywords based on focus area
            if focus_area.lower() == "timeframes":
                priority_keywords = timeframe_keywords
            elif focus_area.lower() == "requirements":
                priority_keywords = requirement_keywords
            elif focus_area.lower() == "process":
                priority_keywords = process_keywords
            else:
                priority_keywords = timeframe_keywords + requirement_keywords + condition_keywords

            # Extract sentences containing key information
            for line in lines:
                line = line.strip()
                if not line or len(line) < 20:
                    continue

                # Check if line contains priority keywords
                line_lower = line.lower()
                if any(keyword in line_lower for keyword in priority_keywords):
                    # Clean up the line
                    if not line.endswith(('.', '!', '?')):
                        line += '.'
                    key_points.append(f"• {line}")

            # If no key points found, extract first few meaningful sentences
            if not key_points:
                meaningful_lines = [
                    line.strip() for line in lines
                    if line.strip() and len(line.strip()) > 30
                ][:5]
                key_points = [f"• {line}" for line in meaningful_lines]

            # Build summary
            summary_header = f"KEY POINTS (Focus: {focus_area}):\n"
            summary_body = "\n".join(key_points[:10])  # Limit to top 10 points

            result = summary_header + summary_body

            logger.info(f"Generated summary with {len(key_points)} key points")
            return result

        except Exception as e:
            error_msg = f"Error summarizing policy: {str(e)}"
            logger.error(error_msg)
            return error_msg


def create_policy_summarizer() -> PolicySummarizerTool:
    """
    Factory function to create a policy summarizer tool.

    Returns:
        Configured PolicySummarizerTool instance
    """
    return PolicySummarizerTool()
