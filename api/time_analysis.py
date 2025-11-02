import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple, Set, Optional
from config import CONFIGS

def load_profit_data(file_path: Path) -> pd.DataFrame:
    """Load the profit percentages CSV file."""
    try:
        df = pd.read_csv(file_path)
        print(f"Loaded {len(df)} funds from {file_path.name}")
        return df
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return None
    except Exception as e:
        print(f"Error loading file: {e}")
        return None

def should_exclude_fund(fund_name: str, exclude_words: List[str]) -> bool:
    """Check if fund name contains any excluded words (case-insensitive)."""
    if not exclude_words:
        return False

    fund_name_upper = fund_name.upper()
    for word in exclude_words:
        if word.upper() in fund_name_upper:
            return True
    return False

def get_column_name_for_week(df: pd.DataFrame, week_number: int) -> str:
    """Find the column name for a specific week number."""
    # Column format is like "4 Weeks", "12 Weeks", etc.
    target_col = f"{week_number} Weeks"
    if target_col in df.columns:
        return target_col

    # If exact match not found, print available columns for debugging
    print(f"Warning: Column '{target_col}' not found. Available columns: {df.columns.tolist()[:5]}...")
    return None

def get_top_funds_for_week(df: pd.DataFrame, week_col: str, top_n: int, exclude_words: List[str], particular_funds: Optional[List[str]]) -> set:
    """Get the top N funds for a specific week column, with optional filtering."""
    # Convert to numeric, handling 'None' and other non-numeric values
    df_copy = df.copy()
    df_copy[week_col] = pd.to_numeric(df_copy[week_col], errors='coerce')

    # Remove NaN values
    valid_funds = df_copy.dropna(subset=[week_col])

    # Apply particular funds filter first (if specified)
    if particular_funds is not None:
        particular_funds_upper = [f.upper() for f in particular_funds]
        original_count = len(valid_funds)
        valid_funds = valid_funds[valid_funds['Fund'].str.upper().isin(particular_funds_upper)]
        filtered_count = len(valid_funds)
        if filtered_count < original_count:
            print(f"    Filtered to {filtered_count} particular funds (from {original_count} total)")

    # Apply exclusion filter (only if not using particular_funds)
    elif exclude_words:
        excluded_count = 0
        mask = ~valid_funds['Full Fund Name'].apply(lambda x: should_exclude_fund(str(x), exclude_words))
        excluded_count = len(valid_funds) - mask.sum()
        valid_funds = valid_funds[mask]
        if excluded_count > 0:
            print(f"    Excluded {excluded_count} funds containing: {exclude_words}")

    # Sort and get top N
    top_funds = valid_funds.nlargest(top_n, week_col)

    return set(top_funds['Fund'].values)

def find_overlapping_funds(df: pd.DataFrame, weeks: List[int], top_n: int, min_appearances: int,
                          exclude_words: List[str], particular_funds: Optional[List[str]]) -> pd.DataFrame:
    """Find funds that appear in top N for at least min_appearances weeks."""

    # Get column names for each week
    week_columns = {}
    for week in weeks:
        col_name = get_column_name_for_week(df, week)
        if col_name is None:
            print(f"Skipping week {week} - column not found")
            continue
        week_columns[week] = col_name

    if not week_columns:
        print("Error: No valid week columns found")
        return pd.DataFrame()

    # Get top funds for each week (with filtering)
    top_funds_per_week = {}
    for week, col_name in week_columns.items():
        top_funds = get_top_funds_for_week(df, col_name, top_n, exclude_words, particular_funds)
        top_funds_per_week[week] = top_funds
        print(f"  Week {week}: {len(top_funds)} top funds")

    # Count appearances for each fund across all weeks
    fund_appearance_count = {}
    all_funds = set()
    for week_funds in top_funds_per_week.values():
        all_funds.update(week_funds)

    for fund in all_funds:
        count = sum(1 for week_set in top_funds_per_week.values() if fund in week_set)
        fund_appearance_count[fund] = count

    # Filter funds that meet minimum appearance threshold
    qualifying_funds = {fund for fund, count in fund_appearance_count.items() if count >= min_appearances}

    print(f"  Funds with at least {min_appearances} appearances: {len(qualifying_funds)}")

    if not qualifying_funds:
        return pd.DataFrame()

    # Create result dataframe with qualifying funds
    result_df = df[df['Fund'].isin(qualifying_funds)].copy()

    # Double-check filters in final results (safety check)
    if particular_funds is not None:
        particular_funds_upper = [f.upper() for f in particular_funds]
        original_count = len(result_df)
        result_df = result_df[result_df['Fund'].str.upper().isin(particular_funds_upper)]
        if len(result_df) < original_count:
            print(f"  Removed {original_count - len(result_df)} non-particular funds from final results")
    elif exclude_words:
        original_count = len(result_df)
        result_df = result_df[~result_df['Full Fund Name'].apply(lambda x: should_exclude_fund(str(x), exclude_words))]
        if len(result_df) < original_count:
            print(f"  Removed {original_count - len(result_df)} excluded funds from final results")

    # Add columns showing the profit for each analyzed week
    analysis_columns = ['Fund', 'Full Fund Name']
    for week in sorted(weeks):
        if week in week_columns:
            analysis_columns.append(week_columns[week])

    # Add appearance count
    appearance_counts = []
    for fund in result_df['Fund']:
        count = fund_appearance_count.get(fund, 0)
        appearance_counts.append(count)
    result_df['Appearances'] = appearance_counts

    # Select and order columns
    final_columns = analysis_columns + ['Appearances']
    result_df = result_df[final_columns]

    # Sort by appearances first (descending), then by first week column (descending)
    first_week_col = week_columns[sorted(weeks)[0]]
    result_df[first_week_col] = pd.to_numeric(result_df[first_week_col], errors='coerce')
    result_df = result_df.sort_values(['Appearances', first_week_col], ascending=[False, False])

    return result_df

def main():
    # Get script directory
    script_dir = Path(__file__).parent
    input_file = script_dir / 'all_fund_profit_percentages_api.csv'

    # Load data
    print("Loading profit data...")
    df = load_profit_data(input_file)

    if df is None or df.empty:
        print("Failed to load data. Exiting.")
        return

    # Process each configuration
    for config_name, config in CONFIGS.items():
        weeks = config['weeks']
        top_n = config['top_n']
        min_appearances = config['min_appearances']
        exclude_words = config['exclude_words']
        particular_funds = config['particular_funds']
        output_file = config['output_file']

        print(f"\nProcessing configuration: {config_name}")
        print(f"  Analyzing weeks: {weeks}")
        print(f"  Top N per week: {top_n}")
        print(f"  Minimum appearances: {min_appearances} out of {len(weeks)}")

        if particular_funds is not None:
            print(f"  Analyzing ONLY particular funds: {particular_funds}")
        else:
            print(f"  Excluding funds containing: {exclude_words}")

        result_df = find_overlapping_funds(
            df,
            weeks,
            top_n,
            min_appearances,
            exclude_words,
            particular_funds
        )

        if result_df.empty:
            print(f"  No qualifying funds found for {config_name}")
            continue

        # Save to CSV
        output_path = script_dir / output_file
        result_df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"  Saved {len(result_df)} funds to {output_path.name}")

        # Show top 10 (or all if less than 10)
        display_count = min(10, len(result_df))
        print(f"\n  Top {display_count} funds for {config_name}:")
        for idx, row in result_df.head(display_count).iterrows():
            print(f"    {row['Fund']} (appears {int(row['Appearances'])}x)")

    print("\nAnalysis complete!")

if __name__ == '__main__':
    main()
