library(tidyverse)
library(RNetLogo)
nl.path <- "/home/dfoguelman/apps/netlogo-5.2.1/"
nl.jarname <- "NetLogo.jar"
NLStart(nl.path, gui = FALSE)
mito.model = '/home/dfoguelman/proj/crazydevs/pythonpdevs/examples/mito/original_abm_model.nlogo'

mito.model = '/home/dfoguelman/Downloads/modelo.nlogo'

experiments = data.frame()

single_retry_run = function(retry){
  NLLoadModel(mito.model)
  NLCommand("setup")
  NLCommand("set prob_fusion 50")
  NLCommand("set prob_fission 50")
   NLCommand("set freq_fusion 5")
   NLCommand("set freq_fission 5")
  
  #experiment_run = seq(1, 720) %>% map_dfr(time_advance)
  experiment_run = NLDoReport(3600, "go", c("big","mid", 'small'),
             as.data.frame=TRUE,df.col.names=c("big", "mid", 'small'))
  experiment_run$retry = retry
  experiment_run$fission_prob = 0.8
  experiment_run$t = seq(1, 3600)
  experiment_run$duration = 3600
  return(experiment_run)
}

# This will run 20 experiments fror the same parameters.
full_run = seq(20) %>% map_dfr(single_retry_run)

write_csv(full_run, "netlogo_results_fission_50.csv")

# full_run %>% gather(1:3, key='mass_group', value='perc') %>% ggplot(data=., aes(x=t, y=perc)) +
#   stat_summary(aes(y=perc, group=mass_group),
#                inherit.aes = T,
#                fun.data=mean_se,
#                alpha=0.1,
#                geom='crossbar',
#                color="gray") +

# stat_summary(aes(y=perc, color=mass_group),
#              fun.y =mean, fun.args = list(mult=1), geom='line')
