#!/usr/bin/env python
# coding: utf-8

# # Inside the War Room: An NFL Draft Analysis (2000-2021)

# ## I. Introduction

# As the National Football League (NFL) has expanded in size and popularity, so has the NFL draft in pursuing the next generation of star players. With the league's ever-changing rulebook and the game becoming more dynamic, every team is seeking to gain a competitive advantage in assembling their 52-man rosters. Hence, team owners and general managers commonly look at the yearly NFL draft to address their team's weak points and add a dash of young, raw, and driven talent to their rosters. That being said, not all NFL positions are created equally, and recent trends observed in the sport over the last few decades have subsequently compelled teams to reconsider how they build their rosters from the ground up—starting with the draft. Additionally, [with an abundance of literature and research](https://trace.tennessee.edu/cgi/viewcontent.cgi?article=1333&context=jasm) indicating the significance of a team's draft to its future success, it is more important than ever for all NFL franchises to dedicate a substantial portion of their offseason to scouting and scrutinizing the next cohort of athletes (Reynolds et al., 2015).
# 
# In this project, we will consider and potentially provide answers to questions such as:
# 
# - **Are certain positions more coveted in the draft than others?**
# - **What does the average draft look like over the years?**
# - **Do height, weight, and other attributes significantly help players' draft stock?**
# - **How important are players' colleges they attended in determining their selection?**
# - **Do successful and non-successful NFL teams behave differently in their approach to the draft?**
# 
# Our first steps should be loading the relevant datasets and considering some descriptive statistics.

# ## II. Initial Data Exploration

# In[1]:


import pandas as pd
import numpy as np
import statsmodels.api as sm
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.formula.api as smf
plt.style.use('ggplot')


# In[2]:


df = pd.read_csv(r'C:\Users\Connor\OneDrive\Documents\Data Analysis\Datasets\nfl_draft_data\2000-2021 Draft Picks.csv')


# In[3]:


df.head(3)


# In[4]:


# Descriptive data, though not particularly useful without quantitative (and some categorical) player attributes
df.describe()


# In[5]:


# Number of rows (total players drafted) and columns
print(df.shape)
# columns
print(df.columns)


# In[6]:


df.info()


# ## III. Cleaning and Enhancing the Data
# 
# We see that the data contains 5,609 players drafted in total from the years 2000-2021. Before examining and analyzing the data, we should clean and augment the data to ensure that we obtain accurate, insightful, and reliable results. Cleaning the dataset, though sometimes tedious, is paramount to our analysis.  

# In[7]:


# The Washington Football Team is now known as the Washington Commanders, therefore we should replace it to avoid confusion
df = df.replace(to_replace = 'TEAM', value = 'COMMANDERS')


# In[8]:


# Printing all positions selected in the years 2000-2021
print(df['Position'].unique())


# One important part of the cleaning process is to check for duplicates. Unfortunately, since many NFL players share the same name, we need to check if the same unique row appears once and only once. 

# In[9]:


# Check for exact duplicates
duplicate_rows = df[df.duplicated()]

# Print the result
if not duplicate_rows.empty:
    print("Exact duplicates were found:")
    print(duplicate_rows)
else:
    print("No exact duplicates were found.")


# At this moment, we should add important player attributes such as height and weight to our dataset. These characteristics, in addition to a player's position and college, should help give us even more insightful results. We can accomplish this by merging NFL Combine data—where college football players are evaluated physically and mentally prior to the draft—to our current dataset. 

# In[10]:


combine_df = pd.read_csv(r'C:\Users\Connor\OneDrive\Documents\Data Analysis\Datasets\nfl_draft_data\combine_stats_df.csv', index_col = 0)
combine_df.head(10)


# In[11]:


combine_df.describe()


# In[12]:


print(combine_df.columns)


