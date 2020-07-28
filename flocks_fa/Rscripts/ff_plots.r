require(tidyverse)

events = read_csv('/home/dfoguelman/proj/crazydevs/pythonpdevs/examples/mito/experiment_events_12_retries_5_duration_dplus1.csv',
                  col_names = c('currenttime', 'fissionprob', 'retry', 'duration', 'requestedstate', 'count'))


# This will run 20 experiments fror the same parameters.
netlogo_events = read_csv("/home/dfoguelman/proj/crazydevs/results/netlogo_results_fuse_model.csv") %>% 
  rename(fissionprob=fission_prob)

nlogo_runs = netlogo_events %>% 
  rename(Fusionated=fusion_event, Fissionated=fission_event) %>% transform(t=t-1) %>% 
  select(Fusionated, Fissionated, retry, fissionprob, t, duration) %>%   add_column(model='Netlogo') %>%

  gather(1:2, key='requestedstate', value='count') %>% filter(t %% 300 ==0 & t > 0) 

ff_events = events %>% filter(requestedstate != 'None') %>% 
  rename(count=`count`, t=currenttime) %>% add_column(model='ebdevs') %>%
  rbind(nlogo_runs)

ff_events %>% ggplot(data=.,
                     aes(x=(t), y=count, fill=model)) +
  geom_col(position = 'dodge2') +
  facet_wrap(fissionprob ~ requestedstate, ncol=2) +
  scale_x_continuous(breaks = pretty_breaks(10)) + ggtitle("Fission probabilty per amount of fusion / fission events")

ff_events %>% ggplot(data=.,
                     aes(x=as.factor(t), y=count, fill=model)) +
  geom_boxplot(position = 'dodge2') +
  facet_wrap(fissionprob ~ requestedstate, ncol=2)

  