"""FP&A budget-versus-actual analysis using synthetic 2025 data.

Run from the repository root:
    python fpa_analysis.py
Requires pandas: pip install pandas
"""
from pathlib import Path
import pandas as pd

DATA_FILE = Path(__file__).resolve().parent / 'fpa_financial_data_2025.csv'
OUTPUT_DIR = Path(__file__).resolve().parent / 'outputs'


def main():
    df = pd.read_csv(DATA_FILE)
    required = {'Month', 'Department', 'Revenue_Budget_EUR', 'Revenue_Actual_EUR',
                'Expense_Budget_EUR', 'Expense_Actual_EUR'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f'Missing required columns: {sorted(missing)}')
    if df.empty:
        raise ValueError('Input CSV has no rows')
    numeric_cols = sorted(required - {'Month', 'Department'})
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='raise')
    if df[numeric_cols].isna().any().any():
        raise ValueError('Financial columns contain missing values')

    df['Revenue_Variance_EUR'] = df['Revenue_Actual_EUR'] - df['Revenue_Budget_EUR']
    df['Expense_Variance_EUR'] = df['Expense_Budget_EUR'] - df['Expense_Actual_EUR']
    df['Budget_Profit_EUR'] = df['Revenue_Budget_EUR'] - df['Expense_Budget_EUR']
    df['Actual_Profit_EUR'] = df['Revenue_Actual_EUR'] - df['Expense_Actual_EUR']
    df['Profit_Variance_EUR'] = df['Actual_Profit_EUR'] - df['Budget_Profit_EUR']
    df['Actual_Profit_Margin_Pct'] = (df['Actual_Profit_EUR'] / df['Revenue_Actual_EUR'].replace(0, float('nan'))) * 100

    money_cols = numeric_cols + ['Revenue_Variance_EUR', 'Expense_Variance_EUR',
                                  'Budget_Profit_EUR', 'Actual_Profit_EUR', 'Profit_Variance_EUR']
    by_department = df.groupby('Department', as_index=False)[money_cols].sum()
    by_department['Actual_Profit_Margin_Pct'] = (
        by_department['Actual_Profit_EUR'] / by_department['Revenue_Actual_EUR'].replace(0, float('nan')) * 100
    )
    by_month = df.groupby('Month', as_index=False)[money_cols].sum()
    by_month['Actual_Profit_Margin_Pct'] = (
        by_month['Actual_Profit_EUR'] / by_month['Revenue_Actual_EUR'].replace(0, float('nan')) * 100
    )

    OUTPUT_DIR.mkdir(exist_ok=True)
    df.to_csv(OUTPUT_DIR / 'fpa_detailed_analysis.csv', index=False)
    by_department.to_csv(OUTPUT_DIR / 'fpa_department_summary.csv', index=False)
    by_month.to_csv(OUTPUT_DIR / 'fpa_monthly_summary.csv', index=False)

    print('FP&A ANALYSIS — 2025 (synthetic EUR data)')
    print(f"Actual revenue: EUR {df['Revenue_Actual_EUR'].sum():,.2f}")
    print(f"Actual expenses: EUR {df['Expense_Actual_EUR'].sum():,.2f}")
    print(f"Actual profit: EUR {df['Actual_Profit_EUR'].sum():,.2f}")
    print(f"Profit variance: EUR {df['Profit_Variance_EUR'].sum():,.2f}")
    print(f'CSV reports saved in: {OUTPUT_DIR}')


if __name__ == '__main__':
    main()