# A few things immediately stand out to us which will make the cleaning process a bit more taxing. First, the school/university attended by the player is often not spelled the same way as it is in our original dataset (e.g., Boston Col. != Boston College). Second, and though we can remove it, is that the 'Pos' column has more positions than the original dataset, opting for depth over clarity. Lastly, some NaN values are several quantitative combine attributes such as Bench and Broad Jump; however, this is to be expected since not every position/player partakes in these events at the combine. Let's fix the school spelling issue first.

# In[13]:


# Iterate over each row in df
for index, row in df.iterrows():
    # Find the corresponding row in combine_df based on player name, draft year, and overall pick
    matching_row_index = (combine_df['Player'] == row['Name']) & (combine_df['draft_year'] == row['Year'])
    matching_row = combine_df[matching_row_index]
    
    # If a matching row is found
    if not matching_row.empty:
        # Update the college in combine_df to match df
        combine_df.loc[matching_row_index, 'School'] = row['School']

# verify that schools like  Boston Col. are now Boston College
combine_df.head()


# We can clearly see some differences between the two datasets. If we ignore these differences, we will have data that is either inconclusive or misleading, or both. For example, Offensive Tackle is listed as OT in the combine_stats dataset, but listed as T in the dataset we have been using thus far. Additionally, Defensive Back (DB) is now split into Cornerback (CB) and Safety (S) positions. Therefore, we must synchronize the datasets before we merge them in order to make sense of the data.

# In[14]:


# Merge the datasets based on 'Name', 'School', and 'draft_year'
merged_data = pd.merge(df, combine_df, how='left', left_on=['Name', 'School', 'Year'], right_on=['Player', 'School', 'draft_year'])

# Print the merged dataset
merged_data.head()


# In[15]:


merged_data.describe()


# The count tells us that there are 5,616 observations in the merged dataset, which cannot be right. This is likely due to duplicates being made due to players sharing the same name and year drafted. Let's check this below.

# In[16]:


duplicate_rows = merged_data[merged_data.duplicated(subset=['Name', 'School', 'Year'], keep=False)]
print(duplicate_rows)


# In[17]:


# Drop redundant columns
merged_data.drop(['Pos', 'draft_year', 'Player'], axis=1, inplace=True)

merged_data.drop_duplicates(subset=['Name', 'School', 'Year'], keep='first', inplace=True)
merged_data.describe()


# From above, we see that height is not being displayed in the descriptive statistics. Further exploration of the .csv file reveals that the height column displays data by inches added to a month of the year for feet (e.g., May and June representing 5 feet and 6 feet, respectively). Fortunately, we can rectify this with a simple conversion function. Converting the height to total inches will allow for easier calculation and analysis later.

# In[18]:


def convert_height_inches(height):
    try:
        # Extract feet and inches from the height
        feet, inches = map(int, height.split('-'))
        
        # Convert feet to inches and sum with inches
        total_inches = feet * 12 + inches
        
        return total_inches
    except:
        return None

# Applying the function to the 'Ht' column
merged_data['Ht'] = merged_data['Ht'].apply(convert_height_inches)


# In[19]:


merged_data.head(5)


# In[20]:


merged_data.describe()


# At this point, we have successfully cleaned the data, and judging by the descriptive statistics, there doesn't seem to be any outliers in the data. We can now move on to our analysis.

# ## IV. Statistical Analysis

# ### Descriptive Analysis

# In[21]:


overall_position_means = merged_data.groupby('Position')['Overall'].mean()
print(overall_position_means)

# Visualizing
plt.bar(overall_position_means.index, overall_position_means, color ='skyblue')
plt.title('Average NFL Draft Pick by Position (2000-2021) ')
plt.xlabel('Position')
plt.ylabel('Average Overall Pick')
plt.xticks(rotation=45, ha ='right')
plt.tight_layout()
plt.show()


# Evidently, players at the Kicker and Punter position seem to be selected much later in the draft relative to other positions. Quarterbacks tend to be selected earlier than other positions, with defensive edge (DE) players and Offensive Tackle (T) right behind them. Why might this be? 
# 
# History tells us that the most talented and NFL-ready players are selected in the first round of the draft. Let's visualize what the first round typically looks like by position.   

