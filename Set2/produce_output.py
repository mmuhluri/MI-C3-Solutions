import pandas as pd

# Load data
df = pd.read_excel('ipdr.xlsx', sheet_name='ipdr.csv')

# Convert datetime columns
df['starttime'] = pd.to_datetime(df['starttime'], format='%Y-%m-%d%H:%M:%S')
df['endtime'] = pd.to_datetime(df['endtime'], format='%Y-%m-%d%H:%M:%S')

# Calculate adjusted end time
df['ET_adj'] = df['endtime'] - pd.Timedelta(minutes=10)
mask = df['ET_adj'] < df['starttime']
df.loc[mask, 'ET_adj'] = df.loc[mask, 'endtime']

# Sort by MSISDN, domain, and start time
df_sorted = df.sort_values(by=['msisdn', 'domain', 'starttime']).reset_index(drop=True)

# Determine session IDs based on gaps between FDRs
df_sorted['prev_et_adj'] = df_sorted.groupby(['msisdn', 'domain'])['ET_adj'].shift(1)
df_sorted['new_session'] = (df_sorted['starttime'] > df_sorted['prev_et_adj']) | df_sorted['prev_et_adj'].isna()
df_sorted['session_id'] = df_sorted.groupby(['msisdn', 'domain'])['new_session'].cumsum()

# Aggregate session data
aggregated = df_sorted.groupby(['msisdn', 'domain', 'session_id']).agg(
    start_time=('starttime', 'min'),
    end_time_adj=('ET_adj', 'max'),
    sum_ul=('ulvolume', 'sum'),
    sum_dl=('dlvolume', 'sum'),
    fdr_count=('session_id', 'count')
).reset_index()

# Calculate duration in seconds
aggregated['duration_sec'] = (aggregated['end_time_adj'] - aggregated['start_time']).dt.total_seconds()

# Filter out sessions with duration <= 0
aggregated = aggregated[aggregated['duration_sec'] > 0]

# Calculate total volume in kilobits and bit rate
aggregated['total_volume_bytes'] = aggregated['sum_ul'] + aggregated['sum_dl']
aggregated['total_volume_kb'] = (aggregated['total_volume_bytes'] * 8) / 1000  # Convert bytes to kilobits
aggregated['kbps'] = aggregated['total_volume_kb'] / aggregated['duration_sec']

# Filter out sessions with bit rate < 10 kbps
filtered = aggregated[aggregated['kbps'] >= 10]

# Classify audio and video calls
filtered['isAudio'] = filtered['kbps'] <= 200
filtered['isVideo'] = filtered['kbps'] > 200

# Select and rename output columns
output = filtered[[
    'msisdn', 'domain', 'duration_sec', 'fdr_count', 'kbps', 'isAudio', 'isVideo'
]].rename(columns={'msisdn': 'Msisdn'})

# Save output
output.to_csv('output.csv', index=False)