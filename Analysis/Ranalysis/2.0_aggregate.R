# Sound Bites
# Michael Schulte-Mecklenbeck, Stefan Borer

# clean slate
rm(list = ls())
require(tidyverse)

# load data
load("../data/ratings.Rdata")
load("../data/searches.Rdata")

# plot rating across audiory stimuli
ggplot(ratings, aes(reorder(stim_id, value), value, colour = event)) +
  stat_summary(fun.y = mean, geom = "point") +
  stat_summary(fun.data = mean_cl_boot, geom = "errorbar", width = 0.1) + 
  facet_grid(. ~ event)

# reorder factor to represent Figure 2 order of Asutay et al., 2017
searches$sound <- fct_relevel(searches$sound, "firealarm", "growlingdog", "cluckinghen", "microwaveoven")

# plot response time across audiory stimuli
# there are 197 NAs where responses are >3500ms
ggplot(searches, aes(sound, responseTime, colour = salience)) +
  stat_summary(fun.y = mean, geom = "point") +
  stat_summary(fun.data = mean_cl_boot, geom = "errorbar", width = 0.1) + 
  facet_grid(salience ~ ., scales = "free") +
  theme_minimal(base_family = 'mono', base_size = 10)

ggsave('../plots/Rep_Figure2B.png')

# calculate accuracy for reproducing Table 1
# per sound/visual / high / low salient target

  searches %>%
    group_by(salience, sound) %>%
    summarise(RT = mean(responseTime, na.rm = TRUE),
              Accuracy = sum(accuracy)/length(accuracy))

### export as csv
write.table(durations, file = "../data/output/durations.csv",
            sep = ';', dec = '.', row.names = FALSE, col.names = TRUE, quote = FALSE)


save(durations, file = "../data/durations.Rdata")