# In[22]:


first_round_data = merged_data[merged_data['Round'] == 1]
rd1_overall_position_means = first_round_data.groupby('Position')['Overall'].mean().reset_index()
print(rd1_overall_position_means)

# Visualizing 
plt.bar(rd1_overall_position_means['Position'], rd1_overall_position_means['Overall'], color ='skyblue')
plt.title('Average NFL Draft Pick by Position in the 1st Round (2000-2021) ')
plt.xlabel('Position')
plt.ylabel('Average Overall Pick in the 1st Round')
plt.xticks(rotation=45, ha ='right')
plt.tight_layout()
plt.show()


# We see that Quarterbacks are picked far earlier than the rest of the positions in the first round. Additionally, Tackles are taken quite early in addition to Quarterbacks. However, this is not a perfect visualization of the first round. For example, there has never been a Punter selected in the first round (which the data reflects), but Kickers are almost never taken in the first round. It would be unwise to assume based off the graph that Kickers are selected earlier than other position in the first round, as this is only taking the average. Let's make this a little more clear.

# In[23]:


# Calculate the frequency of positions drafted in the first round 
position_counts = first_round_data['Position'].value_counts().reset_index()
position_counts.columns = ['position', 'count']

plt.bar(position_counts['position'], position_counts['count'], color = 'orange', label = 'frequency')
plt.title('Distribution of Picks in the First Round by Position (2000-2021)')
plt.xlabel('Position')
plt.ylabel('Frequency (Count)')
plt.tight_layout()
plt.show()

position_counts


# NOTE: Defensive Backs include BOTH the Safety and Cornerback positions. Thus, their total is obviously higher than other positions listed since they are encompassing two different positions. In this sense, it may be more appropriate to judge the Defensive Back position by their average spot selected in the first round. 

# In[24]:


overall_position_means_yearly = merged_data.groupby(['Year', 'Position'])['Overall'].mean()


# In[25]:


from matplotlib.ticker import FuncFormatter

# Unstack the multi-index series to pivot the 'Position' index into columns
overall_position_means_yearly_unstacked = overall_position_means_yearly.unstack()

# Unique colors for each position
color_palette = sns.color_palette("husl", len(overall_position_means_yearly_unstacked.columns))

# Plot the time series with unique colors
ax = overall_position_means_yearly_unstacked.plot(figsize=(10, 6), color=color_palette)
plt.xlabel('Year')
plt.ylabel('Average Overall Draft Position')
plt.title('Average Overall Draft Position by Position and Year')
plt.legend(title='Position', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True)

# Start from the left edge
ax.set_xlim(overall_position_means_yearly_unstacked.index[0], overall_position_means_yearly_unstacked.index[-1])

# Remove decimals
def format_func(value, tick_number):
    return int(value)

ax.xaxis.set_major_formatter(FuncFormatter(format_func))

plt.tight_layout()  # Adjust layout to prevent overlap
plt.show()


# The time series above suggests the growing need for quarterback talent in today's NFL. Having the largest impact on the game not only with their arm but also with their legs, it is not surprising to see a shift in how early teams and General Managers are willing to take quarterbacks. 
# 
# NOTE: For some years, punters and kickers did not have a single selection in the draft, hence the incomplete series. 

# ### Predictive Analysis: OLS Regression
# 
# There are many other insights we would like to gain from this dataset. The combine is a pivotal part of the scouting process for many NFL executives, and so we should attempt to discover what exactly these executives are looking for in their new players. 

# In[26]:


# Renaming several columns of our dataset to avoid errors
merged_data.rename(columns={'40yd': 'Forty_yd'}, inplace=True)

merged_data.rename(columns={'Broad Jump': 'Broad_Jump'}, inplace=True)

merged_data.rename(columns={'3Cone': 'Cone_3'}, inplace=True)

