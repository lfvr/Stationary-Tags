# Stationary Tags [Minchin]

MoveApps

Github repository: *github.com/lfvr/Stationary-Tags*

## Description
Map showing the location and ID of any tags that are currently stationary. Both the time and distance tolerance for determining stationarity can be customized in the app settings.

## Documentation
This app produces an interactive html map using OpenStreetMap tiles to plot the location of any stationary GPS tags.

The amount of tolerance allowed for a tag to be considered stationary can be customized in the app settings, allowing for different data profiles.

The app will ignore any tags that had a stationary period but have since started moving; it only displays tags that are still stationary at the end point of the data.

### Input data
MovingPandas TrajectoryCollection in Movebank format

### Output data
MovingPandas TrajectoryCollection in Movebank format
This is the same data as was input; this app does not modify the data in any way.

### Artefacts
`stationary.html`: interactive html map with the location and ID of each stationary tag

### Settings 
`Stop duration` (hours): The number of hours the tag must remain within the distance tolerance for this to be considered a stationary tag.
`Distance tolerance` (metres): The maximum distance (in metres) the tag can move whilst still being considered stationary. This allows for location error from GPS readings. 

### Null or error handling
The app currently expects the data to have CRS units in metres. If this is not the case, set the distance tolerance in the CRS units of the data.

There must be at least one other reading for a given animal within the `Stop duration` from the final reading for the animal. If there isn't, the app wil log an error for this animal and proceed with any other animals in the data set.
