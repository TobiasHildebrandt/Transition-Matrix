import knime.scripting.io as knio

# This example script simply outputs the node's input table.
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df_log = knio.input_tables[0].to_pandas()

# Ensure time is a datetime column
df_log['time'] = pd.to_datetime(df_log['time'], format='mixed')

# Step 1: Sort by user and time
df_log = df_log.sort_values(by=['student_course_id', 'time'])

# Step 2: Generate transitions
df_log['next_section'] = df_log.groupby('student_course_id')['cross_section'].shift(-1)
transitions = df_log.dropna(subset=['next_section']).groupby(['cross_section', 'next_section']).size().reset_index(name='count')

# Step 3: Calculate total outgoing transitions for each source section
outgoing_totals = transitions.groupby('cross_section')['count'].sum().to_dict()

# Step 4: Create a transition matrix
all_sections = sorted(set(df_log['cross_section']).union(set(df_log['next_section'].dropna())))
transition_matrix = pd.DataFrame(0, index=all_sections, columns=all_sections)

for _, row in transitions.iterrows():
    if outgoing_totals[row['cross_section']] > 0:  # Normalize using total outgoing transitions
        transition_matrix.at[row['next_section'], row['cross_section']] = (row['count'] / outgoing_totals[row['cross_section']]) * 100

# Step 5: Generate heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(transition_matrix, annot=False, fmt=".1f", cmap="Blues", linewidths=0.5, linecolor='black')
plt.title('Transition Frequency Heatmap (Normalized by Outgoing Transitions)', fontsize=16)
plt.xlabel('From Section', fontsize=12)
plt.ylabel('To Section', fontsize=12)
plt.xticks(rotation=90, fontsize=10, ha='center')
plt.yticks(rotation=0, fontsize=10, va='center')
plt.tight_layout()
plt.savefig("cross_course.png")

knio.output_tables[0] = knio.input_tables[0]