formula = 'Overall ~ Ht + Wt + Forty_yd + Vertical + Bench + Broad_Jump + Cone_3 + Shuttle'

model = smf.ols(formula=formula, data=merged_data).fit()
print(model.summary())


# We can derive some key insights from the regression results above. 
# - We see that among the quantitative explanatory variables, all of the variables are significant at the 5% significance level except Vertical, Bench, and Shuttle. 
# - Looking at the test statistic values, the values for Weight, 40yd, and Broad Jump are the highest in absolute value, suggesting that they are the most significant predictors in determining a player's overall selection.
# - The intercept is nonsensical and simply an artifact of the regression. We cannot have a player with a Height and Weight of zero, nor can their overall selection be negative. 
# 
# That being said, caution should also be advised. For example, we see that a one unit increase in weight has an estimated decrease of approximately 1.20—holding all else constant—in a player's overall selection; however, a one unit increase in height has an estimated increase (taken later in the draft) of approximately 1.81 for the player's overall selection, holding all else constant. 
# 
# It is absolutely necessary to scrutinize these results before immediately interpreting them. For some positions, like Quarterback, we might expect an increase in height to help a player's draft stock, but that is not the case here for all positions. Why might that be? It may be because as we established before, quarterbacks are on average taken very early, and other larger positions (e.g., Offensive Linemen) are on average taken later in the draft. We can verify this by taking a look at how Height only affects the Quarterback position's overall selection.

# In[27]:


# Subset the data to include only quarterbacks
qb_data = merged_data[merged_data['Position'] == 'QB']

# Many Quarterbacks do not run the same speed/conditioning drills as other positions
formula_qb = 'Overall ~ Ht'


model_qb = smf.ols(formula=formula_qb, data=qb_data).fit()

print(model_qb.summary())


# In the above model, we utilize a simple linear regression to regress overall selection on Height for Quarterbacks only. So, as a Quarterback's height increases by one unit, their estimated overall draft selection decreases (they are selected earlier in the draft) by approximately -7.05. Additionally, Height is significant at the 5% significance level. This result is far different than the OLS result we obtained earlier, and should highlight how important it is to investigate the results first. 

# Regarding the university the player attended, OLS is more than likely going to conclude that none of the School indicator variables are significant. Thus, for simplicity, we will simply count the number of draft selections and first round draft selection by the top 20 schools. 

# In[327]:


# Get the top 20 schools based on counts
top_20_schools = merged_data['School'].value_counts().head(20).index

# Count the instances of each school in the overall draft and first round
school_draft_counts = {}
school_first_round_counts = {}

for school in top_20_schools:
    # Count instances in overall draft
    overall_count = len(merged_data[merged_data['School'] == school])
    school_draft_counts[school] = overall_count
    
    # Count instances in first round
    first_round_count = len(merged_data[(merged_data['School'] == school) & (merged_data['Round'] == 1)])
    school_first_round_counts[school] = first_round_count

print("Counts of selections for top 20 schools:")
print()
for school, draft_count in school_draft_counts.items():
    print(f"{school}: Overall Draft Selections: {draft_count}, First Round Selections: {school_first_round_counts[school]}")


# In[328]:


schools = list(school_draft_counts.keys())
overall_counts = list(school_draft_counts.values())
first_round_counts = list(school_first_round_counts.values())

plt.figure(figsize=(10, 6))
plt.scatter(overall_counts, first_round_counts, color='red')

plt.xlabel('Overall Draft Selections')
plt.ylabel('First Round Selections')
plt.title('Overall vs First Round Selections for Top 20 Schools')

# Add school names as annotations
for i, school in enumerate(schools):
    plt.annotate(school, (overall_counts[i], first_round_counts[i]))

# Show plot
plt.grid(True)
plt.tight_layout()
plt.show()


# We can see that from 2000-2021, Alabama and Ohio State tended to produce the most NFL-ready players.

