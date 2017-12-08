# Sound Bites
# Michael Schulte-Mecklenbeck, Stefan Borer

# clean slate
rm(list = ls())
source("R_Packages+OwnFunctions.R")

load("../data/rawdata.Rdata")


# remove .wav from stim_id
rawdata$stim_id <- sub("(.*)\\.wav", "\\1", rawdata$stim_id)

# split into ratings and searches
ratings <- rawdata %>%
  filter(event %in% c("valence_rating", "arousal_rating")) %>%
  mutate(value = as.numeric(value))

searches <- rawdata %>%
  filter(event == "SearchResponse") %>%
  separate(stim_id, c("sound", "visual"), sep = "-", fill = "left")

# split stim_id into actual factors of the experiment:
# salience: L1 = low, L2 = high
# position: cen[..] = central, per[..] = peripheral
# orientation: l[..] = left, r[..] = right
searches <- searches %>%
  separate(visual, c("salience", "position", "orientation"), sep = "_") %>%
  mutate(salience = ifelse(salience == "L1", "high", "low")) %>%
  mutate(position = ifelse(grepl("cen", position), "central", "peripheral")) %>%
  mutate(orientation = ifelse(grepl("l", orientation), "left", "right"))

save(ratings, file = "../data/ratings.Rdata")
save(searches, file = "../data/searches.Rdata")
