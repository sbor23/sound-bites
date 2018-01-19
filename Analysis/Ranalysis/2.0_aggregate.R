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

# remove incorrect trials
  searches.acc <- 
    searches %>%
    filter(accuracy == 1)
  
# arousal and valence
# All reactions to auditory stimuli were scaled between −1 and +1, and 
# entered into an ANOVA with stimulus (4 stimuli) and location (frontal vs. rear) 
# within-subject factors (see Supplemental Table 1 for average ratings). 

  # order stimuli based on arousal level into S1 to S4
  arousal.level <- 
  ratings %>%
    filter(event == 'arousal_rating') %>%
    group_by(respondent) %>%
    arrange(desc(value), .by_group = TRUE)
  # add S1 - S4    
  arousal.level$arousal <- rep(c('S1', 'S2', 'S3', 'S4'), length(unique(arousal.level$respondent)))
  # select relevant variables
  arousal.level.short <- 
  arousal.level %>%
    select(respondent, stim_id, arousal)
  
  # searches VA
  searches.VA <- 
    searches.acc %>%
    filter(block == 'VA')
  
  # searches VO
  searches.VO <- 
    searches.acc %>%
    filter(block == 'VO') %>%
    mutate(arousal = 'visual only')
  
  # merge into searches file
  searches.VA <-  merge(searches.VA, arousal.level.short, by.x = c('respondent', 'sound'), by.y = c('respondent', 'stim_id'))
  # put back together
  searches.arousal <- rbind(searches.VA, searches.VO)
  
# reorder factor to represent Figure 2 order of Asutay et al., 2017
  searches.arousal$sound <- fct_relevel(searches.arousal$arousal, "visual only", "S1", "S2", "S3", "S4")

# plot response time across audiory stimuli
  ggplot(searches.arousal, aes(arousal, responseTime, colour = salience)) +
    stat_summary(fun.y = mean, geom = "point", size = 2) +
    stat_summary(fun.data = mean_cl_boot, geom = "errorbar", width = 0.1) + 
    facet_grid(salience ~ ., scales = "free") +
    theme_minimal(base_family = 'mono', base_size = 18) +
    theme(axis.text.x = element_text(angle = 45, hjust = 1))

  ggsave('../plots/Rep_Figure2B.png')
  
# plot rating across audiory stimuli
  arousal.level.count <- 
  arousal.level %>%
    group_by(arousal, stim_id) %>%
    summarise(count_stim = n())
  
  ggplot(arousal.level.count, aes(x = arousal, y = count_stim, fill = stim_id)) +
    geom_bar(stat = 'identity') + 
    ylab('Number of Subjects') + 
    xlab(NULL) + 
    scale_fill_grey() + 
    theme_minimal(base_family = 'mono', base_size = 18) + 
    theme(legend.title=element_blank())
  
  ggsave('../plots/Rep_Figure2A.png')  

# calculate aov for main hypothesis ----
# Does arousal induced by task-irrelevant auditory stimuli modulate attention in a visual search?
  
# convert to factors
  searches.VO$respondent <- as.factor(searches.VO$respondent)
  searches.VO$position <- as.factor(searches.VO$position)
  searches.VO$salience <- as.factor(searches.VO$salience)
  
  # Does arousal induced by task-irrelevant auditory stimuli modulate attention in a visual search?
  searches.long <-
    searches.arousal %>%
    filter(block == 'VO') %>%
    filter(!is.na(responseTime)) %>%
    select(respondent, trial_nr, salience, position, responseTime)
  
  # run anova with the excellent ez package (loaded above)
  ezANOVA(data = searches.VO,
          dv = responseTime,
          wid = respondent,
          within = .(salience, position),
          type = 3)
  # and show some means
  searches.VO %>%
    group_by(salience) %>%
    summarise(av_sal = mean(responseTime),
              sd_sal = sd(responseTime))
  
  searches.VO %>%
    group_by(position) %>%
    summarise(av_pos = mean(responseTime),
              sd_pos = sd(responseTime))

  ggplot(searches.VO, aes(salience, responseTime, group = position, colour = position )) +
  stat_summary(fun.y = mean, geom = "point") +
    stat_summary(fun.y = mean, geom = "line") +
    stat_summary(fun.data = mean_cl_boot, geom = "errorbar", width = 0.1) + 
    theme_minimal(base_family = 'mono', base_size = 18) 
  
  ggsave('../plots/Interaction_VO.png')
  
  # To investigate the influence of auditory-induced arousal on RTs, 
  # we ordered the stimuli based on individual arousal ratings before submitting the RT data
  # into an ANOVA (S1 to S4, see Fig. 2A and Methods for details). Hence, S1 is the most 
  # arousing stimulus for each participant. Similarly, S4 is the least arousing stimulus for 
  # each participant. RTs were analyzed using ANOVA with auditory-cue (S1 to S4), target-saliency, 
  # and target-location as within-subject factors.  
  
  # switch to mixed model approach  
  library(lme4)
  #install.packages('lmerTest')
  library(lmerTest)
    my_lmer = lmer(responseTime ~ (1|respondent) + arousal * position * salience, data = searches.VA)
    summary(my_lmer)
  
# calculate accuracy for reproducing Table 1 ----
    # per sound/visual / high / low salient target
    searches.table <- 
    searches %>%
      group_by(salience, sound) %>%
      summarise(RT = mean(responseTime, na.rm = TRUE),
                Accuracy = sum(accuracy)/length(accuracy))
    
    ### export searches as csv (without filtering accuracy)
    write.table(searches, file = "../data/searches.csv",
                sep = ';', dec = '.', row.names = FALSE, col.names = TRUE, quote = FALSE)
    ### export searches (with filtering accuracy)
    searches.export <- 
    searches.arousal %>%
      group_by(respondent, block, trial_nr, sound, salience, arousal) %>%
      summarise(responseTime = mean(responseTime))
    
    write.table(searches.export, file = "../data/searches_clean.csv",
                sep = ';', dec = '.', row.names = FALSE, col.names = TRUE, quote = FALSE)
    