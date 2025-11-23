# Configuration file for fund analysis

# Common exclusion lists - define once, reuse multiple times
COMMON_EXCLUSIONS = {
    'all_special': [],
    'my_funds': ['DCB', 'GBV', 'GO6', 'HVT', 'IIE', 'IVY', 'OJK', 'PBN', 'PPN', 'PRY', 'TCA', 'TMM']
}

# Main configurations
CONFIGS = {
    '0-36': {
        'weeks': [2, 4, 12, 24, 36],
        'top_n': 30,
        'min_appearances': 3,
        'exclude_words': COMMON_EXCLUSIONS['all_special'],
        'particular_funds': None,
        'output_file': 'top_funds_0-36_weeks.csv'
    },
    '0-52': {
        'weeks': [2, 4, 15, 26, 37, 52],
        'top_n': 35,
        'min_appearances': 4,
        'exclude_words': COMMON_EXCLUSIONS['all_special'],
        'particular_funds': None,
        'output_file': 'top_funds_0-52_weeks.csv'
    },
    '0-72': {
        'weeks': [2, 4, 15, 26, 37, 52, 72],
        'top_n': 45,
        'min_appearances': 5,
        'exclude_words': COMMON_EXCLUSIONS['all_special'],
        'particular_funds': None,
        'output_file': 'top_funds_0-72_weeks.csv'
    },
    'my-portfolio': {
        'weeks': [2, 4, 15, 26, 37, 52, 72],
        'top_n': 100,
        'min_appearances': 1,
        'exclude_words': [],
        'particular_funds': COMMON_EXCLUSIONS['my_funds'],
        'output_file': 'my_portfolio_analysis.csv'
    },
}
