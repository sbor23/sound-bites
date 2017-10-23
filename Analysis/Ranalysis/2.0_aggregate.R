# Sound Bites
# Michael Schulte-Mecklenbeck, Stefan Borer

# clean slate
rm(list = ls())
source("R_Packages+OwnFunctions.R")

load("../data/ratings.Rdata")
load("../data/searches.Rdata")


# summarise the rating values
ratings <- ratings %>%
  group_by(stim_id, event) %>%
  summarise(
    val = mean(value)
  )

### ....


### export as csv
write.table(durations, file = "../data/output/durations.csv",
            sep = ';', dec = '.', row.names = FALSE, col.names = TRUE, quote = FALSE)


save(durations, file = "../data/durations.Rdata")
