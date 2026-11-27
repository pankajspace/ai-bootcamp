"""Shared Financial Modeling Prep (FinanceToolkit) helper used by Labs 2A and 2F."""
import os

import pandas as pd
from dotenv import load_dotenv
from financetoolkit import Toolkit

load_dotenv()
FINANCIAL_MODELING_PREP_API_KEY = os.environ["FINANCIAL_MODELING_PREP_API_KEY"]

PROFITABILITY_RATIOS = ["Return on Equity", "Return on Assets", "Gross Margin",
                        "Operating Margin", "Net Profit Margin"]
VALUATION_RATIOS = ["Price-to-Earnings", "Price-to-Book", "Price-to-Cash-Flow",
                    "Price-to-Free-Cash-Flow", "EV-to-EBITDA", "EV-to-Sales"]
LIQUIDITY_RATIOS = ["Current Ratio", "Quick Ratio", "Cash Ratio", "Working Capital",
                    "Operating Cash Flow Ratio", "Operating Cash Flow to Sales Ratio",
                    "Short Term Coverage Ratio"]


def collect_ratios(ticker: str) -> pd.DataFrame:
    companies = Toolkit([ticker], api_key=FINANCIAL_MODELING_PREP_API_KEY, start_date="2022-01-01")
    return companies.ratios.collect_all_ratios()     # ONE big table: rows = ratio names, columns = years


def pick(ratios: pd.DataFrame, names: list[str]) -> pd.DataFrame:
    return ratios.loc[ratios.index.intersection(names)]
