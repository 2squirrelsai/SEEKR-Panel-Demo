"""
Return eligibility calculator tool.

Determines if a product return is eligible based on purchase date and policy timeframe.
"""

import logging
from datetime import datetime, timedelta
from typing import ClassVar, Type, Dict
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

logger = logging.getLogger("ecom_cs_agent.tools")


class ReturnEligibilityInput(BaseModel):
    """Input schema for return eligibility calculator."""
    purchase_date: str = Field(
        ...,
        description="Purchase date in format YYYY-MM-DD (e.g., 2024-01-15)"
    )
    product_category: str = Field(
        default="general",
        description="Product category: general, electronics, clothing, or food"
    )
    current_date: str = Field(
        default=None,
        description="Current date in format YYYY-MM-DD (defaults to today)"
    )


class ReturnEligibilityCalculator(BaseTool):
    """
    Tool to calculate whether a return is within the eligible timeframe.

    Different product categories have different return windows:
    - General products: 30 days
    - Electronics: 15 days
    - Clothing: 60 days
    - Food/Perishables: 7 days
    """

    name: str = "return_eligibility_calculator"
    description: str = (
        "Calculate if a product return is eligible based on purchase date. "
        "Provide the purchase date in YYYY-MM-DD format and product category. "
        "Returns eligibility status and days remaining or days overdue."
    )
    args_schema: Type[BaseModel] = ReturnEligibilityInput

    # Return window policies by category (in days)
    RETURN_WINDOWS: ClassVar[Dict[str, int]] = {
        "general": 30,
        "electronics": 15,
        "clothing": 60,
        "food": 7,
        "perishables": 7
    }

    def _run(
        self,
        purchase_date: str,
        product_category: str = "general",
        current_date: str = None
    ) -> str:
        """
        Calculate return eligibility.

        Args:
            purchase_date: Date of purchase (YYYY-MM-DD)
            product_category: Category of product
            current_date: Current date (defaults to today)

        Returns:
            Eligibility determination with details
        """
        logger.info(f"Calculating return eligibility for purchase: {purchase_date}")
        logger.debug(f"Product category: {product_category}")

        try:
            # Parse dates
            purchase_dt = datetime.strptime(purchase_date, "%Y-%m-%d")

            if current_date:
                current_dt = datetime.strptime(current_date, "%Y-%m-%d")
            else:
                current_dt = datetime.now()

            # Get return window for category
            category_normalized = product_category.lower()
            return_window_days = self.RETURN_WINDOWS.get(
                category_normalized,
                self.RETURN_WINDOWS["general"]
            )

            # Calculate days since purchase
            days_since_purchase = (current_dt - purchase_dt).days

            # Calculate eligibility
            deadline_date = purchase_dt + timedelta(days=return_window_days)
            is_eligible = current_dt <= deadline_date

            # Build response
            if is_eligible:
                days_remaining = (deadline_date - current_dt).days
                result = (
                    f"✓ ELIGIBLE FOR RETURN\n"
                    f"Purchase Date: {purchase_date}\n"
                    f"Product Category: {product_category}\n"
                    f"Return Window: {return_window_days} days\n"
                    f"Days Since Purchase: {days_since_purchase}\n"
                    f"Days Remaining: {days_remaining}\n"
                    f"Deadline: {deadline_date.strftime('%Y-%m-%d')}"
                )
                logger.info(f"Return eligible - {days_remaining} days remaining")
            else:
                days_overdue = days_since_purchase - return_window_days
                result = (
                    f"✗ NOT ELIGIBLE FOR RETURN\n"
                    f"Purchase Date: {purchase_date}\n"
                    f"Product Category: {product_category}\n"
                    f"Return Window: {return_window_days} days\n"
                    f"Days Since Purchase: {days_since_purchase}\n"
                    f"Days Overdue: {days_overdue}\n"
                    f"Deadline Was: {deadline_date.strftime('%Y-%m-%d')}\n"
                    f"Note: Customer may contact support for special consideration"
                )
                logger.info(f"Return not eligible - {days_overdue} days overdue")

            return result

        except ValueError as e:
            error_msg = f"Invalid date format. Please use YYYY-MM-DD format. Error: {str(e)}"
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Error calculating return eligibility: {str(e)}"
            logger.error(error_msg)
            return error_msg


def create_return_calculator() -> ReturnEligibilityCalculator:
    """
    Factory function to create a return eligibility calculator.

    Returns:
        Configured ReturnEligibilityCalculator instance
    """
    return ReturnEligibilityCalculator()
