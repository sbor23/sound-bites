# Sound Bites
# Michael Schulte-Mecklenbeck, Stefan Borer

# clean slate
rm(list = ls())
require(tidyverse)
#source("R_Packages+OwnFunctions.R")

# load raw data
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
# code "visual only" (ie without sound) into sound variable
searches <- searches %>%
  separate(visual, c("salience", "position", "orientation"), sep = "_") %>%
  
  # recode some values
  mutate(salience = recode(salience,
                           L1 = "high",
                           L2 = "low")) %>%
  mutate(position = case_when(
    grepl("cen", position) ~ "central",
    grepl("per", position) ~ "peripheral")) %>%
  mutate(orientation = case_when(
    grepl("[lL]", orientation) ~ "left",
    grepl("[rR]", orientation) ~ "right")) %>%
  mutate(sound = ifelse(is.na(sound), "visual only", sound)) %>%
  
  # transform RTs into milliseconds
  mutate(responseTime = responseTime * 1000) %>%
  
  # calculate accuracy
  mutate(accuracy = case_when(
    orientation == value ~ 1,
    TRUE                 ~ 0
  ))

# save data frames
save(ratings, file = "../data/ratings.Rdata")
save(searches, file = "../data/searches.Rdata")
