require(tidyverse)
sir = read_csv("~/proj/crazydevs/pythonpdevs/examples/sir/results_graph_tp.csv") %>%
  add_column(Tot=.$S+.$I+.$R) 

sir %>%  filter(t != 'Inf') %>% add_column(tbin=cut_interval(.$t, 20)) %>% 
  gather("type", "amount", 3:5) %>%
  group_by(tbin, type) %>% 
  summarise(sum = sum(amount)) %>%
  add_column(dsum = c(.$sum[1], diff(.$sum))) %>%
  qplot(data=., x=tbin, y=dsum, color=type, facets = . ~ type)

sir %>%  filter(t != 'Inf') %>% 
  gather("type", "amount", 3:5) %>% add_column(tbin=cut_interval(.$t, 20)) %>%
  group_by(tbin, type) %>% mutate(mbin = mean(amount)) %>% 
  ggplot(data=., aes(x=tbin, y=amount, color=type)) + 
  facet_wrap(~ type, nrow=3) + 
  geom_boxplot() +
  stat_summary(fun.y=mean, geom="line", aes(group=1))  + 
  stat_summary(fun.y=mean, geom="point")
  
sir %>%  filter(t != 'Inf') %>% 
  gather("type", "amount", 6:9) %>% add_column(tbin=cut_interval(.$t, 20)) %>%
  group_by(tbin, type) %>% mutate(mbin = mean(amount)) %>% 
  ggplot(data=., aes(x=tbin, y=amount, color=type)) + 
  facet_wrap(~ type, nrow=3) + 
  geom_boxplot() +
  stat_summary(fun.y=mean, geom="line", aes(group=1))  + 
  stat_summary(fun.y=mean, geom="point")

  
sir %>% 
    gather("type", "amount", 3:5) %>%
    qplot(data=., x=t, y=amount, color=type) + 
    stat_summary(fun.y=mean, geom="line", aes(group=1))  + 
    stat_summary(fun.y=mean, geom="point")
  