# Having a franchise Quarterback that starts every season is a huge boon to an NFL team. Without one, teams will desperately try each off-season to determine who is the best available player to start at Quarterback, whether that be through free agency or the draft. Of course, backup players are always needed due to how many injuries occur to players every year. Nevertheless, we will ask and answer the question: "Does already having a franchise quarterback affect how a team approaches the draft?"
# 
# We will attempt to answer this question by considering teams that have had great success with one starting quarterback from 2000-2021 (New England, New Orleans, Pittsburgh) as well as considering teams with minimal success with starting quarterbacks (Chicago, Cleveland, Jacksonville). 

# In[329]:


# Define lists of teams for the two groups
successful_qb_teams = ['PATRIOTS', 'SAINTS', 'STEELERS']
poor_qb_teams = ['BEARS', 'BROWNS', 'JAGUARS']

# Create separate DataFrames for each group
good_qb = merged_data[merged_data['Team'].isin(successful_qb_teams)]
bad_qb = merged_data[merged_data['Team'].isin(poor_qb_teams)]


# In[330]:


# Occurrences of each position for the successful QB teams
good_qb_team_positions = good_qb['Position'].value_counts()

# Occurrences of each position for the poor QB teams
bad_qb_team_positions = bad_qb['Position'].value_counts()

print("Positions drafted by successful QB teams:")
print(good_qb_team_positions)
print("\nPositions drafted by poor QB teams:")
print(bad_qb_team_positions)


# In[331]:


# Sort positions by overall counts for successful QB teams
good_qb_sorted = good_qb_team_positions.sort_values(ascending=False)

# Sort positions by overall counts for poor QB teams
bad_qb_sorted = bad_qb_team_positions.sort_values(ascending=False)

plt.figure(figsize=(10, 6))
plt.bar(good_qb_sorted.index, good_qb_sorted, color='blue', alpha = 0.7, label='Successful QB Teams')
plt.bar(bad_qb_sorted.index, bad_qb_sorted, color='red', alpha = 0.7, label='Poor QB Teams')
plt.xlabel('Position')
plt.ylabel('Count')
plt.title('Comparison of Drafted Positions by QB Team Performance (Sorted)')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()


# Surprisingly, there is not much of a noticeable difference in how Quarterback-successful teams draft their players versus the teams that are not Quarterback-successful based on the distributions above. However, we can discern that the teams with poor Quarterback play generally have more draft picks at their disposal versus the Quarterback-successful teams. This is likely due to factors outside the draft, such as the poor Quarterback teams trading away their existing talented players for additional draft capital knowing that they won't make the playoffs without a talented Quarterback. 

# ## V. Conclusion
# 
# While this data does have its limitations and cannot be the only resource used to assess what a team might do in this year's NFL draft, it has nonetheless provided us some interesting insights. With data from 2000-2021, we determined that:
# 
# - Quarterbacks have continued to see their draft stock rise; that is, they are being taken earlier. 
# - Offensive Tackle (T), behind quarterback, is the most coveted position in the first round. 
# - Weight, 40-yard dash time, and Broad Jump are among the most significant predictors in determining one's overall draft selection.
# - Height is a more significant predictor of overall selection for Quarterbacks than most other positions. 
# - Alabama and Ohio State are the two most popular colleges for players drafted as well as for the most NFL-ready players (1st rd.)
# - NFL teams tend to not make significant changes to their draft ideologies depending on their current Quarterback situation.
# 
# Of course, there are even more questions outside of our scope to consider following these results, such as:
# 
# - Have recently succesful teams (e.g., Kansas City) drafted differently than other teams? If so, what kinds of players are  they targeting? 
# - Do some teams prefer players from certain colleges? If so, why?
# - Are location and geographic preference relevant variables to consider when selecting players?
# - Is there a long-term correlation between player attributes at the combine and future team success?
# - Is there a long-term correlation between overall draft position and career success in the NFL? Can we compare this to undrafted free agents/players? 
