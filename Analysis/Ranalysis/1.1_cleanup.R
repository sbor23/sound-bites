# Sound Bites
# Michael Schulte-Mecklenbeck, Stefan Borer

# clean slate
rm(list = ls())
require(tidyverse)

# load raw data
load("../data/rawdata.Rdata")

# remove respondents with NAs
rawdata <- rawdata[!is.na(rawdata$responseTime),] 


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
# salience: L1 = high, L2 = low
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

  # check accuracy per participant
  sum.searches <- 
    searches %>%
    group_by(respondent, block_nr) %>%
    summarise(acc.part = sum(accuracy),
              acc.perc = 100/32*acc.part)
  
  # there are some participants with close to zero accuracy
  # we assumae that these participants flipped the response key order (in their head)
  # we could a) recode them or b) remove them - to make less assumptions we remove them  
  # we do this at the top of this file
  exclusion.list <- unique(sum.searches[sum.searches$acc.part < 10,]$respondent)
  
  searches <- searches[!(searches$respondent %in% exclusion.list),]
  ratings <- searches[!(ratings$respondent %in% exclusion.list),]
  
  
# save data frames
save(ratings, file = "../data/ratings.Rdata")
save(searches, file = "../data/searches.Rdata")
