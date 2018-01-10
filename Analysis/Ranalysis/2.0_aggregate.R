# Sound Bites
# Michael Schulte-Mecklenbeck, Stefan Borer

# clean slate
rm(list = ls())
require(tidyverse)
# install.packages('ez') #run once!
require(ez)

# load data
load("../data/ratings.Rdata")
load("../data/searches.Rdata")

# arousal and valence
# A ective reactions to auditory stimuli were scaled between −1 and +1, and 
# entered into an ANOVA with stimulus (4 stimuli) and location (frontal vs. rear) 
# within-subject factors (see Supplemental Table 1 for average ratings). 

ratings %>%
  group_by(stim_id, event) %>%
  mutate(ind = row_number()) %>%
  spread(stim_id, event) %>% 
  select(stim_id, event)

ratings %>%
  spread(event, value)
  group_by(stim_id, event) %>%
  summarise(arousal = mean(value),
            valence = mean(value))

# plot rating across audiory stimuli
ggplot(ratings, aes(reorder(stim_id, value), value, colour = event)) +
  stat_summary(fun.y = mean, geom = "point", size = 2) +
  stat_summary(fun.data = mean_cl_boot, geom = "errorbar", width = 0.1) + 
  facet_grid(. ~ event) +
  ylim(0,1) +
  theme_minimal(base_family = 'mono', base_size = 18) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))

ggsave('../plots/Rep_Figure2A.png')

# reorder factor to represent Figure 2 order of Asutay et al., 2017
searches$sound <- fct_relevel(searches$sound, "firealarm", "growlingdog", "cluckinghen", "microwaveoven")

# plot response time across audiory stimuli
# there are 197 NAs where responses are >3500ms
ggplot(searches, aes(sound, responseTime, colour = salience)) +
  stat_summary(fun.y = mean, geom = "point", size = 2) +
  stat_summary(fun.data = mean_cl_boot, geom = "errorbar", width = 0.1) + 
  facet_grid(salience ~ ., scales = "free") +
  theme_minimal(base_family = 'mono', base_size = 18) +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))

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


# calculate aov for main hypothesis ----

# convert to factors
searches$respondent <- as.factor(searches$respondent)
searches$position <- as.factor(searches$position)
searches$salience <- as.factor(searches$salience)

# Does arousal induced by task-irrelevant auditory stimuli modulate attention in a visual search?
  searches.long <-
  searches %>%
    filter(block == 'VO') %>%
    filter(!is.na(responseTime)) %>%
    select(respondent, trial_nr, salience, position, responseTime)
  
# write_csv(searches.long, '../data/searches.long.csv')
  
# run anova with the excellent ez package (loaded above)
  ezANOVA(data = searches.long,
          dv = responseTime,
          wid = respondent,
          within = .(salience, position),
          type = 3)
  # and show some means
  searches.long %>%
    group_by(salience) %>%
    summarise(av_sal = mean(responseTime),
              sd_sal = sd(responseTime))
  
  searches.long %>%
    group_by(position) %>%
    summarise(av_pos = mean(responseTime),
              sd_pos = sd(responseTime))

  ggplot(searches.long, aes(salience, responseTime, group = position, colour = position )) +
  stat_summary(fun.y = mean, geom = "point") +
    stat_summary(fun.y = mean, geom = "line") +
    stat_summary(fun.data = mean_cl_boot, geom = "errorbar", width = 0.1) + 
    theme_minimal(base_family = 'mono', base_size = 18) 
  
  ggsave('../plots/Interaction_VO.png')
  
  
  # To investigate the in uence of auditory-induced arousal on RTs, 
  # we ordered the stimuli based on individual arousal ratings before submitting the RT data
  # into an ANOVA (S1 to S4, see Fig. 2A and Methods for details). Hence, S1 is the most 
  # arousing stimulus for each participant. Similarly, S4 is the least arousing stimulus for 
  # each participant. RTs were analyzed using ANOVA with auditory-cue (S1 to S4), sound-location 
  # (frontal vs. rear), target-saliency, and target-location as within-subject factors.  
  
  # auditory
  audditory.long <-
    searches %>%
    filter(block == 'VA') %>%
    filter(!is.na(responseTime)) %>%
    select(respondent, trial_nr, salience, position, sound, responseTime)
  
  
  # run anova with the excellent ez package (loaded above)
  ezANOVA(data = auditory.long,
          dv = responseTime,
          wid = respondent,
          within = .(salience, position, sound),
          type = 3)