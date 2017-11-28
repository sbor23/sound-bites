# Sound Bites
# Michael Schulte-Mecklenbeck, Stefan Borer

# clean slate
rm(list = ls())
require(tidyverse)


### Data import from csv files ###
# get list of all data files
# See Exp_Bemerkungen.xlsx
filelist <- list.files(path = "../data/rawdata/", full.names = TRUE)

# load the first file -> data frame has right number of columns
rawdata <- read.csv(file = filelist[1], header = TRUE, stringsAsFactors = FALSE, encoding = "UTF-8")

# load all the remaining files, merge them
for (file in filelist[2:length(filelist)]) {
  tempdata <- read.csv(file = file, header = TRUE, stringsAsFactors = FALSE, encoding = "UTF-8")
  rawdata <- rbind(rawdata, tempdata)
}

glimpse(rawdata)


# save
save(rawdata, file = "../data/rawdata.Rdata")
