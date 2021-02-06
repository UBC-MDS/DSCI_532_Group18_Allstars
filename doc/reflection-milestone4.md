reflection-milestone4
================
Deepak Sidhu, Nicholas Wu, William Xu, Zeliha Ural Merpez

# Reflection

## Choosing Python over R

Our group decided to continue working on the Python version of our dashboard. 
This is mainly because dash in Python is generally easier to work with. 
Specifically, because we plan to implement a data table that shows country 
specific data from the happiness data set, we felt that using Altair and Python 
would be a better choice for implementation. In addition, we also felt that 
dashboard in Python is easier to debug and faster deploy. When researching on 
coding problems, it also seems that there are more supporting resources on dash 
for Python/Altair than for R/ggplotly. Based on the above, we utimately chose to 
continue to improve on our Python version of the dashboard. 

## What We Have Implemented

In this milestone, we were able to build on previous version and implement most 
of the proposed functions in our dashboard. On top of the world map, we added an
extra layer of customization. A user can ask the world map to show all countries
or only the filtered ones. This gives the user the ability to zoom in on 
the world map and focus on the region of interest. 

Based on Joel's feedback, we also added "Top 20 Countries" as an option in the 
region selection bar. Combining this option with the "Ascending" and 
"Descending" buttons on top of the bar chart, a user will be able to expand 
their exploration zone and see both top and bottom rankings of any matrix. 

In the country-to-country comparison, we added the data table as an widget at 
the bottom right of the dashboard. If a user simultaneously hold the SHIFT key
and click on either the happiness score or the density plot, the data table 
widget will show the rent and cost index of highlighted countries in a table. 
This helps the user to explore two more matrices among countries and 
make an informative decision. 


## What Is Not Yet Working

Initially, we planned to plot two pie charts that help the user visualize the 
proportion between population and migrants of each country. This has been left 
out due to time and space constraint. We 

Some countries are not showing on the world map due to missing data in our data 
set. We have added a note on top of the world map to communicate the underlying 
assumption. 

## Ease of Use, Reoccuring Feedback, Strength and Room for Improvement

Based on TA and peer feedback, our app has been consistently easy to use and 
aesthetically pleasing. We provided clear instruction and comments throughout 
the dashboard. It delivered a pleasant flow for user to explore the happiness 
data set.

The data table currently present rent and living cost index, which we felt are 
the most relevant factors in making a decision. If time permits, we wish to 
include more matrices in the data table widget so auser can get a clearer 
picture in country comparison. 



