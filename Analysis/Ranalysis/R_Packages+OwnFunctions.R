# check for installed packages and load if necessary

is.installed <- function(mypkg) is.element(mypkg, installed.packages()[,1])

check_packages <- c(#'afex',
                    #'broome',
                    #'combinat',
                    #'car',
                    #'plyr',
                    'dplyr',
                    #'dataframes2xls',
                    #'ez',
                    #'gdata',
                    'ggplot2',
                    #'ggmap',
                    #'lme4',
                    #'magrittr'
                    #'mapproj',
                    #'Matrix',
                    #'multcomp',
                    #'pbkrtest',
                    #'pwr',
                    #'psych',
                    #'QuantPsyc',
                    #'RecordLinkage',
                    #'reshape',
                    #'robust',
                    #'tseries',
                    #'gridExtra',
                    #'grid',
                    'stringr',
                    'tidyr'
                    #'mousetrack'
                    )
number_packages <- length(check_packages)

for(i in 1:number_packages) {
  if (is.installed(check_packages[i])) {
          print(check_packages[i])
          library(check_packages[i], character.only=TRUE)
  } else {
          install.packages(check_packages[i])
  }
}


theme_presentation <- function (base_size = 26, base_family = "")
        {
  theme_bw(base_size = base_size, base_family = base_family) %+replace%
  theme(#axis.text = element_text(size = rel(0.8)),
        axis.ticks = element_line(colour = "black"),
        legend.key = element_rect(colour = "grey80"),
        panel.background = element_rect(fill = "white", colour = NA),
        panel.border = element_rect(fill = NA, colour = "grey50"),
        panel.grid.major = element_blank(),
        panel.grid.minor = element_blank(),
        strip.background = element_rect(fill = "grey80", colour = "grey50"),
        strip.background = element_rect(fill = "grey80", colour = "grey50")
        #axis.title.y = element_text(vjust=-0.1)
        )
  }


presentation.ggsave <- function(filename = default_name(plot), height= 11, width= 16, dpi= 96, ...) {
  ggsave(filename=filename, height=height, width=width, dpi=dpi, ...)
}

## Summarizes data.
## Gives count, mean, standard deviation, standard error of the mean, and confidence interval (default 95%).
##   data: a data frame.
##   measurevar: the name of a column that contains the variable to be summariezed
##   groupvars: a vector containing names of columns that contain grouping variables
##   na.rm: a boolean that indicates whether to ignore NA's
##   conf.interval: the percent range of the confidence interval (default is 95%)
summarySE <- function(data=NULL, measurevar, groupvars=NULL, na.rm=FALSE, conf.interval=.95, .drop=TRUE) {
  require(plyr)

# New version of length which can handle NA's: if na.rm==T, don't count them
  length2 <- function (x, na.rm=FALSE) {
    if (na.rm) sum(!is.na(x))
    else       length(x)
  }

  # This does the summary; it's not easy to understand...
  datac <- ddply(data, groupvars, .drop=.drop,
                 .fun= function(xx, col, na.rm) {
                   c( N        = length2(xx[,col], na.rm=na.rm),
                      mean     = mean   (xx[,col], na.rm=na.rm),
                      median   = median (xx[,col], na.rm=na.rm),
                      sd       = sd     (xx[,col], na.rm=na.rm)
                      )
                 },
                 measurevar,
                 na.rm
                 )

  # Rename the "mean" column
  datac <- rename(datac, c("mean"=measurevar))

  datac$se <- datac$sd / sqrt(datac$N)  # Calculate standard error of the mean

  # Confidence interval multiplier for standard error
  # Calculate t-statistic for confidence interval:
  # e.g., if conf.interval is .95, use .975 (above/below), and use df=N-1
  ciMult <- qt(conf.interval/2 + .5, datac$N-1)
  datac$ci <- datac$se * ciMult

  return(datac)
}


# merge function
multiple_merge <- function(indflist,joinvar="VPN",...){
  if(!all(sapply(indflist,function(inv){joinvar%in%names(inv)}))){
    stop("Join Variable is missing in one of the dataframes. \n Check Again")
  }
  rdf <- indflist[[1]]
  for(i in 2:length(indflist)){
    rdf <- merge(rdf,indflist[[i]],by=joinvar,...)
  }
  return(rdf)
}


# remove variables
remove(i, number_packages, check_packages, is.installed )

# add facet labels to ggplot2
# must come in form:
#label_names <- list(
#  '1'="Game 1",
#  '2'="Game 2")

function_labeller <- function(variable,value){
  return(label_names[value])
}

binIntervals <- function(nrOfBins,binSize,offset=1) {
  list <- list()
  for(i in 1:nrOfBins){
    list <- append(list,list(seq(offset+(i-1)*binSize,i*binSize+(offset-1))))
  }
  return(list)
}
